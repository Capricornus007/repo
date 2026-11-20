#!/usr/bin/env bash
# WorkBuddy 國際版自動更新（由 .github/workflows/workbuddy-update.yml 呼叫）。
#
# 流程：官方更新 API → 比對 in-tree PKGBUILD → 有新版就下載官方產物、
# 驗證 sha256 → 從產物抽出 Electron 版本 → 更新 PKGBUILD/.SRCINFO →
# 推送父倉與獨立倉（CI 構建來源）→ 觸發單包構建。
#
# 安全邊界（同 aur-update.yml 的思路）：只讀 API、下載官方產物、算雜湊、
# 改文字，不執行任何上游代碼（不跑 makepkg build）。產物必須通過官方
# API 公布的 sha256 才寫入 PKGBUILD。
#
# 本地也能跑：DRY_RUN=true bash scripts/workbuddy-update.sh（只檢查、產 diff，不推）。
set -euo pipefail

API='https://www.workbuddy.ai/v2/update?platform=workbuddy-darwin-x64'
COS='https://codebuddy-1328495429.cos.accelerate.myqcloud.com/workbuddy/saas/darwin-x64'
OWNER='Capricornus007'
STANDALONE='workbuddy-international-bin'
MAIN_REPO='repo'
PKGDIR='workbuddy-international-bin'
DRY_RUN="${DRY_RUN:-false}"
BUILD_TOKEN="${BUILD_TOKEN:-}"

log() { printf '[workbuddy-update] %s\n' "$*"; }
die() { printf '[workbuddy-update] ERROR: %s\n' "$*" >&2; exit 1; }

[[ -f "$PKGDIR/PKGBUILD" ]] || die "找不到 $PKGDIR/PKGBUILD（請從倉庫根目錄執行）"

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

log "查詢官方更新 API"
curl -fsSL --retry 3 --retry-all-errors --max-time 60 "$API" -o "$work/api.json" \
    || die "無法連線更新 API"

# 解析 API 並與現行 PKGBUILD 比對，結果寫進 vars.sh。
python3 - "$work" "$PKGDIR/PKGBUILD" <<'PYEOF'
import json, re, sys
work, pkgpath = sys.argv[1], sys.argv[2]
api = json.load(open(f'{work}/api.json'))
ver, sha, url = api['version'], api['sha256hash'], api['url']
# 這些值會寫進 vars.sh 被 source、並寫進 PKGBUILD——先驗格式，杜绝注入。
if not re.fullmatch(r'[0-9]+(?:\.[0-9]+)*', ver):
    sys.exit(f'API version format unexpected: {ver!r}')
if not re.fullmatch(r'[0-9a-fA-F]+', sha):
    sys.exit(f'API sha256 format unexpected: {sha!r}')
if not re.fullmatch(r'https://[A-Za-z0-9./_-]+', url):
    sys.exit(f'API url format unexpected: {url!r}')
m = re.search(r'WorkBuddy-darwin-x64-.+-([0-9a-fA-F]+)\.(?:zip|dmg)$', url)
if not m:
    sys.exit(f'cannot parse build hash from API url: {url}')
build = m.group(1)
pkg = open(pkgpath).read()
def grab(pat):
    m = re.search(pat, pkg, re.M)
    if not m:
        sys.exit(f'PKGBUILD missing {pat}')
    return m.group(1)
cur_ver = grab(r'^_pkgver=(\S+)$')
cur_build = grab(r'^_build=(\S+)$')
cur_el = grab(r'^_electronver=(\S+)$')
cur_el_sha = grab(r"sha256sums=\('[0-9a-f]+'\n\s+'([0-9a-f]+)'")
vt = lambda v: tuple(int(x) for x in v.split('.'))
skip = vt(ver) < vt(cur_ver) or (vt(ver) == vt(cur_ver) and build == cur_build)
with open(f'{work}/vars.sh', 'w') as f:
    for k, v in dict(NEW_VER=ver, NEW_BUILD=build, API_SHA=sha, API_URL=url,
                     CUR_VER=cur_ver, CUR_BUILD=cur_build, CUR_ELECTRON=cur_el,
                     CUR_ELECTRON_SHA=cur_el_sha, SKIP=int(skip)).items():
        f.write(f"{k}='{v}'\n")
print(f'[workbuddy-update] upstream {ver}-{build} / current {cur_ver}-{cur_build} / electron {cur_el}')
PYEOF
# shellcheck disable=SC1091
source "$work/vars.sh"

if [[ "$SKIP" == 1 ]]; then
    log "已是最新（${CUR_VER}-${CUR_BUILD}），不做任何事"
    exit 0
fi
log "發現新版：${CUR_VER}-${CUR_BUILD} -> ${NEW_VER}-${NEW_BUILD}"

if [[ "$DRY_RUN" != true && -z "$BUILD_TOKEN" ]]; then
    die "PERSONAL_BUILD_TOKEN 為空，無法推送獨立倉"
fi

# 下載官方產物：優先 COS 鏡像 DMG（與現行 PKGBUILD 來源一致），
#  unavailable 或雜湊不符時退回 API 的 zip。兩者都必須通過官方 sha256。
dmg_name="WorkBuddy-darwin-x64-${NEW_VER}-${NEW_BUILD}.dmg"
artifact="$work/$dmg_name"
src_name="$dmg_name"
src_url="$COS/$dmg_name"
if curl -fsSL --retry 3 --max-time 1200 "$src_url" -o "$artifact" \
   && [[ "$(sha256sum "$artifact" | cut -d' ' -f1)" == "$API_SHA" ]]; then
    log "COS DMG 下載完成，sha256 與官方 API 一致"
else
    log "COS DMG 不可用或雜湊不符，退回 API zip"
    artifact="$work/artifact.zip"
    src_url="$API_URL"
    src_name="$(basename "$API_URL")"
    curl -fsSL --retry 3 --max-time 1200 "$src_url" -o "$artifact" || die "無法下載官方產物"
    [[ "$(sha256sum "$artifact" | cut -d' ' -f1)" == "$API_SHA" ]] \
        || die "官方產物 sha256 與 API 公布不符（供應鏈檢查失敗）"
    log "API zip 下載完成，sha256 與官方 API 一致"
fi
ARTIFACT_SHA="$API_SHA"

# 從產物抽出捆绑的 Electron 版本（與 lib-dmg.sh detect_electron_version 同法）。
mkdir -p "$work/extract"
7z x -o"$work/extract" "$artifact" -y >/dev/null || die "無法解開產物"
plist="$(find "$work/extract" -maxdepth 12 -path '*Electron Framework.framework/Versions/A/Resources/Info.plist' -type f | head -1)"
[[ -n "$plist" ]] || die "產物內找不到 Electron Framework Info.plist"
NEW_ELECTRON="$(python3 -c 'import plistlib,sys; print(plistlib.load(open(sys.argv[1],"rb"))["CFBundleVersion"])' "$plist")"
rm -rf "$work/extract"
[[ "$NEW_ELECTRON" =~ ^[0-9]+(\.[0-9]+)*$ ]] || die "plist 裡的 Electron 版本格式異常：$NEW_ELECTRON"
log "產物捆绑 Electron：$NEW_ELECTRON（現行 $CUR_ELECTRON）"

ELECTRON_SHA="$CUR_ELECTRON_SHA"
if [[ "$NEW_ELECTRON" != "$CUR_ELECTRON" ]]; then
    ez="electron-v${NEW_ELECTRON}-linux-x64.zip"
    curl -fsSL --retry 3 --max-time 600 \
        "https://github.com/electron/electron/releases/download/v${NEW_ELECTRON}/${ez}" \
        -o "$work/$ez" || die "無法下載 Electron $NEW_ELECTRON Linux zip"
    ELECTRON_SHA="$(sha256sum "$work/$ez" | cut -d' ' -f1)"
    log "Electron zip sha256：$ELECTRON_SHA"
fi

# 更新 PKGBUILD（逐行置換；electron 那行 source 用 ${_electronver} 變數，自動跟著動）。
python3 - "$PKGDIR/PKGBUILD" "$NEW_VER" "$NEW_BUILD" "$NEW_ELECTRON" "$ARTIFACT_SHA" "$ELECTRON_SHA" "$src_name" "$src_url" <<'PYEOF'
import sys
path, ver, build, el, asha, esha, sname, surl = sys.argv[1:9]
lines = open(path).read().splitlines(keepends=True)
out, in_sums = [], False
for ln in lines:
    if ln.startswith('_pkgver='):
        ln = f'_pkgver={ver}\n'
    elif ln.startswith('_build='):
        ln = f'_build={build}\n'
    elif ln.startswith('_electronver='):
        ln = f'_electronver={el}\n'
    elif ln.startswith('_dmg=') and not sname.endswith('.dmg'):
        ln = f'_dmg="{sname}"\n'
    elif ln.startswith('pkgrel='):
        out.append(f'# pkgrel 1: upstream {ver}-{build} (workbuddy-update.yml auto-bump)\n')
        ln = 'pkgrel=1\n'
    elif ln.startswith('source=('):
        ln = f'source=("{sname}::{surl}"\n'
    elif ln.startswith('sha256sums=('):
        ln = f"sha256sums=('{asha}'\n"
        in_sums = True
    elif in_sums:
        indent = ln[:len(ln) - len(ln.lstrip())]
        ln = f"{indent}'{esha}'\n"
        in_sums = False
    out.append(ln)
open(path, 'w').write(''.join(out))
PYEOF

bash -n "$PKGDIR/PKGBUILD" || die "更新後 PKGBUILD 語法錯誤"
( cd "$PKGDIR" && makepkg --printsrcinfo > .SRCINFO ) || die "無法產生 .SRCINFO"
log "PKGBUILD/.SRCINFO 已更新"

if [[ "$DRY_RUN" == true ]]; then
    log "DRY_RUN：以下為 diff，不推送"
    git diff -- "$PKGDIR/PKGBUILD" "$PKGDIR/.SRCINFO" 2>/dev/null || true
    exit 0
fi

git config --global user.name 'github-actions[bot]'
git config --global user.email '41898282+github-actions[bot]@users.noreply.github.com'
msg="workbuddy-international-bin: upstream ${NEW_VER}-${NEW_BUILD} (auto-update)"

# 1) 父倉（鏡像；checkout 的 origin 已帶 GITHUB_TOKEN）。
git add "$PKGDIR/PKGBUILD" "$PKGDIR/.SRCINFO"
git commit -m "$msg"
git push origin HEAD:master
log "父倉已推送"

# 2) 獨立倉（CI 通用分支 clone 的構建來源）。
git clone --depth 1 "https://x-access-token:${BUILD_TOKEN}@github.com/${OWNER}/${STANDALONE}.git" "$work/standalone"
cp "$PKGDIR/PKGBUILD" "$PKGDIR/.SRCINFO" "$work/standalone/"
git -C "$work/standalone" add PKGBUILD .SRCINFO
git -C "$work/standalone" commit -m "$msg"
git -C "$work/standalone" push origin HEAD:master
log "獨立倉已推送"

# 3) 觸發單包構建（盡力而為：失敗就等 build-packages 排程接手）。
payload='{"ref":"master","inputs":{"packages":"[{\"key\":\"workbuddy-international-bin\",\"repo_name\":\"workbuddy-international-bin\",\"variant\":\"none\"}]"}}'
if curl -fsS -X POST \
     -H "Authorization: Bearer ${BUILD_TOKEN}" \
     -H 'Accept: application/vnd.github+json' \
     "https://api.github.com/repos/${OWNER}/${MAIN_REPO}/actions/workflows/build-one-package.yml/dispatches" \
     -d "$payload"; then
    log "已觸發 build-one-package"
else
    log "WARN：觸發 build-one-package 失敗，build-packages 排程稍後會接手"
fi
log "完成：${NEW_VER}-${NEW_BUILD}"