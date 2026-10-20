#!/usr/bin/env python3
"""AUR 回推引擎：算出版號／內容級更新，重算 sums，產 .SRCINFO，可選擇推上 AUR。

只在 aur-update.yml 這個**獨立**工作流裡跑。它跟 build-packages.yml 的差別是重點：
build 那條會 clone 上游 PKGBUILD 並實際執行 prepare()/build()（任意代碼），
這條只讀 PKGBUILD、抓上游 tarball 算雜湊（updpkgsums 下載但不執行 build()），
所以 AUR 寫入金鑰跟「跑來路不明代碼」不會出現在同一個 job 裡。

設計上寧可漏推也不能亂推：任何一步算不出可信結果就整包跳過並印原因，
不猜、不寫半個版本號進去。
"""
import argparse, json, os, re, shlex, subprocess, sys, tempfile
import urllib.parse, urllib.request

AUR_HTTPS = "https://aur.archlinux.org/{base}.git"
AUR_SSH = "ssh://aur@aur.archlinux.org/{base}.git"
NV_LISTING = "https://download.nvidia.com/XFree86/Linux-x86_64/"

# 內容級規則：某些包的 PKGBUILD 裡有寫死的上游版本，光跑 pkgver() 抓不到。
# linux-cachyos-cjktty:211 的 _nv_ver 就是這種——它同時決定 source URL 與 sums，
# 而且預設空轉（:118 `_build_nvidia_open:=no`），所以落後時不會報錯、只會過期。
CONTENT_RULES = {
    "linux-cachyos-cjktty": [
        {"var": "_nv_ver", "resolver": "nvidia_newest"},
    ],
    # flutter-beta 的 pkgver 是靜態的，而且 URL 與 sums 都綁在它身上。
    # 官方 manifest 直接給 sha256，所以不必下載 tarball 就能把兩樣都更新對。
    "flutter-beta": [
        {"kind": "flutter", "channel": "beta"},
    ],
    # linux-cjktty 跟的是 Arch 的 core/linux（見 resolve_arch_pkg 的說明）。
    # 跨大版會被上面那道补丁路徑守門擋下來，所以這裡只吃同次版本內的跟進。
    "linux-cjktty": [
        {"kind": "arch_pkg", "pkg": "linux", "repo": "core"},
    ],
}


def run(cmd, cwd=None):
    return subprocess.run(cmd, shell=isinstance(cmd, str), cwd=cwd,
                          capture_output=True, text=True)


def verkey(v):
    return [int(x) if x.isdigit() else x for x in re.split(r'[._-]', str(v))]


def is_newer(new, old):
    """用 pacman 自己的 vercmp 判，不自己寫演算法。

    各包的 pkgver() 格式**本來就不統一**，而且不該統一：實測同一輪裡就有
    xcb-imdkit-git 的 `1.0.9.r1.g621048b`、gnome-keyring-git 的 `51.0+8+ge9706199`、
    fzf-git 的 `v0.74.5.r2.g55c122f1` 三種寫法（.r 與 + 混用）。vercmp 全部認得，
    自己拆字串比反而會錯。
    拿不到 vercmp 時退回簡化比對，並在註記裡說明是退回路徑。
    """
    if new == old:
        return False
    r = run(['vercmp', str(new), str(old)])
    if r.returncode == 0 and r.stdout.strip() in ('-1', '0', '1'):
        return r.stdout.strip() == '1'
    try:
        return verkey(new) > verkey(old)
    except TypeError:
        return True


def resolve_nvidia_newest():
    """NVIDIA 官方目錄列表取最大版號。

    絕對不要用 download.nvidia.com/XFree86/Linux-x86_64/latest.txt：
    實測它回 595.104.02（生產分支），拿它會把 PKGBUILD 裡的 610.57.04 降成 595。
    """
    try:
        html = urllib.request.urlopen(NV_LISTING, timeout=30).read().decode('utf-8', 'replace')
    except Exception as e:
        return None, f'抓 {NV_LISTING} 失敗: {e}'
    # 列表是目錄項 <a href='615.78.08/'>，不是檔名。實測用
    # NVIDIA-Linux-x86_64-<ver> 去配會全盤配不中（回 0 個候選）。
    vs = sorted(set(re.findall(r'>\s*(\d+\.\d+(?:\.\d+)?)/<', html)), key=verkey)
    if not vs:
        return None, '列表裡找不到任何 NVIDIA 版號'
    return vs[-1], f'列表最新 {vs[-1]}（候選末三個 {vs[-3:]}）'


FLUTTER_RELEASES = "https://storage.googleapis.com/flutter_infra_release/releases/releases_linux.json"


def resolve_flutter(channel):
    """Flutter 官方 release manifest：同時給 version 與 sha256。

    有 sha256 就不用為了算 sums 去下載 200MB tarball。實測該 JSON 的
    current_release 有 beta/dev/stable 三個鍵，releases[] 每條都帶 sha256。
    PKGBUILD 的 pkgver 用底線（`3.48.0_0.2.pre`），URL 裡再 ${pkgver/_/-} 換回連字號，
    所以這裡要主動把 '-' 換成 '_'，否則寫進去的是非法 pkgver。
    """
    try:
        d = json.loads(urllib.request.urlopen(FLUTTER_RELEASES, timeout=30).read().decode())
    except Exception as e:
        return None, f'抓 Flutter manifest 失敗: {e}'
    # current_release[channel] 是 **commit hash**，不是版本字串（實測 beta =
    # 07502c7de3806b668e2fb57e3eaf412d833b1726），所以要拿它去 releases[] 比 hash。
    want = d.get('current_release', {}).get(channel)
    if not want:
        return None, f'manifest 裡沒有 current_release.{channel}'
    for r in d.get('releases', []):
        if r.get('channel') == channel and r.get('hash') == want:
            ver = str(r['version']).replace('-', '_')
            sha = r.get('sha256')
            if not re.fullmatch(r'[0-9a-fA-F]{64}', sha or ''):
                return None, f'{channel} {ver} 的 manifest sha256 不可信: {sha!r}'
            return (ver, sha.lower()), f'{channel} 最新 {ver}'
    return None, f'manifest 的 releases[] 找不到 hash={want} 的 {channel} 條目'


def resolve_arch_pkg(pkg, repo=None):
    """Arch 官方倉庫的現行版號。

    linux-cjktty 的源碼 URL 是直接從 pkgver 拼的
    （`v${pkgver%%.*}.x/linux-<pkgver>.tar.xz` 與
      `gitlab…/linux/-/raw/${pkgver}-${pkgrel}/config.x86_64`），
    所以它的真值是 Arch 那顆 `core/linux`，不是 kernel.org 的 mainline——
    抓 kernel.org 會拿到沒有 .archN 後綴的版本，config 那條 URL 直接 404。
    """
    url = f"https://archlinux.org/packages/search/json/?name={urllib.parse.quote(pkg)}"
    try:
        d = json.loads(urllib.request.urlopen(url, timeout=30).read().decode())
    except Exception as e:
        return None, f'查 Arch 倉庫失敗: {e}'
    # 欄位名是 `repo` 不是 `repository`（實測後者回 None，害我把唯一的 linux 過濾掉）。
    hits = [p for p in d.get('results', []) if not repo or p.get('repo') == repo]
    if not hits:
        return None, f'Arch 倉庫查無 {pkg}' + (f'（repo={repo}）' if repo else '')
    p = hits[0]
    return (p['pkgver'], p['pkgrel'], p.get('repo')), f"{p.get('repo')}/{pkg} = {p['pkgver']}-{p['pkgrel']}"


RESOLVERS = {"nvidia_newest": resolve_nvidia_newest}


def source_entries(adir):
    """用 bash 展開 source=()，跟 makepkg 同一做法。

    正則替換變數是錯的：PKGBUILD 常寫 git+$_urlbase/$_pkgname，
    只有真的讓 bash 展開才不會漏（實測 fcitx5-rime-git 就因此 clone 到 "$url.git"）。
    """
    r = run(['bash', '-c',
             f'cd {shlex.quote(adir)} && . ./PKGBUILD >/dev/null 2>&1; '
             f'printf "%s\\n" "${{source[@]}}"'])
    return [l.strip() for l in r.stdout.splitlines() if l.strip()]


def git_sources(entries):
    """解析 source 條目裡的 git 源，支援兩種寫法：
        git+https://host/path/repo.git[#branch=x][&module=y]
        <目錄名>::git+https://host/path/repo      ← xfce 系常用，實測 garcon-git /
                                                   xfce4-volumed-pulse-git 就是這型，
                                                   舊版只認 'git+' 開頭會整批漏掉。
    pkgver() 通常 cd 進那個 <目錄名>，所以目錄名必須照它來，不能自己推。
    """
    out = []
    for e in entries:
        rest = e
        prefix = None
        if '::' in rest:
            prefix, _, rest = rest.partition('::')
        if not rest.startswith('git+'):
            continue
        spec = rest[4:]
        url, _, frag = spec.partition('#')
        module = branch = None
        for kv in frag.split('&'):
            if kv.startswith('module='):
                module = kv[7:]
            elif kv.startswith('branch='):
                branch = kv[7:]
        if prefix:
            name = prefix
        elif module:
            name = module
        else:
            name = os.path.basename(url.rstrip('/'))
        if name.endswith('.git'):
            name = name[:-4]
        out.append((url, name, branch))
    return out


def has_pkgver_func(pb):
    return re.search(r'^\s*pkgver\(\)\s*\{', pb, re.M) is not None


def compute(adir, cache):
    """回傳 (edits, note)。edits 是 [(regex, repl, 說明)]，空代表不動。"""
    pb = open(os.path.join(adir, 'PKGBUILD')).read()
    m = re.search(r'^pkgver=(.*)$', pb, re.M)
    if not m:
        return [], 'PKGBUILD 沒有 pkgver='
    old_ver = m.group(1).strip().strip('"\'')
    mr = re.search(r'^pkgrel=(.*)$', pb, re.M)
    old_rel = mr.group(1).strip() if mr else '1'
    edits, notes = [], []

    if has_pkgver_func(pb):
        gs = git_sources(source_entries(adir))
        if not gs:
            notes.append('有 pkgver() 但找不到 git+ 源 → 跳過')
        else:
            srcdir = os.path.join(cache, 'src')
            os.makedirs(srcdir, exist_ok=True)
            ok = True
            for url, name, branch in gs:
                d = os.path.join(srcdir, name)
                if not os.path.isdir(os.path.join(d, '.git')):
                    run(['rm', '-rf', d])
                    # 只要 refs 與 commit（describe / rev-list / tag 列舉），永遠不需要檔案內容。
                    # 實測 flutter-git 完整 clone 吃到 326MB 還沒抓完，blobless 同一倉 138MB，
                    # CI 裡這條會變成 26 包矩陣的瓶頸，所以一律 --filter=blob:none。
                    r = run(['git', 'clone', '-q', '--filter=blob:none', url, d])
                    if r.returncode:
                        # 老 git / 不支援 partial clone 的伺服器：退回完整 clone。
                        run(['rm', '-rf', d])
                        r = run(['git', 'clone', '-q', url, d])
                        if r.returncode:
                            ok = False; notes.append(f'clone 失敗 {url}'); break
                else:
                    run(['git', '-C', d, 'fetch', '-q', '--tags', '--force', 'origin'])
                ref = f'origin/{branch}' if branch else '@{u}'
                run(['git', '-C', d, 'checkout', '-q', '-B', 'bump', ref])
            if ok:
                script = (f'cd {shlex.quote(srcdir)} && '
                          f'export srcdir={shlex.quote(srcdir)} '
                          f'pkgdir={shlex.quote(cache)}/pkg '
                          f'startdir={shlex.quote(adir)} && '
                          f'. {shlex.quote(os.path.join(adir, "PKGBUILD"))} >/dev/null 2>&1; pkgver')
                r = run(['bash', '-c', script])
                cand = r.stdout.strip().splitlines()[-1].strip() if r.stdout.strip() else ''
                if r.returncode or not cand or ' ' in cand:
                    notes.append(f'pkgver() 輸出不可信（{cand!r} rc={r.returncode}）')
                elif not is_newer(cand, old_ver):
                    notes.append(f'pkgver() 算出 {cand}，不比現值 {old_ver} 新 → 不推（防降級）')
                else:
                    edits.append((r'^pkgver=.*$', f'pkgver={cand}', f'pkgver {old_ver}->{cand}'))
                    edits.append((r'^pkgrel=.*$', 'pkgrel=1', 'pkgrel 歸 1'))
                    notes.append(f'{old_ver} -> {cand}')
    else:
        # 別寫成「無 pkgver()」就完事——靜態版號當然是版號，只是要另一種解析來源。
        if CONTENT_RULES.get(os.path.basename(adir)):
            notes.append('靜態版號型，改走內容規則')
        else:
            notes.append(f'靜態版號型（現值 {old_ver}），且 CONTENT_RULES 裡沒有它的解析規則'
                         f'——要自動跟版得先加一條')

    for rule in CONTENT_RULES.get(os.path.basename(adir), []):
        if rule.get('kind') == 'arch_pkg':
            got, why = resolve_arch_pkg(rule['pkg'], rule.get('repo'))
            if not got:
                notes.append(f'arch_pkg 規則放棄：{why}')
                continue
            aver, arel, _ = got
            cur = re.search(r'^pkgver=(\S+)', pb, re.M)
            curl_ = re.search(r'^pkgrel=(\S+)', pb, re.M)
            if not cur or not curl_:
                notes.append('arch_pkg 規則：PKGBUILD 缺 pkgver=/pkgrel=，放棄')
                continue
            if not is_newer(aver, cur.group(1).strip('"\'')):
                notes.append(f'arch_pkg：{why}，現值 {cur.group(1)} 不比它舊 → 不推')
                continue
            # ⚠️ linux-cjktty 的 PKGBUILD 把 cjktty 补丁档名寫死成
            #    `$_cjktty_repo/raw/master/v7.x/cjktty-7.2-rc7.patch`。跨大版
            #    （7.x → 8.x，或 7.2 → 7.3）時那個路徑一定不存在，自動跟版會推出一個
            #    構不起來的包。所以跨大版一律停下來等人，不猜补丁名。
            new_maj = str(aver).split('.')[:2]
            old_maj = str(cur.group(1).strip('"\'')).split('.')[:2]
            if new_maj[:1] != old_maj[:1]:
                notes.append(f'arch_pkg 算出 {aver}，但跨大版（{old_maj[0]}→{new_maj[0]}）'
                             f'会让写死的 cjktty 补丁路径失效 → 交给人处理')
                continue
            if new_maj != old_maj:
                notes.append(f'arch_pkg 算出 {aver}，次版本变了（{cur.group(1)}）——'
                             f'补丁档名可能也要换，先不推')
                continue
            edits.append((r'^pkgver=.*$', f'pkgver={aver}', f'pkgver {cur.group(1)}->{aver}'))
            # config.x86_64 那條 URL 是 ${pkgver}-${pkgrel}，pkgrel 不同步就會 404。
            edits.append((r'^pkgrel=.*$', f'pkgrel={arel}', f'pkgrel {curl_.group(1)}->{arel}（跟 Arch 同步，URL 要用）'))
            notes.append(f'arch_pkg: {cur.group(1)} -> {aver}（{why}）')
            continue

        if rule.get('kind') == 'flutter':
            got, why = resolve_flutter(rule['channel'])
            if not got:
                notes.append(f'flutter 規則放棄：{why}')
                continue
            ver, sha = got
            cur = re.search(r'^pkgver=(\S+)', pb, re.M)
            if not cur:
                notes.append('flutter 規則：PKGBUILD 沒有 pkgver=，放棄')
                continue
            if not is_newer(ver, cur.group(1).strip('"\'')):
                notes.append(f'flutter：算出 {ver}，不比現值 {cur.group(1)} 新 → 不推')
                continue
            edits.append((r'^pkgver=.*$', f'pkgver={ver}', f'pkgver {cur.group(1)}->{ver}'))
            # 只換第一顆（tarball 那顆）；後面 .sh/.csh 是倉內附檔，不該動。
            edits.append((r"^(sha256sums=\(')[0-9a-fA-F]{64}(')", rf'\g<1>{sha}\g<2>',
                          'tarball sha256 取自官方 manifest'))
            if not re.search(r"^pkgrel=", pb, re.M):
                notes.append('警告：找不到 pkgrel=，無法歸 1')
            else:
                edits.append((r'^pkgrel=.*$', 'pkgrel=1', 'pkgrel 歸 1'))
            notes.append(f'flutter {rule["channel"]}: {cur.group(1)} -> {ver}（{why}，sums 一併更新）')
            continue

        got, why = RESOLVERS[rule['resolver']]()
        if not got:
            notes.append(f'內容規則 {rule["var"]} 放棄：{why}')
            continue
        cur = re.search(rf'^{re.escape(rule["var"])}=(\S+)', pb, re.M)
        if not cur:
            notes.append(f'內容規則 {rule["var"]} 在 PKGBUILD 裡找不到，放棄（寫法變了？）')
            continue
        if not is_newer(got, cur.group(1).strip('"\'')):
            notes.append(f'{rule["var"]} 現值 {cur.group(1)} 不比 {got} 舊，不動')
            continue
        edits.append((rf'^{re.escape(rule["var"])}=.*$', f'{rule["var"]}={got}',
                      f'{rule["var"]} {cur.group(1)}->{got}'))
        if not any('pkgver' in d for _, _, d in edits):
            new_rel = str(int(re.match(r'(\d+)', old_rel).group(1)) + 1)
            edits.append((r'^pkgrel=.*$', f'pkgrel={new_rel}', f'pkgrel {old_rel}->{new_rel}'))
        notes.append(f'{rule["var"]}: {cur.group(1)} -> {got}（{why}）')

    return edits, '；'.join(notes)


def apply_bump(adir, edits, msg, push, do_sums):
    pbf = os.path.join(adir, 'PKGBUILD')
    txt = open(pbf).read()
    applied = []
    for pat, repl, why in edits:
        new, n = re.subn(pat, repl, txt, count=1, flags=re.M)
        if n != 1:
            return f'規則沒命中（{why}），中止不推'
        txt = new
        applied.append(why)
    open(pbf, 'w').write(txt)

    if do_sums:
        r = run(['updpkgsums'], cwd=adir)
        if r.returncode:
            return f'updpkgsums 失敗: {r.stderr.strip()[:200]}'
    r = run(['makepkg', '--printsrcinfo'], cwd=adir)
    if r.returncode:
        return f'.SRCINFO 產生失敗: {r.stderr.strip()[:200]}'
    open(os.path.join(adir, '.SRCINFO'), 'w').write(r.stdout)

    run(['git', '-C', adir, 'add', '-A'])
    if run(['git', '-C', adir, 'diff', '--cached', '--quiet']).returncode != 0:
        run(['git', '-C', adir, 'commit', '-m', msg])
    else:
        return '寫入後與原檔相同（無實際差異），不推'
    if not push:
        return 'DRY-RUN 已 commit，未 push'
    # clone 走 HTTPS（免互動、不用 host key），但 AUR **只收 SSH push**，
    # 所以真推之前要把 origin 換掉。
    base = os.path.basename(adir)
    run(['git', '-C', adir, 'remote', 'set-url', 'origin', AUR_SSH.format(base=base)])
    rp = run(['git', '-C', adir, 'push', 'origin', 'HEAD:master'])
    return '已 push' if rp.returncode == 0 else f'push 失敗: {rp.stderr.strip()[:200]}'


def resolve_pkgbase(name):
    """把包名換成它真正的 pkgbase。

    AUR 的 git repo 是**按 pkgbase 建**的，split 包沒有自己的 repo。實測
    `linux-cjktty-headers` 的 RPC 回 base=linux-cjktty，而
    `git clone https://aur.archlinux.org/linux-cjktty-headers.git` 回 **rc=0 但倉是空的**
    （AUR 對未知路徑會建立空倉），於是程式一路走到讀 PKGBUILD 才 FileNotFoundError。
    回 None 代表查無此包。
    """
    url = f"https://aur.archlinux.org/rpc/?v=5&type=info&arg[]={urllib.parse.quote(name)}"
    try:
        d = json.loads(urllib.request.urlopen(url, timeout=25).read().decode())
    except Exception:
        return None, 'RPC 查詢失敗'
    if not d.get('resultcount'):
        return None, 'AUR 查無此名（可能已被刪除或本來就不是獨立包）'
    r = d['results'][0]
    return r.get('PackageBase'), r.get('Version')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--bases', help='JSON 陣列或逗号分隔的 pkgbase 清單')
    ap.add_argument('--file', help='從檔案讀 pkgbase 清單（一行一個）')
    ap.add_argument('--push', action='store_true')
    ap.add_argument('--no-sums', action='store_true', help='不跑 updpkgsums（除錯用）')
    ap.add_argument('--work', default=os.environ.get('AUR_WORK', tempfile.mkdtemp(prefix='aur-')))
    a = ap.parse_args()

    if a.file:
        bases = [l.strip() for l in open(a.file) if l.strip() and not l.startswith('#')]
    elif a.bases:
        s = a.bases.strip()
        bases = json.loads(s) if s.startswith('[') else [x.strip() for x in s.split(',')]
    else:
        ap.error('要給 --bases 或 --file')

    os.makedirs(a.work, exist_ok=True)
    results, seen = [], set()
    for name in bases:
        real, aurver = resolve_pkgbase(name)
        if not real:
            results.append((name, 'FAIL', aurver))
            print(f'{name:32s} 查無：{aurver}', flush=True); continue
        if real != name:
            print(f'{name:32s} → 不是獨立 pkgbase，實際是 {real} 的 split 包，併進去處理', flush=True)
        if real in seen:
            results.append((real, 'SKIP', '同 pkgbase，已處理過')); continue
        seen.add(real)

        base = real
        adir = os.path.join(a.work, base)
        if not os.path.isdir(os.path.join(adir, '.git')):
            run(['rm', '-rf', adir])
            if run(['git', 'clone', '-q', AUR_HTTPS.format(base=base), adir]).returncode:
                results.append((base, 'FAIL', 'clone AUR 失敗')); print(f'{base:32s} clone 失敗', flush=True); continue
        # AUR 對未知路徑會給一個 rc=0 的**空倉**，PKGBUILD 不存在才會炸 FileNotFoundError。
        # 上面 resolve_pkgbase 已經擋掉多數情況，這裡再守一次，空倉直接回報而不是拋例外。
        if not os.path.isfile(os.path.join(adir, 'PKGBUILD')):
            results.append((base, 'FAIL', 'clone 回來是空倉（沒有 PKGBUILD）'))
            print(f'{base:32s} 空倉，跳過', flush=True); continue
        run(['git', '-C', adir, 'fetch', '-q', 'origin'])
        run(['git', '-C', adir, 'reset', '-q', '--hard', 'origin/master'])
        try:
            edits, note = compute(adir, os.path.join(a.work, base + '.cache'))
        except Exception as e:
            results.append((base, 'FAIL', f'{type(e).__name__}: {e}'))
            print(f'{base:32s} 例外 {e}', flush=True); continue
        if not edits:
            results.append((base, 'SKIP', note)); print(f'{base:32s} 不動：{note}', flush=True); continue
        msg = f'{base}: upstream update'
        res = apply_bump(adir, edits, msg, a.push, not a.no_sums)
        results.append((base, 'BUMP', f'{note} ⇒ {res}'))
        print(f'{base:32s} {note} ⇒ {res}', flush=True)

    print(json.dumps(results, ensure_ascii=False))
    if any(s == 'FAIL' for _, s, _ in results):
        sys.exit(2)


if __name__ == '__main__':
    main()
