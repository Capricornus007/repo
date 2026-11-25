#!/bin/sh
# feed-bot CI 專用：把目標機（AMD Ryzen 5 5600U / Zen 3）的 -march 套到每一次
# gcc / g++ / cc / c++ 呼叫，含 -m32 的 32 位步驟。
#
# 為什麼需要它：makepkg.conf 的 CFLAGS 只會進到 configure/meson 型配方；
# bzip2 的 Makefile 自己寫死 CFLAGS=，libcap 硬寫 CC="gcc -m32 -march=i686"，
# udev-standalone 直接 make CFLAGS=...，這些都吃不到 makepkg.conf。
# 把 -march 放在 argv 最後，GCC 由左至右處理，會蓋掉前面的 -march=i686 /
# -mtune=generic，所以 64 位與 32 位一致都是 znver3。
#
# 這不是 -march=native：不探測宿主 CPU，GitHub runner 是什麼 CPU 都不影響目標。
#
# 2026-11-25 修正（qt6-base-git run 45680731567 實測）：呼叫端已明確指定
# 「非 32 位基線」的 -march 時尊重之，不再尾部覆蓋。起因是 Qt 的
# config.tests/x86intrin 帶 -march=cannonlake 編譯 AVX-512 intrinsic 探測，
# 被尾部 znver3 蓋掉（znver3 無 AVX-512）→ always_inline target mismatch
# → Qt 把這個 required config.test 的失敗當 configure 錯誤 → 整包中止。
# 尊重明確 -march 對可跑性是安全的：呼叫端指定的 march 只要不超出
# znver3 能力就能在目標機跑（Qt 的 AVX-512 路徑本身有 qsimd 執行期分派）。
# 32 位基線（i386..i686）照舊覆蓋：libcap 等硬寫 -march=i686 的步驟
# 仍要拉回 znver3（這是本包裝器存在的初衷）。
real="/usr/bin/${0##*/}"
for a in "$@"; do
  case "$a" in
    -dumpmachine|-dumpversion|--version|-print-*|-v|-###)
      exec "$real" "$@"
      ;;
  esac
done
case "$*" in
  *-march=i386*|*-march=i486*|*-march=i586*|*-march=i686*)
    exec "$real" "$@" -march=znver3 -mtune=znver3
    ;;
  *-march=*)
    exec "$real" "$@"
    ;;
  *)
    exec "$real" "$@" -march=znver3 -mtune=znver3
    ;;
esac
