#!/bin/bash
# feed-bot CI 專用：clang / clang++ 包裝器。與 gcc-znver3.sh 同一手法，但方向相反：
# gcc 包裝器是「補上 -march」，clang 包裝器是「濾掉 GCC 專有旗標」。
#
# 為什麼需要它：makepkg-flags.conf 的 CFLAGS 是全域的，clang 構建的包
# （llvm-bolt-git 用 clang 自舉、librewolf-git 的 cc-rs 探測到 clang、
# sccache-git 的 aws-lc-sys 走 cc crate）會原樣吃到 CFLAGS，而其中
# -fipa-pta / -fdevirtualize-at-ltrans / -fgraphite-identity / -floop-nest-optimize
# 是 GCC（graphite/ipa-pta）專有的，clang 直接
#   clang: error: unknown argument: '-floop-nest-optimize'
# 整個 job 紅（2026-11-22 run #86：llvm-bolt-git / librewolf-git 實測）。
#
# 用戶鐵律「遇衝突修源頭不降旗標」：GCC 構建的包旗標一根不動，只在
# clang 入口處濾掉它不認得的旗標——GCC 包照吃全套六最，clang 包吃
# clang 認得的部分（-march=znver3 -mtune=znver3 -O3 -pipe 等都認）。
#
# -flto=auto 一併濾掉：那是 GCC 的 LTO 模式寫法，clang 的 LTO 由構建系統
# 自己控制（-flto[=full|thin]），makepkg 的 lto option 不該越俎代庖。
real="/usr/bin/${0##*/}"
args=()
for a in "$@"; do
  case "$a" in
    -fipa-pta|-fdevirtualize-at-ltrans|-fgraphite-identity|-floop-nest-optimize|-flto=auto) ;;
    *) args+=("$a") ;;
  esac
done
exec "$real" "${args[@]}"
