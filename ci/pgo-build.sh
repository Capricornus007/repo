#!/bin/bash
# 六最 v2.26：全量兩段式 PGO（移植自 lfs-pacman/ci/build-recipe.sh）。
# 主構建 step 只呼叫本腳本的三個階段，避免 workflow run 塊撞 GitHub 21000 表達式上限。
#
# 用法（在主構建 step 內，$PWD = pkg_dir）：
#   PGO_RUNAS="$_runas" PGO_MP_ENV="$_mp_env" pgo-build.sh pre   <name> <flags> <pd> <pkgdir>   # pass1 插樁編譯 + 訓練
#   （主 step 跑 until makepkg 迴圈 = pass2 最終出包）
#   pgo-build.sh post <name>                                                                   # 還原 makepkg.conf
#
# 原理：makepkg -p 自訂 conf 會踩 readonly OPTIONS（run 43623494641 實測 90/91 包全死），
# 故直接對 /etc/makepkg.conf 追加旗標、每段前快照還原。PGO 旗標必須同時進 LDFLAGS：
# LTO 下最終連結由 lto1 重編，dhcpcd 類「編譯用 CFLAGS、連結只用 LDFLAGS」的構建系統
# 會漏 libgcov → undefined reference to __gcov_*（run #51 dhcpcd 實測）。
set -uo pipefail

stage=$1
name=${2:-}
pd=${4:-}
pkgdir=${5:-$PWD}
CONF_BAK="/tmp/makepkg.conf.pgo-bak-${name}"
GCDA_COUNT_FILE="/tmp/pgo-gcda-count-${name}"

run_makepkg() {  # $1 = 額外 makepkg 參數字串（flags）
  local extra="$1"
  if [ -n "${PGO_RUNAS:-}" ]; then
    eval "${PGO_RUNAS} \"${PGO_MP_ENV:-}makepkg ${extra}\""
  else
    su builder -c "makepkg ${extra}"
  fi
}
run_train() {
  if [ -n "${PGO_RUNAS:-}" ]; then
    eval "${PGO_RUNAS} \"cd '${pkgdir}' && /usr/local/bin/pgo-train '${pkgdir}' '${pd}'\""
  else
    su builder -c "cd '${pkgdir}' && /usr/local/bin/pgo-train '${pkgdir}' '${pd}'"
  fi
}

case "$stage" in
  pre)
    flags=${3:-}
    echo "::notice::PGO 兩段式 pass1：${name}（profile dir=${pd}）"
    cp /etc/makepkg.conf "$CONF_BAK"
    rm -rf "$pd" "$pkgdir/src" "$pkgdir/pkg"
    mkdir -p "$pd"; chown -R builder "$pd" 2>/dev/null || true
    printf '\n# PGO pass1 (六最)\nCFLAGS+=" -fprofile-generate=%s -fprofile-update=atomic"\nCXXFLAGS+=" -fprofile-generate=%s -fprofile-update=atomic"\nLDFLAGS+=" -fprofile-generate=%s -fprofile-update=atomic"\nOPTIONS=(!strip docs !libtool staticlibs emptydirs zipman purge !debug lto)\n' \
      "$pd" "$pd" "$pd" >> /etc/makepkg.conf
    # pass1 只編插樁樹、不出包(--noarchive)；去掉 -f(force 重建由 rm src/pkg 保證)。
    p1flags=$(printf '%s' "$flags" | sed -E 's/ -f([ ]|$)/ /g')
    if ! (cd "$pkgdir" && run_makepkg "$p1flags --noarchive") 2>&1 | tee /tmp/makepkg-pgo-pass1.log; then
      cp "$CONF_BAK" /etc/makepkg.conf
      echo "::error::PGO pass1 插樁編譯失敗：${name}（六最無豁免，修源頭）"
      exit 1
    fi
    cp "$CONF_BAK" /etc/makepkg.conf
    # conftest.gcda 污染：pass1 configure 每個 conftest（含 autotools 子測試
    # conftest-<n> 變體）都寫 profile dir，
    # pass2 configure 路徑相同 → checksum 不匹配自檢炸(coreutils/attr 實測)。只清 conftest。
    find "$pd" -name 'conftest*.gcda' -delete 2>/dev/null || true
    echo "::notice::PGO 訓練：${name}"
    run_train || true
    find "$pd" -name 'conftest*.gcda' -delete 2>/dev/null || true
    gcda=$(find "$pd" -name '*.gcda' 2>/dev/null | wc -l)
    if [ "$gcda" -eq 0 ]; then
      cp "$CONF_BAK" /etc/makepkg.conf
      echo "::error::${name} PGO 訓練零 .gcda（六最無豁免，不出無 profile 包；修 /usr/local/bin/pgo-train 訓練負載）"
      exit 1
    fi
    echo "$gcda" > "$GCDA_COUNT_FILE"
    echo "::notice::PGO 訓練收到 ${gcda} 個 .gcda：${name}"
    rm -rf "$pkgdir/src" "$pkgdir/pkg"
    printf '\n# PGO pass2 (六最)\nCFLAGS+=" -fprofile-use=%s -fprofile-correction -Wno-missing-profile -fprofile-partial-training"\nCXXFLAGS+=" -fprofile-use=%s -fprofile-correction -Wno-missing-profile -fprofile-partial-training"\nLDFLAGS+=" -fprofile-use=%s -fprofile-correction -Wno-missing-profile -fprofile-partial-training"\n' \
      "$pd" "$pd" "$pd" >> /etc/makepkg.conf
    ;;
  post)
    [ -f "$CONF_BAK" ] && cp "$CONF_BAK" /etc/makepkg.conf
    gcda="?"; [ -f "$GCDA_COUNT_FILE" ] && gcda=$(cat "$GCDA_COUNT_FILE")
    echo "::notice::PGO 兩段式完成：${name}（${gcda} 個 .gcda 餵進 pass2）"
    ;;
  *)
    echo "用法: $0 {pre|post} <name> [flags] <pd> [pkgdir]"; exit 2
    ;;
esac
