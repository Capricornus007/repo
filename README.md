# PKGBUILD snapshots (security baseline)

Dated copies of every packaging definition used by the build matrices in
`Capricornus007/repo`. In-tree packages are copied as-is; AUR packages are the
official AUR snapshot tarballs (download only, never executed). Each snapshot
has a `MANIFEST.json` with the source URL and a SHA-256 per file.

The first snapshot is `2026-10-22`, taken after the October 2026 AUR malware
reports, so a later AUR change can be compared against a known copy.

- Refresh: `python3 tools/snapshot_pkgbuilds.py $(date +%F)` from the repo root,
  then commit the new directory here.
- Missing in 2026-10-22 (special sources, not AUR/in-tree): `android-ndk-23`,
  `linux-ltscjk`, `mesa-tkg-git`. They come from Google's NDK, kernel.org and the
  chaotic-aur Tk-Glitch template respectively.
