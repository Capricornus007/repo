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
  # 2026-11-26（shard4 #120）：export RUSTFLAGS 不會被 su/eval 帶進 makepkg
  # 子進程，必須顯式注入命令字串。值自己帶引號，避免 eval 雙層拆分。
  local _rust=""
  if [ -n "${RUSTFLAGS:-}" ]; then
    _rust="RUSTFLAGS='${RUSTFLAGS}' "
  fi
  if [ -n "${PGO_RUNAS:-}" ]; then
    eval "${PGO_RUNAS} \"${PGO_MP_ENV:-}${_rust}makepkg ${extra}\""
  else
    su builder -c "${_rust}makepkg ${extra}"
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
    # 2026-11-26 gcc 自我插樁實錘（shard3 #94）：gcc 是本倉唯一用 xgcc 邊編邊跑
    # autoconf conftest 的包，LDFLAGS 的 -fprofile-generate 會滲進 conftest 連結，
    # 讓 libatomic 的 "cannot run C compiled programs" 誤判。gcc 本體的插樁完全由
    # CFLAGS 提供、gcc driver 自動鏈 libgcov，LDFLAGS 不需要 PGO（ gcc 也是 !lto ）。
    # 其餘包照舊注入 LDFLAGS——LTO 下 lto1 重編需要它（dhcpcd 實錘），不能一刀切。
    if [ "$name" = gcc ]; then
      printf '\n# PGO pass1 (六最)\nCFLAGS+=" -fprofile-generate=%s -fprofile-update=atomic"\nCXXFLAGS+=" -fprofile-generate=%s -fprofile-update=atomic"\nOPTIONS=(!strip docs !libtool staticlibs emptydirs zipman purge !debug lto)\n' \
        "$pd" "$pd" >> /etc/makepkg.conf
      # 2026-11-26（shard3 #101 gcc 實錘）：gcc 特殊分支刻意不加 LDFLAGS
      # 的 -fprofile-generate（避免 xgcc conftest 誤判），但 gcc 自建 gcov-tool
      # 用 g++ 連結並帶 -static-libgcc → libiberty.a 的插樁對象需要 __gcov_*
      # 而 static libgcc 不會自動拉 libgcov → undefined reference __gcov_merge_add。
      # 只補 -lgcov（不帶 -fprofile-generate）：conftest 不會產生 .gcda，
      # 不影響「cannot run C compiled programs」判斷。
      # 2026-11-27（shard3 #107 gcc 實錘）：gcc 自己的 Makefile 把 $(LDFLAGS)
      # 放在物件檔**前面**，而 binutils 的 --as-needed 在還沒看到 __gcov_*
      # 引用時就把 libgcov.a 丟掉 → 後面 libiberty/libcody 的插樁對象全紅。
      # 本機實測：`gcc -Wl,--as-needed -lgcov foo.o` 必 undefined；
      # 加 --whole-archive 後順序無關（libgcov.a 很小，整包拉進來無害）。
      printf 'LDFLAGS+=" -Wl,--whole-archive -lgcov -Wl,--no-whole-archive"\n' >> /etc/makepkg.conf
    else
      printf '\n# PGO pass1 (六最)\nCFLAGS+=" -fprofile-generate=%s -fprofile-update=atomic"\nCXXFLAGS+=" -fprofile-generate=%s -fprofile-update=atomic"\nLDFLAGS+=" -fprofile-generate=%s -fprofile-update=atomic"\nOPTIONS=(!strip docs !libtool staticlibs emptydirs zipman purge !debug lto)\n' \
        "$pd" "$pd" "$pd" >> /etc/makepkg.conf
    fi
    # 2026-11-25（librewolf 實測）：Rust 的 cargo-linker 用 -nodefaultlibs 連結，
    # clang 的 -fprofile-generate 不會自動補 compiler-rt profile 執行庫 →
    #   ld.lld: undefined symbol: __llvm_profile_instrument_target / _memop
    # 顯式把庫加進 LDFLAGS；靜態庫無符號引用時 linker 不會拉進來，對純 GCC 包無害。
    # 用 -l 讓 lld 從 resource dir 自己找，避免硬編路徑/符號連結失效
    # （CI 實測硬編路徑寫進去後錯誤依舊 → 該 .a 在容器裡是壞的 symlink）。
    # 若找到 Static 檔，直接用 -l 名稱；同時加 -L 指向 resource lib/linux。
    _rt_dir="$(clang -print-resource-dir 2>/dev/null)/lib/linux"
    if [ -d "$_rt_dir" ]; then
      printf 'LDFLAGS+=" -L%s -lclang_rt.profile-x86_64"\n' "$_rt_dir" >> /etc/makepkg.conf
      # 2026-11-27（shard4 #121 librewolf 實錘）：Rust 的 build script
      # （webrender 等）用 clang 連結、不吃 LDFLAGS，只吃 RUSTFLAGS →
      # __llvm_profile_instrument_target/_memop undefined。與 gcc 側
      # __gcov_* 對稱：同一個 compiler-rt 也經 RUSTFLAGS link-arg 注入。
      # append（不覆蓋 librewolf 的 -C target-cpu、sccache 的 allow-shlib）。
      export RUSTFLAGS="${RUSTFLAGS:-} -Clink-arg=-L$_rt_dir -Clink-arg=-lclang_rt.profile-x86_64"
    fi
    # 2026-11-26（rustup / shard4 #113 實錘）：混合工具鏈包——Rust 的
    # cc crate 用系統 gcc 編 C 依賴（aws-lc-sys/zstd-sys 等），gcc 插樁產生
    # __gcov_* 符號，但最終連結由 rustc 掌控：`gcc -fuse-ld=lld -nodefaultlibs`
    # 且**不讀 LDFLAGS**（cargo 只吃 RUSTFLAGS）→ LDFLAGS 補的 -lgcov 根本
    # 進不了連結指令。故同時透過 RUSTFLAGS 傳 link-arg；對純 Rust/非 Rust
    # 包無害（無 __gcov 引用時 lld --gc-sections 直接丟掉）。
    _gcov_a="$(gcc -print-file-name=libgcov.a 2>/dev/null || true)"
    # 2026-11-26（shard4 #118 實錘）：CI 裡 gcc 被 setup-sixmax 的包裝腳本
    # 取代，`gcc -print-file-name=libgcov.a` 回傳的路徑 [ -f ] 判斷失敗 →
    # RUSTFLAGS 整段沒寫進去 → rustup 的 aws-lc-sys C 依賴插樁符號
    # __gcov_*_atomic 全部 undefined。三層 fallback：gcc 探測 → 標準路徑 find
    # → 直接 -lgcov（lld 自己從 default lib path 找）。
    if [ ! -f "$_gcov_a" ]; then
      _gcov_a="$(find /usr/lib/gcc -name libgcov.a -type f 2>/dev/null | grep -v '/32/' | head -1 || true)"
    fi
    # 2026-11-26（shard4 #120 實錘）：只寫 makepkg.conf 的 RUSTFLAGS+="..." 不夠——
    # makepkg 預設不把 makepkg.conf 的 shell 變數 export 給構建子進程，rustc 根本
    # 看不到 link-arg（job 日誌 RUSTFLAGS 0 命中、rustc 指令無 -Clink-arg）。
    # 改為直接 export 到 pgo-build 的環境（makepkg 及其 cargo/rustc 子進程繼承），
    # 同時保留 makepkg.conf 寫入作雙保險。
    if [ -f "$_gcov_a" ]; then
      _gcov_dir="$(dirname "$_gcov_a")"
      # 不寫 LDFLAGS：-fprofile-generate 已讓 gcc 自動鏈「正確位元寬」的 libgcov；
      # 手動 -L<64 位元目錄> -lgcov 會被 multilib(-m32) 包繼承 →
      # ld.lld: libgcov.a is incompatible with elf32-i386（mesa-tkg #1044 實錘）。
      # rustc 不讀 LDFLAGS，只靠這條 RUSTFLAGS link-arg 補 __gcov_*。
      export RUSTFLAGS="${RUSTFLAGS:-} -Clink-arg=-L$_gcov_dir -Clink-arg=-lgcov"
      printf 'RUSTFLAGS+=" -Clink-arg=-L%s -Clink-arg=-lgcov"\n' "$_gcov_dir" >> /etc/makepkg.conf
    else
      # 連 find 都找不到時不帶 -L：gcc driver 的 default search path 仍含
      # libgcov，-Clink-arg=-lgcov 讓 lld 自己解析（總比不注入強）。
      echo '::warning::找不到 libgcov.a 檔案，RUSTFLAGS 改用 -lgcov 由 linker 解析'
      export RUSTFLAGS="${RUSTFLAGS:-} -Clink-arg=-lgcov"
      printf 'RUSTFLAGS+=" -Clink-arg=-lgcov"\n' >> /etc/makepkg.conf
    fi
    # pass1 只編插樁樹、不出包(--noarchive)；去掉 -f(force 重建由 rm src/pkg 保證)。
    p1flags=$(printf '%s' "$flags" | sed -E 's/ -f([ ]|$)/ /g')
    if ! (cd "$pkgdir" && run_makepkg "$p1flags --noarchive") 2>&1 | tee /tmp/makepkg-pgo-pass1.log; then
      cp "$CONF_BAK" /etc/makepkg.conf
      echo "::error::PGO pass1 插樁編譯失敗：${name}（六最無豁免，修源頭）"
      exit 1
    fi
    cp "$CONF_BAK" /etc/makepkg.conf
    # conftest.gcda 污染（run 45380396175 acl 實測、lfs-pacman 817a48e 本機 gcc16 復現確認）：
    # pass1 configure 把每個 conftest 的 profile 寫成 $PD/#<來源路徑以#分隔>#conftest.gcda
    # ——basename 以 '#' 開頭，不是 'conftest'！舊的 find -name 'conftest*.gcda'
    # （含 e0d30b9 的「通配」）從來沒匹配到，清理形同虛設。
    # pass2 的 -fprofile-use 讀到 pass1 殘留 → configure 每個 conftest.c 控制流不同 →
    # gcc -Werror=coverage-mismatch → configure 誤判「cannot compute suffix of executables」失敗。
    # 正確 glob 是 '*conftest*.gcda'（前綴也要有 *）；真實來源 .gcda 不含 conftest 字樣、
    # 完整保留 → pass2 PGO 零降級、無豁免。
    find "$pd" -name '*conftest*.gcda' -delete 2>/dev/null || true
    echo "::notice::PGO 訓練：${name}"
    run_train || true
    find "$pd" -name '*conftest*.gcda' -delete 2>/dev/null || true
    gcda=$(find "$pd" -name '*.gcda' 2>/dev/null | wc -l)
    if [ "$gcda" -eq 0 ]; then
      # 區分兩類零 gcda（repo shard2 #101 實測 18 包掛閘）：
      #   結構性：純腳本/純數據/圖標主題包（elementary-icon-theme 純 SVG 等）
      #           沒編 C 代碼 → pass1 無 .gcno，pass2 的 -fprofile-use 是
      #           no-op，放行不算「無 profile 包」。
      #   訓練失敗：有 .gcno（插樁對象存在）但訓練沒跑到 → 真問題，判死。
      gcno=$(find "$pkgdir/src" -name '*.gcno' 2>/dev/null | wc -l)
      if [ "$gcno" -eq 0 ]; then
        echo "::notice::${name} PGO 訓練零 .gcda 但亦零 .gcno（無 C 代碼，結構性無 profile），放行"
      else
        cp "$CONF_BAK" /etc/makepkg.conf
        echo "::error::${name} PGO 訓練零 .gcda（有 ${gcno} 個插樁對象但訓練沒跑到；六最無豁免，修 /usr/local/bin/pgo-train 訓練負載）"
        exit 1
      fi
    fi
    echo "$gcda" > "$GCDA_COUNT_FILE"
    echo "::notice::PGO 訓練收到 ${gcda} 個 .gcda：${name}"
    rm -rf "$pkgdir/src" "$pkgdir/pkg"
    # -Wno-error=coverage-mismatch（lfs-pacman #113 coreutils/grep 實測）：
    # 兩遍編譯間 configure 非確定性讓個別函式 CFG 漂移（chroot.c main arcs
    # 94 vs 88），coverage-mismatch 默認硬錯誤炸 pass2；降警告後
    # -fprofile-correction 照常校正，PGO 不降級。
    # gcc 同 pass1：LDFLAGS 不注入 PGO，避免自我插樁污染 conftest（CFLAGS 已足夠）。
    if [ "$name" = gcc ]; then
      printf '\n# PGO pass2 (六最)\nCFLAGS+=" -fprofile-use=%s -fprofile-correction -Wno-missing-profile -Wno-error=coverage-mismatch -fprofile-partial-training"\nCXXFLAGS+=" -fprofile-use=%s -fprofile-correction -Wno-missing-profile -Wno-error=coverage-mismatch -fprofile-partial-training"\n' \
        "$pd" "$pd" >> /etc/makepkg.conf
    else
      printf '\n# PGO pass2 (六最)\nCFLAGS+=" -fprofile-use=%s -fprofile-correction -Wno-missing-profile -Wno-error=coverage-mismatch -fprofile-partial-training"\nCXXFLAGS+=" -fprofile-use=%s -fprofile-correction -Wno-missing-profile -Wno-error=coverage-mismatch -fprofile-partial-training"\nLDFLAGS+=" -fprofile-use=%s -fprofile-correction -Wno-missing-profile -fprofile-partial-training"\n' \
        "$pd" "$pd" "$pd" >> /etc/makepkg.conf
    fi
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
