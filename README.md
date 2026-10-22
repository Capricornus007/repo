# PKGBUILD snapshots (security baseline)

Dated copies of everything that decides **what this feed builds**: the packaging
definitions of every matrix package plus the CI definitions themselves.

Why a second copy exists: half the packages take their `PKGBUILD` from AUR at build
time, so master never stores it — if AUR drops, renames or poisons a package there is
no record of what we actually built. The CI files (`.github/workflows`, `scripts`,
`tools`, `docs`) only ever exist on master, so a force-push or a careless hand edit
would leave nothing to compare against. Added after the October 2026 AUR malware
reports.

## What is in a snapshot

```
pkgbuild-snapshots/<YYYY-MM-DD>/
  <package>/            one directory per matrix package
    PKGBUILD …          extra files too (*.install, *.patch, *.service, *.sysusers …)
  ci/workflows/         .github/workflows/*.yml
  ci/scripts/           scripts/*
  ci/tools/             tools/*
  ci/docs/              docs/*
  MANIFEST.json         per-file SHA-256, source (in-tree | aur), kind, missing_aur[]
```

* `in-tree` — copied from master at snapshot time.
* `aur` — a real `git clone --depth 1` of the AUR repository (download only, never executed).
* `missing_aur[]` — the AUR repository came back **empty** (deleted or orphaned). Those
  packages have no snapshot here; `android-ndk-23`, `linux-ltscjk` and `mesa-tkg-git` were
  in that state on 2026-10-22 (their real sources are Google's NDK, kernel.org and the
  chaotic-aur Tk-Glitch template).

## Refresh

Automatic: `.github/workflows/backup-pkgbuilds.yml` on master runs daily (18:40 UTC) and
also accepts a manual `workflow_dispatch`. It writes into `pkgbuild-snapshots/<date>/`
and pushes one commit per day. The generator is `tools/pkgbuild_snapshot.py` on master
(`--only pkg1,pkg2` exists for debugging a single package).

Manual, from a master checkout:

```bash
python3 tools/pkgbuild_snapshot.py --repo . --out /tmp/snap/pkgbuild-snapshots/$(date -u +%F)
```

## Restore — the part that makes a backup worth having

Fetch the branch once; everything below reads from it without checking anything out:

```bash
git -C ~/Downloads/repo fetch origin pkgbuild-snapshots
B=origin/pkgbuild-snapshots
D=2026-10-22
```

1. **Read** a historical definition:
   `git show $B:pkgbuild-snapshots/$D/<pkg>/PKGBUILD`
2. **Verify** a snapshot against its own manifest before trusting it:
   ```bash
   git -C ~/Downloads/repo show $B:pkgbuild-snapshots/$D/MANIFEST.json > /tmp/m.json
   python3 - <<'PY'
   import json,hashlib,subprocess
   m=json.load(open('/tmp/m.json')); d='2026-10-22'
   bad=0
   for pkg,i in m['packages'].items():
       for f,want in i['files'].items():
           p=f'pkgbuild-snapshots/{d}/{pkg}/{f}'
           r=subprocess.run(['git','-C','/home/avatar/Downloads/repo','show',f'origin/pkgbuild-snapshots:{p}'],capture_output=True)
           if r.returncode: print('MISSING',p); bad+=1
           elif hashlib.sha256(r.stdout).hexdigest()!=want: print('HASH',p); bad+=1
   print('checked, problems =',bad)
   PY
   ```
3. **Put a package back into master** (e.g. AUR served something different and you want
   the known-good copy):
   ```bash
   git show $B:pkgbuild-snapshots/$D/<pkg>/PKGBUILD > ~/Downloads/repo/<pkg>/PKGBUILD
   ```
   then commit in `~/Downloads/repo` as usual. For an `aur` package this also means
   adding it to the in-tree list in `build-packages.yml` — see `docs/in-tree-packages.md`.
4. **Rebuild the feed after master is lost**: check out this branch, copy the needed
   package directories back into a repo skeleton, and take `.github/workflows`,
   `scripts`, `tools`, `docs` from `pkgbuild-snapshots/$D/ci/`. Then re-run
   `build-one-package.yml` per package rather than the whole matrix.

## House rules

* This branch is **append-only**. Never force-push it and never delete an old date
  directory — the whole point is a comparison point that cannot be rewritten.
* Snapshot commits carry `[skip ci]`; they must not trigger the build matrices.
* Never execute a snapshotted AUR file to "check" it. Read it, hash it, diff it.
