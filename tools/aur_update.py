#!/usr/bin/env python3
"""AUR 回推引擎：算出版號／內容級更新，重算 sums，產 .SRCINFO，可選擇推上 AUR。

只在 aur-update.yml 這個**獨立**工作流裡跑。它跟 build-packages.yml 的差別是重點：
build 那條會 clone 上游 PKGBUILD 並實際執行 prepare()/build()（任意代碼），
這條只讀 PKGBUILD、抓上游 tarball 算雜湊（updpkgsums 下載但不執行 build()），
所以 AUR 寫入金鑰跟「跑來路不明代碼」不會出現在同一個 job 裡。

設計上寧可漏推也不能亂推：任何一步算不出可信結果就整包跳過並印原因，
不猜、不寫半個版本號進去。
"""
import argparse, json, os, re, shlex, subprocess, sys, tempfile, urllib.request

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
    out = []
    for e in entries:
        if not e.startswith('git+'):
            continue
        spec = e[4:]
        url, _, frag = spec.partition('#')
        module = branch = None
        for kv in frag.split('&'):
            if kv.startswith('module='):
                module = kv[7:]
            elif kv.startswith('branch='):
                branch = kv[7:]
        name = module or os.path.basename(url.rstrip('/'))
        out.append((url, name[:-4] if name.endswith('.git') else name, branch))
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
                    if run(['git', 'clone', '-q', url, d]).returncode:
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
        notes.append('靜態版號型（無 pkgver()）')

    for rule in CONTENT_RULES.get(os.path.basename(adir), []):
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
    results = []
    for base in bases:
        adir = os.path.join(a.work, base)
        if not os.path.isdir(os.path.join(adir, '.git')):
            run(['rm', '-rf', adir])
            if run(['git', 'clone', '-q', AUR_HTTPS.format(base=base), adir]).returncode:
                results.append((base, 'FAIL', 'clone AUR 失敗')); print(f'{base:32s} clone 失敗', flush=True); continue
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
