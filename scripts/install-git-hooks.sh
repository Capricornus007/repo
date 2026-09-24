#!/usr/bin/env bash
# 把本倉自帶的 git hooks 裝進 .git/hooks。hook 不進版本控制，clone 後要跑一次。
set -euo pipefail
root=$(git rev-parse --show-toplevel)
dest="$root/.git/hooks"
mkdir -p "$dest"
cat > "$dest/pre-commit" <<'HOOK'
#!/usr/bin/env bash
# PKGBUILD 有實質改動但 pkgver/pkgrel 沒動時，自動 pkgrel +1（見 scripts/bump-pkgrel）
exec "$(git rev-parse --show-toplevel)/scripts/bump-pkgrel"
HOOK
chmod +x "$dest/pre-commit" "$root/scripts/bump-pkgrel"
echo "已安裝 pre-commit → scripts/bump-pkgrel"
