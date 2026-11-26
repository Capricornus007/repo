#!/bin/bash
# Arch 官方包抓齊：PKGBUILD + 同目錄所有根層 blobs（patch / install / hook）。
# 2026-11-26 shard4 #111 實錘：gsm 只抓 PKGBUILD → gsm-shared.patch 不存在。
# 用法：arch-fetch.sh <pkg_dir> <pkgbase>
# API 失敗時退回只抓 PKGBUILD（不讓抓檔失敗炸掉整顆包）。
set -uo pipefail
_dir="$1"
_pkgbase="$2"
_raw="https://gitlab.archlinux.org/archlinux/packaging/packages/${_pkgbase}/-/raw/main"
mkdir -p "$_dir"
curl -sfL "${_raw}/PKGBUILD" -o "$_dir/PKGBUILD" || exit 1
_proj="archlinux%2Fpackaging%2Fpackages%2F${_pkgbase}"
if curl -sfL "https://gitlab.archlinux.org/api/v4/projects/${_proj}/repository/tree?ref=main&per_page=100" \
     -o /tmp/_arch_tree.json \
   && jq -e 'type == "array"' /tmp/_arch_tree.json >/dev/null 2>&1; then
  jq -r '.[] | select(.type == "blob") | select(.path | contains("/") | not) | .name' /tmp/_arch_tree.json \
    | while IFS= read -r _af; do
        [ -n "$_af" ] && [ "$_af" != 'PKGBUILD' ] || continue
        curl -sfL "${_raw}/${_af}" -o "${_dir}/${_af}"
      done
else
  echo "::warning::GitLab tree API 取不到 ${_pkgbase}，退回只抓 PKGBUILD"
fi
