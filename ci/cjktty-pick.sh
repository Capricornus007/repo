#!/bin/bash
# 從 cjktty-patches 可用補丁列表中挑最適合目標內核系列的一份。
# 用法: cjktty-pick.sh <series如7.3> < 補丁文件名列表(stdin)
# 優先順序: 1) 本線精確  2) 本線 rc  3) 跨線: 不高於目標的最大版本
#           4) 全高於目標時取最小版本（只能向上漂移一個次版本）
set -euo pipefail
series="${1:?need series}"
major="${series%%.*}"; minor="${series##*.}"
# 提取補丁版本號 (7.2-rc7 -> "7 2", 7.0.8 -> "7 0")
ver_of() {
  local n="$1"
  echo "$n" | sed -nE 's/^cjktty-([0-9]+)\.([0-9]+).*/\1 \2/p'
}
avail="$(cat)"
# 1) 本線精確: cjktty-<series>.patch 或 cjktty-<series>.<N>.patch
pick=$(printf '%s\n' "$avail" | grep -E "^cjktty-${series//./\\.}(\.[0-9]+)?\.patch$" | sort -V | tail -n1 || true)
[ -n "$pick" ] && { echo "$pick"; exit 0; }
# 2) 本線 rc: cjktty-<series>-rc<N>.patch
pick=$(printf '%s\n' "$avail" | grep -E "^cjktty-${series//./\\.}-rc[0-9]+\.patch$" | sort -V | tail -n1 || true)
[ -n "$pick" ] && { echo "$pick"; exit 0; }
# 3) 跨線: 不高於目標 (major 相同、minor <= 目標) 的最大版本
best=""; best_min=-1
while IFS= read -r n; do
  [ -n "$n" ] || continue
  read -r pmaj pmin < <(ver_of "$n")
  [ "$pmaj" = "$major" ] || continue
  [ "$pmin" -le "$minor" ] || continue
  if [ "$pmin" -gt "$best_min" ]; then best="$n"; best_min="$pmin"; fi
done <<< "$avail"
[ -n "$best" ] && { echo "$best"; exit 0; }
# 4) 全高於目標: 取最小版本（只容忍相鄰次版本，差距由 caller 檢查）
printf '%s\n' "$avail" | grep -E '^cjktty-.*\.patch$' | sort -V | head -n1
