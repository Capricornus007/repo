#!/bin/sh
# 从上游 .deb 拆包读真实版本（不信 AUR/网页显示的版本）。
# 用法: sh ci/deb-version.sh <deb-url> [arch]
# 输出: 规范化 pkgver（wechat: 4.1.13.29 / linuxqq: 3.2.35_54395）
set -eu
URL="$1"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
# .deb 的 control 在 ar archive 头部，只需前 256KB
curl -fsSL --retry 3 --connect-timeout 30 -r 0-262143 -o "$TMP/head.deb" "$URL"
cd "$TMP"
ar x head.deb control.tar.xz control.tar.gz 2>/dev/null || true
if [ -f control.tar.xz ]; then
  tar -xf control.tar.xz ./control 2>/dev/null
elif [ -f control.tar.gz ]; then
  tar -xzf control.tar.gz ./control 2>/dev/null
fi
[ -f control ] || { echo "ERROR: 拆包找不到 control" >&2; exit 1; }
# 读 Package 和 Version
PKG=$(sed -n 's/^Package: *//p' control | head -1)
VER=$(sed -n 's/^Version: *//p' control | head -1)
[ -n "$VER" ] || { echo "ERROR: control 无 Version" >&2; exit 1; }
# linuxqq 的 Version 是 3.2.35-54395 -> pkgver 规范为 3.2.35_54395
case "$PKG" in
  linuxqq) echo "$VER" | sed 's/-/_/' ;;
  *) echo "$VER" ;;
esac
