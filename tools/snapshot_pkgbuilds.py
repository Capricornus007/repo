#!/usr/bin/env python3
"""Snapshot every packaging definition the build matrices use.

In-tree packages are copied from this repository; AUR packages are fetched as the
official AUR snapshot tarball (https://aur.archlinux.org/cgit/aur.git/snapshot/).
Nothing is executed: PKGBUILDs are only downloaded/extracted. The result is a
dated directory with a MANIFEST.json (source, URL, file sha256).
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import time
import urllib.error
import urllib.request

ROOT = os.environ.get('REPO_ROOT', os.getcwd())
WORKFLOWS = ['.github/workflows/build-git-packages.yml', '.github/workflows/build-kernels.yml']
OUT = os.path.join(ROOT, 'pkgbuild-snapshots', sys.argv[1] if len(sys.argv) > 1 else time.strftime('%Y-%m-%d'))
AUR = 'https://aur.archlinux.org/cgit/aur.git/snapshot/%s.tar.gz'
EXTERNAL = {
    'u1s1-bin': 'https://github.com/Capricornus007/u1s1-bin.git',
}
SKIP_DIRS = {'.git', 'src', 'pkg', '__pycache__', '.gradle', 'build'}
SKIP_SUFFIX = ('.pkg.tar.zst', '.pkg.tar.xz', '.pkg.tar.gz', '.part')


def matrix():
    packages = {}
    for rel in WORKFLOWS:
        lines = open(os.path.join(ROOT, rel), encoding='utf-8').read().splitlines()
        start = None
        for i, line in enumerate(lines):
            if line.strip() == 'packages: |':
                start = i + 1
                break
        if start is None:
            continue
        block, begun = [], False
        for line in lines[start:]:
            text = line.strip()
            if not begun and text.startswith('['):
                begun = True
            if begun:
                block.append(text)
                if text.endswith(']'):
                    break
        for entry in json.loads('\n'.join(block)):
            packages[entry['repo_name']] = entry
    return packages


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def copy_tree(src, dst):
    files = []
    for base, dirs, names in os.walk(src):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in names:
            if name.endswith(SKIP_SUFFIX):
                continue
            path = os.path.join(base, name)
            if os.path.islink(path) or not os.path.isfile(path):
                continue
            rel = os.path.relpath(path, src)
            target = os.path.join(dst, rel)
            os.makedirs(os.path.dirname(target), exist_ok=True)
            shutil.copy2(path, target)
            files.append(rel)
    return files


def fetch(url, dest):
    # AUR occasionally resets TLS mid-handshake; curl retries the whole transfer.
    rc = subprocess.run(['curl', '-4', '-fL', '--retry', '5', '--retry-all-errors',
                         '--connect-timeout', '20', '--max-time', '120', '-o', dest, url],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode
    if rc == 22:  # HTTP error, usually 404
        raise urllib.error.HTTPError(url, 404, 'not found', None, None)
    if rc != 0:
        raise OSError('curl exit %d for %s' % (rc, url))


def snapshot_aur(name, dst, manifest):
    tarball = os.path.join('/tmp', 'aur-%s.tar.gz' % name)
    try:
        fetch(AUR % name, tarball)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False
        raise
    with tarfile.open(tarball) as tar:
        members = [m for m in tar.getmembers() if m.isfile() and '..' not in m.name.split('/')]
        for m in members:
            rel = m.name.split('/', 1)[1] if '/' in m.name else m.name
            if not rel or rel.endswith(SKIP_SUFFIX):
                continue
            target = os.path.join(dst, rel)
            os.makedirs(os.path.dirname(target) or dst, exist_ok=True)
            src = tar.extractfile(m)
            if src is None:
                continue
            with open(target, 'wb') as out:
                shutil.copyfileobj(src, out)
    os.remove(tarball)
    return True


def main():
    packages = matrix()
    os.makedirs(OUT, exist_ok=True)
    manifest = {'date': os.path.basename(OUT), 'packages': {}}
    for i, (name, entry) in enumerate(sorted(packages.items()), 1):
        dst = os.path.join(OUT, name)
        src_dir = os.path.join(ROOT, name)
        item = {'source': None, 'url': None, 'kind': entry.get('kind', 'none'), 'files': {}}
        if os.path.isfile(os.path.join(src_dir, 'PKGBUILD')):
            os.makedirs(dst, exist_ok=True)
            files = copy_tree(src_dir, dst)
            item.update(source='in-tree', url=None)
        else:
            os.makedirs(dst, exist_ok=True)
            ok = snapshot_aur(name, dst, manifest)
            if ok:
                files = sorted(os.path.relpath(os.path.join(b, f), dst)
                               for b, _, fs in os.walk(dst) for f in fs)
                item.update(source='aur', url=AUR % name)
            elif name in EXTERNAL:
                subprocess.run(['git', 'clone', '--depth', '1', EXTERNAL[name], dst], check=True,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                files = sorted(os.path.relpath(os.path.join(b, f), dst)
                               for b, _, fs in os.walk(dst) for f in fs if '.git' not in b)
                item.update(source='external', url=EXTERNAL[name])
            else:
                shutil.rmtree(dst, ignore_errors=True)
                item.update(source='missing')
                files = []
        item['files'] = {f: sha256(os.path.join(dst, f)) for f in files}
        manifest['packages'][name] = item
        print('[%d/%d] %-40s %s' % (i, len(packages), name, item['source']))
        if item['source'] == 'aur':
            time.sleep(0.15)
    with open(os.path.join(OUT, 'MANIFEST.json'), 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2, sort_keys=True)
    missing = [n for n, v in manifest['packages'].items() if v['source'] == 'missing']
    print('done: %d packages, missing %d: %s' % (len(packages), len(missing), missing))


if __name__ == '__main__':
    main()
