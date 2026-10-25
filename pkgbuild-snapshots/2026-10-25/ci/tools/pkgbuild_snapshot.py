#!/usr/bin/env python3
"""把自動構建倉的全部打包檔快照成一個目錄，供 `backup-pkgbuilds.yml` 推到
孤兒分支 `pkgbuild-snapshots`。

為什麼要有這支：AUR 那半數的包，PKGBUILD 只存在於 AUR 與本倉的**建置期下載**裡，
本倉 master 沒存；AUR 一旦被投毒／下架／被移除（2026-10 的 iThome 報導那類），
或本倉 master 被 force-push，就再也拿不回「我們當初到底建的是哪一份」。
所以每天定時把兩邊都存一份進同一個倉的另一條分支，並連 CI 定義檔
（.github/workflows／scripts／tools／docs）一起存——那層最容易被亂手改壞，
而且只有 master 一份。

用法：tools/pkgbuild_snapshot.py --repo <倉根> --out <快照目錄>
"""
import argparse, hashlib, json, os, re, shutil, subprocess, sys

MATRIX_FILES = ('.github/workflows/build-git-packages.yml',
                '.github/workflows/build-kernels.yml')
# 矩陣裡 kind=aur 的包，其 pkgbase 可能不等於包名（split 包）；這類靠 aur_rpc 查。
AUR_CLONE = 'https://aur.archlinux.org/{base}.git'


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def matrix_entries(repo):
    """從雨個排程 workflow 裡抓出所有 {"key":…,"repo_name":…,"kind":…} 條目。"""
    out = {}
    for rel in MATRIX_FILES:
        p = os.path.join(repo, rel)
        if not os.path.isfile(p):
            continue
        for line in open(p, encoding='utf-8'):
            m = re.search(r'\{"key".*\}\s*,?\s*$', line.strip())
            if not m:
                continue
            try:
                e = json.loads(m.group(0).rstrip(','))
            except Exception:
                continue
            name = e.get('repo_name') or e.get('key')
            if name:
                out.setdefault(name, e)
    return out


def in_tree_dirs(repo):
    """master 目錄版（in-tree）包：倉根下與包同名的目錄。"""
    return {d for d in os.listdir(repo)
            if os.path.isdir(os.path.join(repo, d)) and not d.startswith('.')}


def copy_tree(src, dst, skip=('.git', 'src', 'pkg', '__pycache__')):
    files = {}
    for root, dirs, fs in os.walk(src):
        # 剪掉構建殘留目錄，以及**巢狀 git 倉**（例如 nashira-git/nashira 那種
        # 建置期 mirror clone：上一次快照把它的 objects 全塞進孤兒分支，
        # 23 檔「倉裡查無」就是這樣來的）。
        dirs[:] = [d for d in dirs if d not in skip
                   and not os.path.exists(os.path.join(root, d, '.git'))]
        for f in fs:
            s = os.path.join(root, f)
            rel = os.path.relpath(s, src)
            d = os.path.join(dst, rel)
            os.makedirs(os.path.dirname(d), exist_ok=True)
            shutil.copy2(s, d)
            files[rel] = sha256(d)
    return files


def aur_files(base, workdir):
    """`git clone --depth 1` AUR 倉，取全部打包檔（PKGBUILD／*.install／*.patch／*.service…）。"""
    tgt = os.path.join(workdir, base)
    shutil.rmtree(tgt, ignore_errors=True)
    r = subprocess.run(['git', 'clone', '-q', '--depth', '1',
                        AUR_CLONE.format(base=base), tgt],
                       capture_output=True, text=True, timeout=180)
    if r.returncode != 0:
        return None, (r.stderr or r.stdout).strip()[:160]
    # ⚠️ 輸出目錄**不能放在源碼目錄裡面**：舊版寫 `tgt/.snapshot-out`，而 copy_tree 會把
    #    自己剛建出來的這個子目錄當成源的一部分再遞迴複製，於是撞 distutils 的
    #    「Destination path ... already exists」——2026-10-22 的 run 39861036185 就是死在
    #    `/tmp/snap/pkgbuild-snapshots/2026-10-22/android-ndk-27/.snapshot-out already exists`。
    #    改成放在克隆目錄的**兄弟**位置，並在複製前清一次（冪等）。
    snap_out = tgt + '.out'
    shutil.rmtree(snap_out, ignore_errors=True)
    files = copy_tree(tgt, snap_out, skip=('.git',))
    if not files:
        # AUR 的倉被刪／移為 orphan 時，git 會給一個**空的**成功克隆；
        # 這種「查無此包」必須如實記進 missing_aur，不能當快照成功。
        # （2026-10-22 實測：android-ndk-23、linux-ltscjk、mesa-tkg-git 三顆就是這樣）
        shutil.rmtree(tgt, ignore_errors=True)
        return None, 'AUR 倉是空的（已下架或成 orphan）'
    return files, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', default='.')
    ap.add_argument('--out', required=True)
    ap.add_argument('--only', default='', help='除錯用：只處理這幾個包名（逗號分隔）')
    args = ap.parse_args()
    repo = os.path.abspath(args.repo)
    out = os.path.abspath(args.out)
    os.makedirs(out, exist_ok=True)
    work = os.path.join(out, '.aur-work')
    os.makedirs(work, exist_ok=True)

    entries = matrix_entries(repo)
    if args.only:
        keep = {x for x in args.only.split(',') if x}
        entries = {k: v for k, v in entries.items() if k in keep}
    intree = in_tree_dirs(repo)
    manifest, missing = {}, []
    for name, e in sorted(entries.items()):
        kind = e.get('kind') or ''
        pkgdir = os.path.join(repo, name)
        if name in intree and os.path.isfile(os.path.join(pkgdir, 'PKGBUILD')):
            files = copy_tree(pkgdir, os.path.join(out, name))
            src = 'in-tree'
        else:
            base = e.get('pkgbase') or name
            files, err = aur_files(base, work)
            if files is None:
                missing.append({'package': name, 'pkgbase': base, 'error': err})
                continue
            # 冪等：上一輪半途而廢時可能已留下同名目錄/檔案（run 40028409928 實測
            # shutil.move 把 .out 搬進舊目錄後撞 'Destination path already exists'），
            # 重跑前先清掉目標，快照本來就該是「以本輪爲準」的全量覆寫。
            dest = os.path.join(out, name)
            if os.path.isdir(dest):
                shutil.rmtree(dest, ignore_errors=True)
            elif os.path.exists(dest):
                os.remove(dest)
            shutil.move(os.path.join(work, base + '.out'), dest)
            shutil.rmtree(os.path.join(work, base), ignore_errors=True)
            src = 'aur'
        manifest[name] = {'files': files, 'kind': kind, 'source': src}

    # CI 定義檔：只有 master 一份，最容易被改壞，一併進快照
    ci = {}
    for label, rel in (('workflows', '.github/workflows'), ('scripts', 'scripts'),
                       ('tools', 'tools'), ('docs', 'docs')):
        p = os.path.join(repo, rel)
        if not os.path.isdir(p):
            continue
        for k, v in copy_tree(p, os.path.join(out, 'ci', label)).items():
            ci[f'ci/{label}/{k}'] = v

    json.dump({'date': os.environ.get('SNAP_DATE') or __import__('datetime').date.today().isoformat(),
               'packages': manifest,
               'missing_aur': missing,
               'ci': ci,
               'note': '每日自動快照：in-tree 包取 master 現檔，AUR 包取 AUR 現檔，'
                       '外加 CI 定義檔。缺的 AUR 包列在 missing_aur（幽靈／改名包）。'},
              open(os.path.join(out, 'MANIFEST.json'), 'w'),
              ensure_ascii=False, indent=1, sort_keys=True)
    shutil.rmtree(work, ignore_errors=True)
    print(f'快照完成：套件 {len(manifest)} 顆（in-tree '
          f'{sum(1 for v in manifest.values() if v["source"]=="in-tree")}／aur '
          f'{sum(1 for v in manifest.values() if v["source"]=="aur")}）、'
          f'CI 檔 {len(ci)} 個、AUR 取不到 {len(missing)} 顆')
    for m in missing:
        print(f'  缺 {m["package"]}（pkgbase={m["pkgbase"]}）: {m["error"]}', file=sys.stderr)
    return 0


if __name__ == '__main__':
    sys.exit(main())
