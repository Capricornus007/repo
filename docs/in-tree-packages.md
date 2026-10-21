# in-tree 包為什麼必須列進 build-packages.yml「拉取对应的套件仓库」

CI 的通用規則是「名字以 `-git` 結尾 → clone AUR，否則 clone `github.com/<owner>/<repo_name>.git`」。
本倉的目錄版（in-tree）包會被那條規則搶走，所以**必須**在那個 step 的 `case` 名稱清單裡先攔掉。
逐包理由原本寫在 workflow 內，但含 `${{ }}` 的 step 有 **21000 位元組**的上限（shell 註解也計入，中文 1 字算 3 bytes），故搬到這裡。精確語意與踩雷實錄見文末「21000 上限的精確語意」，本地守門＝`scripts/workflow-step-budget.py`。
加新 in-tree 包時：清單加一行、說明寫進本檔，不要寫回 workflow。

---

npm-git／pnpm-git／go-git（用戶 2026-10-06 點名，全走本倉目錄版）：
  · npm-git：AUR 上根本沒有（實測 RPC info resultcount=0）。
  · pnpm-git：AUR 有，但那顆**編不過當前 master**（run #366 實測
    `couldn't read pnpm/crates/deps-restorer/src/cas-loader.mjs.inc`
    ——它漏了上游新增的 esbuild 建置期產物，所以版本卡在 v12.9.0）。
    本倉目錄版把那一步補回來，矩陣仍留 kind:aur 只為借用 giant if 的
    `matrix.kind != 'aur'` 跳過回推（與 openai-codex-git 同一手法，
    case 是首命中即中，走的是本倉目錄、不會去 clone AUR）。
  · go-git：AUR 那顆已死（LastModified=2020-08-07、版本停在
    go1.15beta1.r138），照抄就是降級，所以自己照 master 編。
jbr21／jbr25（用戶 2026-09-30 指令）：**必須**加在這裡，否則通用規則見
「不是 -git 結尾」就會掉到最後的 `git clone github.com/<owner>/<repo_name>.git`，
而 Capricornus007/jbr21 這個倉**不存在也不需要存在**（in-tree 包的 PKGBUILD
一律躺在本倉同名目錄，實證：bash-git／amd-debug-tools-git／pi-coding-agent-git
等六顆既有 in-tree 包都沒獨立倉）→ 會索要憑證、CI 無 TTY 直接 exit 128。
這批 in-tree 包（本倉同名目錄，PKGBUILD 要嘛是用戶 ~/.cache/yay 的本地版、
要嘛是我方改過的版本）。**必須在這裡先攔掉**：下面的通用規則見 '-git$'
就去 clone AUR，而 free-claude-code-git、qalculate-gtk-git 在 AUR 上
根本不存在（或內容不同），openai-codex-git 的 AUR 配方已跟不上上游，
alacritty-sixel-git 的 AUR 版抓的是 ayosec 原 fork（停在 0.17.0、沒跟上
master 的 0.18.0-dev，且源目錄名與版本探測對不上），adguardhome-git 雖在
AUR 有用戶要的是本地那份（規則 25）；clone 到 AUR/錯的 PKGBUILD 會直接紅
或拿到非用戶版。
amd-debug-tools-git：AUR 上确实有同名包（dreieck 維護），但穩定版 amd-debug-tools
住在 Arch 官方 extra 而不是 AUR，用戶要的是「照官方那份改的 -git」；
且 AUR 那份的 depends 照 pyproject 全抄、版本公式與本倉慣例不同，
故也攔下來走本倉目錄版（細節寫在 amd-debug-tools-git/PKGBUILD 檔頭）。
這三個 -git 包（openai-codex-git、alacritty-sixel-git、adguardhome-git 等）
版本都由 makepkg build 時現算，所以都已列進下方「更新校驗和並回推」的
giant if 排除清單；不然那步會為 1.9GB 級別的 git 源重跑 updpkgsums
（連續失敗 5 次就 exit 1 把 job 判紅）。
pi-coding-agent-git：AUR 那份（dougefresh）的 build() 到解開的 npm 包目錄裡
跑 `npm install --omit=dev`，會去註冊表要 @earendil-works/pi-codemode ——
而那個 workspace 包上游 HEAD 已列進 dependencies 卻**還沒發佈到 npm**
（實測 registry 404、倉內 packages/codemode 存在），所以 AUR 版恆紅。
本倉目錄版把該依賴指到本地 `npm pack` 出來的 tarball（file:），
不改上游依賴清單、不降版、不關校驗。保留矩陣上的 kind:aur 只為借用
 giant if 的 `matrix.kind != 'aur'` 自動跳過回推，**不是**要抓 AUR 那份。
serein（用戶 2026-10-03 點名）：AUR 上確實有同名包，但本倉要的是
「跟隨上游最新 nightly」＋「零 systemd」兩件事，AUR 那份版號寫死在檔內
（每次更新要人手工抬），故走 in-tree。它的依賴清單本來就沒有 systemd 條目
——沾 systemd 的是上游自附的 `serein-bin`（prebuilt）配方，裡面列
`systemd-libs>=262-1`，而 Artix 啟用的倉裡 systemd／systemd-libs／
libsystemd 三顆全部查無 → 那條路根本裝不起來，只能從源碼建。
細節與閘門寫在 serein-git/PKGBUILD 檔頭。
fsearch-git／lmdb-git（用戶 2026-10-05 點名進倉）：**不加進來就會被下面的
通用規則「名字以 -git 結尾 → clone AUR」搶走**，那是直接違反規則 25：
  · fsearch-git 的 AUR 版（xiota）pkgver() 只認「當前分支的祖先 tag」，而上游
    0.3.1/0.3.2 兩個 tag 落在 fsearch_0.3 維護分支、不在 master 上
    → 算出 0.3.r55.gcb6cd67；而
    `vercmp 0.3.1.r44.g975be2f 0.3.r55.gcb6cd67` = 1
    → 使用者本機那顆永遠「比倉庫新」、換裝永不發生（就是他報上來的現象）。
    本倉目錄版把基版號取「倉內最高編號 tag」，細節寫在 fsearch-git/PKGBUILD 檔頭。
  · lmdb-git 的 AUR 版（Chocobo1）實查最後更新 2023-05-20、
    算出 0.9.30.r22965，比用戶本機實裝的 lmdb 1.0.0 **還舊**
    （規則 15 直接違反），而且它抓的是
    openldap monorepo 預設分支（那上面 nearest tag 根本不是 LMDB_*）。
    本倉目錄版以 Arch 官方 extra/lmdb 的配方為底、改成鏡像 mdb.RE/1.0 分支，
    並靠 provides/conflicts/replaces 平順頂掉系統 lmdb，理由全寫在
    lmdb-git/PKGBUILD 檔頭。
  · qt6ct-git（用戶 2026-10-05 點名「重編 qt6ct-git 讓它掛上 6.12」）：AUR 那顆
    追的是 github 鏡像 trialuser02/qt6ct，master 凍在 0.9+6 筆（55dba87），
    而 0.9 代碼在 Qt≥6.10 **必然編不過**——Qt 把 private/qgenericunixthemes_p.h
    改名成單數 qgenericunixtheme_p.h，上游到 0.11 才加版本分支與 Qt6::GuiPrivate
    （實測照抄 AUR 的 qmake 流程 MAKEPKG_EXIT=4，報 fatal error 找不到該頭檔）。
    官方上游是 opencode.net/trialuser/qt6ct（master == tag 0.11 == 00823e4）。
    本倉目錄版：來源改官方上游、建構改 CMake、並把 depends 釘成
    qt6-base=<建置時 Qt 版本>——Qt6 的 platform theme 插件有 minor 硬閘
    （6.12 實測拒載 6.11 編的 .so，訊息 Ignoring QPA plugin due to mismatching
    Qt versions），釘版本讓 Qt 換代時 yay 立刻判這顆過期並重編，
    不會再出現「Qt 升級後主題靜默失靈、yay 因為 epoch 永遠不換代」。
這三包都**不標 kind**（純 in-tree），所以下方的「更新校驗和並回推」那步要
手動把它們排除掉——那步會 updpkgsums 再 push 到 Capricornus007/<包名>.git，
而 in-tree 包根本沒有那個獨立倉。
連同 PKGBUILD 把目錄內**全部**檔案取進容器：bash-git 的 dot.*/system.*、
free-claude-code-git 的 .install 都是 source/install 引用的本地檔，
只抓 PKGBUILD 會讓 makepkg 報「was not found in the build directory」。
用 contents API（帶 github.token，免 60/hr 限流）動態列檔，以後目錄再加
輔助檔也不用改 CI；API 萬一異常（限流 / 非 JSON）就退回只抓 PKGBUILD，
至少維持舊行為，不會把本來能過的 nodejs/ttf/qalculate 也帶崩。

---

gstreamer／lib32-glib2（用戶 2026-10-08 點名：「lib32-glib2 跟 gst 那些軟件包
爲什麼沒弄源碼直出軟件包？」）：
  · **為什麼原本是缺席的**：查證結論沒有客套——**沒有正當理由，就是漏了**。
    倉裡 149 條矩陣 0 命中、`git log --all -S'lib32-glib'` 為空，這批東西
    **從未進過倉**（不是被降級成 kind:aur、也不是被移走）。用戶機上現裝的是
    Artix 官方：`lib32-glib2 2.90.1-1`（[lib32]，packager ndowens）、
    `gstreamer 1.28.7-3`（[world]，packager Dudemanguy），
    `/var/log/pacman.log` 實寫 `pacman -S world/gst-libav world/gst-plugins-bad`。
  · **gstreamer 必頌整組收**：`pkgbase=gstreamer` 一次拆 25 個子包
    （Arch 官方 PKGBUILD 1318 行、pkgname 陣列 25 項、makedepends 165 條）。
    只收其中幾顆會造成 feed 與官方混裝，同一支 `libgst*-1.0.so` 由不同 build
    提供 → ABI 錯位。所以 `pkgname` 陣列**逐字沿用官方、不自己裁**。
  · **不準走 kind:artix 容器**：官方 makedepends 有 `systemd-libs`，而實查
    world／world-goblins／system／galaxy／lib32 五倉**全部查無**
    `systemd-libs` 與 `libsystemd` → 丟進 artix 容器必恆紅（qt6ct 的
    `devtools` 就是同一類坑）。走預設 archlinux:base-devel 容器。
    另外實測本機 world 版所有 `libgst*.so` 與 `libgstreamer-1.0.so` 都沒有
    連結 libsystemd（ldd 掃 0 hits）→ 不會重演 fcitx5「裝完載不到動態庫」。
  · **lib32-glib2 標 `kind: multilib`**（新 kind）：需要 [multilib] 倉與
    `/usr/share/meson/cross/lib32`（實查 extra 與 world 的 meson-1.12.0-1 都有
    該檔）；`arch-meson` 來自 devtools，工作流在 `kind != artix` 時已裝。
    「初始化容器環境（Arch／Artix）」那步新增一段 `kind == 'multilib'`：開 [multilib]
    ＋`pacman -Syu`＋預裝 lib32 底層鏈。**不與 kind:tkg 共用分支**——tkg 那段
    還要做 LLVM 對齊與 customization.cfg，混進來會把 mesa 專有邏輯帶進 lib32。
  · **checkdepends 有 bootstrap 迴圈**（含 lib32-glib2 自己）＋ 3 條 glib 測試
    補丁；`--nocheck` 目前**只給 kind:aur**，in-tree 包照跑 check，所以這顆的
    測試會實跑（多 20–40 分鐘）。**不准用 kind:aur 混過**——那會連
    `--skipchecksums` 一起吞掉，等於把校驗和也放棄了。
  · **epoch=1 的取捨**（用戶「不準設計降級路徑／憑什麼要讓它缺席」的代價）：
    同包名要蓋過官方，只能靠 epoch 取得換代抓手（手法同 gh-git commit 6b01eba；
    `repo-add -p` 與 pacman 都只比版號，版號相同時 feed 完全沒意義）。
    代價是**之後每顆都要跟著官方抬版，停更就會卡在舊版**；因此驗收不能只看
    badge：唯一判據是 deploy job「整合並更新 repo.db 數據庫」日誌裡有沒有
    `A newer version for '<pkg>' is already present in database`（字串實查自
    `/usr/bin/repo-add:256`，出現即代表寫庫被拒）。
  · 輔助檔：lib32-glib2 五個（3 個 .patch ＋ `gio-querymodules-32.hook`、
    `gio-remove-module-cache-32.hook`）、gstreamer 兩個 .patch，全部從
    `gitlab.archlinux.org/archlinux/packaging/packages/<包>/-/raw/main/` 原樣取，
    與 PKGBUILD 同目錄；in-tree 分支用 contents API 動態全抓，不用改 CI。
  · 兩顆都要在「更新校驗和並回推」的 giant if 裡排除（`repo_name` 兩條＋
    `matrix.kind != 'multilib'`），否則 updpkgsums 之後會往**不存在的獨立倉**
    `Capricornus007/gstreamer.git` push（實測該倉不存在也不需要存在）。
  · **2026-10-11 `elements_gdkpixbufoverlay` 這條線（用戶紀律：容器缺環境就補環境，
    不准跳測試）**。真因不在 gdk-pixbuf 解不了圖，而是 glycin 的 bwrap 沙箱在容器裡
    起不來——builder 進程在 bwrap 設 loopback 那一刻 `CapEff=0000000000000000` →
    `bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted`。容器其他前提實測
    都在：`--privileged`、`unprivileged_userns_clone=1`、`max_user_namespaces=63838`、
    `/` 無 nosuid、root 身分跑 `bwrap --unshare-all` rc=0，缺的就是那一顆 cap。
    已否證兩條：給 bwrap 上 file capabilities（#413：bwrap 自己拒「Unexpected
    capabilities but not setuid」）；用 `su` 帶 caps（/usr/bin/su 是 setuid 檔，
    execve setuid/setgid 時內核清掉整個 ambient 集，capabilities(7)）。
    → 落地：「云端编译」那步**只對 gstreamer** 把 `su builder -c` 換成
      `setpriv --reuid=builder --regid=builder --clear-groups --inh-caps=+net_admin
       --ambient-caps=+net_admin env -i … bash -c`（setpriv 不像 su 會重建環境，
      所以要自己把 HOME/USER 換掉；跑之前先自檢一次，過不了就退回 su——這顆剛綠，
      不能拿它試錯）。PKGBUILD 的探針判定邏輯不動：cap 補到了就 bwrap rc=0、
      自動走真沙箱路徑；補不到才用上游自備的 `GLYCIN_DISABLE_SANDBOX=i-know-the-risks`
      降級（值必須是這一串，設 `1` 等於沒設；這是上游 meson `test_disable_sandbox`
      的同一條路，元素與解碼照跑，只是不套沙箱殼）。CapEff／CapBnd 現在印進 check()
      日誌，cap 有沒有跟上肉眼可判。
    · 順帶修掉一條**自己做出來的假診斷**：#419 那版把整條 pipeline 當單一 argv 餵給
      gst-launch，只会得到 `erroneous pipeline: syntax error`；現在逐詞傳參
      （`videotestsrc num-buffers=3 ! gdkpixbufoverlay location=… ! fakesink` 各佔一個
      參數），`location` 也改餵檔案系統路徑（餵 `file://…` 會被當成檔名）。#418 那
      三層探針的「全綠」是假綠：探針拿的是 `find` 到的第一張圖，不是測試編譯進二進位
      的那張；而 gdkpixbufoverlay 載圖失敗走 `GST_ELEMENT_ERROR`，只 post 到 bus、
      不寫 stderr，所以 meson 的 errorlog 永遠只剩 set_state 回 FAILURE。
    · 診斷 3（直接執行 `gst-plugin-scanner`）留著：`External plugin loader failed`
      （gstpluginloader.c:437）是**另一條**線索，指 GStreamer 的外部插件載入 helper
      在容器裡起不來，與沙箱是兩件事，別混在一起。

CI run #394 的兩記紅與修法（實測，不是推測）：
  · gstreamer 紅在 `install file (gstreamer.install) does not exist`：
    該檔是 PKGBUILD 第 361 行用 `install=gstreamer.install` 宣告的，
    **不在 `source=()` 陣列裡**，所以照 source 陣列抓輔助檔會漏掉它。
    已從 Arch 官方目錄補抓（144 bytes，內容是給 gst-ptp-helper 上
    setcap 的 post_install/post_upgrade）。教訓：in-tree 包的輔助檔清單
    要同時掃 `source=()` **與** `install=`／`backup=` 等變數，不能只看 source。
  · lib32-glib2 紅在 check()：391 支 gio 測試 Ok 381 / Fail 2，失敗的是
    `gdbus-peer` 與 `gdbus-address-get-session`，兩支都是 SIGABRT（容器裡
    沒有 session/system bus，拿不到總線位址），不是断言失敗。Arch 自己的
    构建環境帶 bus 所以不會遇到。修法：makedepends 加 `dbus`、check() 改成
    `dbus-run-session -- meson test ...`，給它一個真的 session bus；
    **不用 --nocheck、也不 --no-suite 跳過整個 gio**，那是放棄 391 支測試。

---

linux-firmware-nfp-git（用戶 2026-10-10 裁決：停止在壞掉的 AUR PKGBUILD 上疊 sed，
自己寫一份 in-tree 由本倉維護）。必須在這裡攔掉，否則通用規則見 `-git$` 就去
clone AUR 的 `linux-firmware-git` pkgbase。逐點理由：
  · **AUR 那份在 CI 從沒建成功過**，而且一關過了露下一關：
    (a) 授權行 `install -m644 LICEN*` 仍指頂層，上游早已把授權檔搬進 `LICENSES/`
        → 樣式匹配到 LICENSES 目錄本身 → `install: omitting directory 'LICENSES'`
        → package() 中止（run #426 實測）；
    (b) 上一輪在 CI 用 sed 修掉 (a) 後露出第二關：`install: cannot stat
        'linux-firmware-git/LICENSE.amd-ucode'` → package_amd-ucode_git() 中止。
        該檔在頂層**確實存在**（kernel.org cgit 查過 a3e1417a 的檔案清單），
        所以不是上游改名，是 AUR 那份對「來源目錄／工作檔」的假設壞了——它的
        source 是裸 `linux-firmware-git::git+<url>.git`、不帶 `#tag=`／`#commit=`。
        → 那兩條 sed 已隨本次改動一併移除（留著只會誤導日後的人）。
  · **基準是 Arch 官方 core 倉那份**（實測 `linux-firmware` 與 `linux-firmware-nfp`
    都在 core、20260916-1），依本倉判準「穩定版住官方倉 → in-tree 並以官方那份為底」。
    官方 426 行拆 20 顆子包；本倉**只做 nfp 一顆**（選項 B 整組收被否）：
    矩陣本來就只有 nfp 這條需求；整組收會把用戶機上全部 Wi-Fi/GPU/NVMe 固件一起
    換成 git 尖端並顶掉 core 同名包，風險與收益不成比；官方那套「`make install-zst`
    全壓 1.4GB 再 `_pick` 搬出去」對單顆來說是每三小時 CI 白燒 99%。
  · **裝檔改成「過濾 WHENCE」**：上游 `copy-firmware.sh` 只讀兩樣東西——CWD 的
    WHENCE（只認 File:/RawFile:/Link: 三種行，`Version:` 是註記它不管）與相對
    CWD 的源檔。所以 package() 把 WHENCE 過濾成只剩 `Driver: nfp` 那一段，在臨時
    stage 目錄放 `netronome -> 源/netronome` 符號鏈接，腳本只會處理 nfp 的 40 個
    檔＋38 條鏈接，產出與官方同形（真檔 `*.zst` ＋同名 `*.zst` 鏈接，比對過用戶機
    上 Garuda 那顆的 `/usr/lib/firmware/netronome` 佈局）。stage 不含 `.git` 是
    故意的：`copy-firmware.sh` 只在 `.git/config` 存在時跑 `check_whence.py`，而
    它驗的是「整棵樹都被 WHENCE 覆蓋」，過濾版必然不過。三道防呆（過濾結果非空、
    `netronome/` 真的裝出檔、頂層只准有 netronome/）擋掉「綠燈出一顆只有授權檔的
    空包」——第二道是必要的：`copy-firmware.sh` 的複製迴路是 `... | while read`，
    迴路內失敗不會讓腳本非 0 退出，上游目錄一旦改名就可能「零產物卻回 0」。
    makedepends 因此只要 `git`＋`rdfind`（官方的 parallel/python 用不到：不傳 -j、
    不跑 check_whence.py；rdfind 要留是因为 dedup 是官方每顆子包都跑的）。
  · **保留 `kind:"aur"` 但拿掉 `"pkgbase"` 欄位**：case 首命中即中，走的是本倉目錄、
    不會去 clone AUR；留 kind 只為借用回推那步的 `matrix.kind != 'aur'`（與
    pnpm-git／pi-coding-agent-git 同一手法）。上面 gstreamer 那段「不准用 kind:aur
    混過」在這裡不適用——本包源是滾動 git、`sha256sums=('SKIP')` 本來就沒有校驗和
    可放棄，`--skipchecksums --nocheck` 零成本（PKGBUILD 無 check()）。
  · **`epoch=1` 與 `provides`／`conflicts` 是硬性欄位**（用戶機實測依據寫在
    PKGBUILD 檔頭）：現裝的是 Garuda Builder 的 `linux-firmware-nfp-git
    20261009.afabaf77-1`（epoch 0），本檔 pkgver() 錨在最新 tag（日期段
    20260916 < 20261009），不加 epoch 就是「CI 出包、用戶 `pacman -Syu` 永不換裝」；
    `mkinitcpio-firmware` 的 Depends 有 `linux-firmware-nfp`，靠本包 provides 滿足，
    拿掉即整機依賴斷鏈。

---

llvm-git（用戶 2026-10-11 點名「那六個全部，搬去 -git 版本的自動構建」；一個目錄產七顆
split：llvm-libs／llvm／llvm-lit／compiler-rt／lld／lldb／clang）：

  · **為什麼非 in-tree 不可**：三個來源都不給。① Artix world-goblins 的 DB 列了
    `lld-23.1.3-1`，實測 12 臺鏡像全部 404（該倉目錄裡只有 lldb、沒有 lld 檔）→ 本機
    卡在「llvm/clang 23.1.3 ＋ lld 23.1.1」，而 lld 補不上會讓整條 `-Syu` 原子失敗；
    ② AUR `llvm-git` 停在 18.0.0_r484887（2024-04）、`llvm-minimal-git` 停在
    21.0.0_r537041（2025-05）→ 走 kind:aur 取它們是「假尖端真降級」；③ Arch 自己的
    llvm 是 release tarball，跟不了 trunk。
  · **分割方案是用戶裁的，不是省事的**：不猜 CMake 的 `install-*` target（名字上游會改，
    而且 `install-llvm` 本身也含函式庫 → 必然重疊），改成 `build()` 一次性
    `cmake --install` 到 `$srcdir/stage`，各 `package_*()` 按路徑清單搬。
  · ⚠️ **搬必須是 `mv` 而不是 `cp`**：glob 表達不了「同目錄下誰不屬於我」
    （`usr/bin/llvm-*` 罩住 `usr/bin/llvm-lit`、`usr/lib/*.a` 罩住 `libLLVM*.a`），
    用 cp 時 `scripts/check-pkg-split-overlap.py` 實測報出 14 對交集。改 mv 後歸屬由
    **pkgname 的先後順序**決定（先搶者赢），所以 broad 樣式一律排在被它罩住的 narrow
    樣式之後；順序是 llvm-libs-git → llvm-lit-git → compiler-rt-git → lld-git →
    lldb-git → clang-git → llvm-git。
  · **2026-10-13：標頭與 cmake 設定檔搬回 `llvm-git`（改回 Arch 的邊界）**。實查
    `gitlab.archlinux.org/archlinux/packaging/packages/llvm/-/raw/main/PKGBUILD` 的
    `package_llvm()`(458) 與 `package_llvm-libs()`(482)：Arch 的 `llvm-libs` 只還原
    `lib{LLVM,LTO,Remarks}*.so*` ＋ `LLVMgold.so` ＋ `usr/lib/bfd-plugins/LLVMgold.so`
    符號鏈接（bug #28479），**`/usr/include/llvm*` 與 `/usr/lib/cmake/llvm` 留在 `llvm`**。
    我們先前把這兩樣收在 llvm-libs-git，邊界跟 Arch 不一致。因為 `package_llvm-git()`
    本來就有 `usr/include/*` 與 `usr/lib/cmake/*` 的 broad 兜底，這裡只要「不搬」就自然
    落回去（`check-pkg-split-overlap.py` 復核：無重疊）。附帶把 Arch 那條
    `bfd-plugins/LLVMgold.so` 符號鏈接補進 llvm-libs-git。
    ⚠️ 改邊界的代價＝全家族重編一輪（用戶裁定：「重編就重新編就是了，弄好不就好了」）。
    下游只要 `makedepends=(llvm)` 就能拿到標頭，跟 Arch 的習慣一致；執行期仍然只需要
    llvm-libs-git（mesa 那條鏈的 `llvm-libs-abi=<soname>` 鎖不變）。
  · ⚠️ **不准「先 `_move` 再 `_drop`」**：mv 過的檔頭已離開 stage，`_drop` 等於刪除。
    上一版就踩在這裡——clang-git 逐個 `_drop` 掉 `${_extra_tools[@]}`，而說好接手它們的
    `package_clang-tools-extra-git()` **根本沒列進 pkgname**（makepkg 不會呼叫它），
    結果 clangd／clang-tidy 等十幾支工具被 rm 掉後無人收＝從產物裡消失。實測 Artix 的
    `clang-tools-extra` 也不是獨立包（`pacman -Qi` 解析到 clang、兩份 `-Ql` 完全相同），
    所以正確做法是 clang-git 自己 provides 那兩個名字（系統 clang 23.1.3-1.1 的 Provides
    就是 `clang-analyzer=23.1.3 clang-tools-extra=23.1.3`）。
  · **`pkgver()` 的地雷**：上游最新 tag 不是語意版而是 `llvmorg-24-init`
    （`git ls-remote --tags` 查實：23.1.3 之後直接跳到 24-init），describe 回
    `llvmorg-24-init-<n>-g<sha>`。count 必須從 describe 字串本身拆；用
    `rev-list --count llvmorg-24..HEAD` 會因該 tag 不存在而落進 `|| echo 0`，每輪都算出
    r0、只剩 hash 段在變，而 hash 屬 alpha 段 ⇒ vercmp 不單調、repo-add 拒收
    （kew-git 同一個坑，那包靠 epoch=2 才爬出來）。已在 /tmp 用 mini repo 實測三種
    tag 形貌與單調性。
  · **CI 探測的通用缺口（順帶修）**：plan 的 -git 版本探測會 `source PKGBUILD` 後**直接
    呼叫包自己的 `pkgver()`**（比 kew 那顆「兩處要逐字相同」好），但它軟鏈進 `src/` 的
    目錄名清單沒有 `_pkgbase` → llvm 的 `cd llvm-project` 找不到路徑，會報「跑 pkgver()
    失敗」每輪跳過。已在清單補上 `"${_pkgbase:-}"`（同類包一起受益）。
  · **timeout 是天花板不是開關**：GitHub Actions 的 `jobs.timeout-minutes` 上限就是 360
    （feed 現值 360，`build-git-packages.yml:37`），調不上去。所以本包照 Arch 那份裁：
    關 tests/docs/benchmarks/examples、後端只留 X86;NVPTX;AMDGPU、runtimes 只 compiler-rt
    且 `COMPILER_RT_DEFAULT_TARGET_ONLY=ON`、polly/openmp/offload/libc++/libc++abi 全不進
    （本機 `pacman -Qs` 查實沒裝），並用 lld 當連結器＋`LLVM_PARALLEL_LINK_JOBS=2`
    （linking 是 RAM 瓶頸不是 CPU 瓶頸）。第一輪若仍撞 360，砍的順序是 lldb → 
    clang-tools-extra 那批工具，**不是關功能換綠燈**。
  · ⚠️ **上線前提（還沒做，別先發包）**：本機實測有 35 個已安裝的 `.so` 直接 NEEDED
    `libLLVM.so.23.1`，其中含 GL 驅動；而 mesa-tkg-git 那顆 CI job 目前裝的是倉庫裡的
    llvm-libs 23.1.3，產物就鏈著 `.23.1`。本包是用 trunk **取代**系統那套（裝進 /usr、
    同路徑、provides/conflicts/replaces 頂替），所以必須先讓 mesa 那個 job「裝我們產出的
    llvm-libs-git 再編」，否則這批一上線、裝下去 GL 直接黑。
  · **run #443 的紅與真因（2026-10-11，顶層 `$srcdir` 地雷）**：日誌是
    `mv: cannot stat '/stage/usr/include/llvm'`，但報錯的那行不是 bug 本身——
    頂層寫了 `_stage="$srcdir/stage"`，而 makepkg 是**先 source PKGBUILD、之後才算
    srcdir**（本機 `/usr/bin/makepkg` 查實：`source_safe "$BUILDFILE"` 在 211 行、
    `srcdir=` 在 1178/1181 行），於是 `$srcdir` 展開成空字串、`_stage` 變成 `/stage`，
    `DESTDIR=/stage cmake --install` 全盤落空。接著 `nullglob` 只救得了**含元字元**的
    樣式，`usr/include/llvm` 那種字面路徑 bash 根本不做檔名展開，原字串直送 mv
    → 才是那句 cannot stat（訊息指向假路徑、真因在變數）。修法：
    `_stage_init()` 在 build() 與每次 `_move` 裡現算；`_move` 另外會先確認暫存區存在，
    否則硬紅；build() 尾端的 `[ -d "$_stage/usr/lib" ]` 讓「install 回 0
    卻沒裝東西」無法蒙過。⚠️ 這是所有 PKGBUILD 的通用地雷：**函式以外不要取用
    `$srcdir`／`$pkgdir`**。
  · **第二次裁參數（用戶 2026-10-11 點名六包 ＋ 硬性要求）**：
    `LLVM_ENABLE_PROJECTS=clang;lld;lldb`、`LLVM_TARGETS_TO_BUILD=X86;AMDGPU`、
    `CMAKE_BUILD_TYPE=Release` ＋ `LLVM_ENABLE_ASSERTIONS=OFF`。代價寫清楚：
    clangd／clang-tidy／scan-build 那批 extra 工具不再產出、`nvptx-arch` 沒了，
    所以 clang-git 的 `provides` 也**拿掉** `clang-analyzer`／`clang-tools-extra`
    兩個虛名（留著等於讓 pacman 誤判依賴已滿足）。本機實查沒有任何已裝包依賴這
    兩個名字：依賴 `clang` 的是 doxygen、lldb、rust-bindgen-git、shiboken6-generator、
    linux-cachyos-cjktty-headers 這五顆，全部走 `clang` 本體。
    時效證據：run #443（job 114382764499）整包 2 時 31 分，沒撞 360；裁完只會更短。
  · **六包之外為什麼還多一颗 compiler-rt（依賴關係，不是湊數）**：用戶點名的六顆是
    llvm／llvm-libs／llvm-lit／clang／lld／lldb；`docs/upstream-pkgbuilds/clang.PKGBUILD:11`
    寫的是 `depends=('llvm-libs' 'gcc' 'compiler-rt' 'libgcc' 'libxml2')`，本機
    `pactree -r compiler-rt` 也顯示唯一的上游依賴就是 clang ⇒ **clang 不帶 compiler-rt
    就不是系統 clang 的等值替換**，所以 clang-git 的 depends 補
    `compiler-rt-git=$pkgver-$pkgrel`。方向必須是 clang→compiler-rt 單向：
    Arch 的 compiler-rt 只把 clang 當 **makedepends**，兩邊互指就會是 pacman 裝不起來的
    依賴環，故 compiler-rt-git 的 depends 改成 `glibc libgcc libstdc++`（照上游）。
    polly／openmp／offload／libc++／libc++abi 仍未收（用戶不认得 polly、本機 `pacman -Qs`
    查實沒裝）。
  · **四接點現況**（少一個就會「建了但發不出去」或「矩陣裡沒有它」）：
    ① `llvm-git/PKGBUILD` 一個目錄切 split（收集與 repo-add 都是 `pkg_dir/*.pkg.tar.zst`
      的 glob，分割不需要額外接點）；② `build-git-packages.yml` 的 `packages: |` 有
      `{"key": "llvm-git", …, "kind": "aur"}`；③ 版本偵測沒有 llvm 專屬 case，走 plan 步
      的通用 `-git` 分支（老實跑包自己的 `pkgver()`），它軟鏈進 `src/` 的目錄名清單已補
      `_pkgbase`（monorepo 的源碼目錄是 `llvm-project`，既不是 `${pkgname%-git}` 也不是
      `$pkgbase`，缺這條就每輪「跑 pkgver() 失敗」跳過）；④ 拉取步驟有 `llvm-git)` 顯式
      分支只 curl 本倉那一份 PKGBUILD（擋掉「名字以 -git 結尾 → clone AUR」的通用規則，
      否則會撈到 AUR 那顆 18.0.0 的假尖端）。`kind: aur` 另外借兩件事：掛 junlin03-aur
      源，以及讓「更新校驗和並回推」的 giant if（`matrix.kind != 'aur'`）不去 push
      不存在的 `Capricornus007/llvm-git.git`。

  · **2026-10-12 覆核（任務 #157）：七顆已經在 feed 裡，但產物有兩個「CI 全綠的壞包」**
    run #454（job 114714371131）七顆全綠並發布，`gh api releases/tags/current-repo` 查實
    `clang-git/compiler-rt-git/lld-git/lldb-git/llvm-git/llvm-libs-git/llvm-lit-git`
    都在 `24_r13699.g7159ce54c436-1`。**把產物下載回來拆**才看見日誌看不出的洞：

      ① **別名符號連結整批不見／发到錯的包**。`tar -tf lld-git-24_r13699…` 的 /usr/bin
         只有 `lld` 一個（官方 `pacman -Ql lld` 是 `lld ld.lld ld64.lld lld-link wasm-ld`
         五個）；`tar -tf clang-git-24_r13699…` 有 clang／clang-24／clang-cl／clang-cpp，
         **就是沒有 clang++ 與 amdgpu-arch**。根因不是 glob，而是 `_move` 的存在性檢查
         用 `[ -e ]`：上游那些別名是 CMake `install(CODE … create_symlink …)` 造的
         **相對符號連結**，`cmake --install` 對它們一行 `-- Installing:` 都不印（日誌查實，
         只印本體），而本體在 pattern 清單裡**排在前面、先被 `mv` 走**，於是別名在 `$_stage`
         裡當場變 dangling，`[ -e ]` 對 dangling symlink 一律回假 → 被當成「不存在」跳過。
         跳過≠消失：留在 stage 的它们又被最後一包 `llvm-git` 的 `usr/bin/*` 兜底掃走，
         所以「檔案有發出去」，只是**發到錯的包**——而 `clang-git` 不依賴 `llvm-git`，
         只裝 clang-git 的人徹底沒有 `clang++`；`-fuse-ld=lld` 是靠 exec `ld.lld` 找它的，
         少了那條連結等於 lld 不能用。修法：`_move` 的存在性判定改「`-e` 或 `-L`」、
         新增 `_alias()` 兜底補相對連結（本體在、別名不在才補，不覆寫），並給 lld／clang
         各加一道「入口沒齊就紅」的收口（與 compiler-rt 的 asan 檢查同一手法）。
         教訓：**`mv` 型分割不能只驗「檔案有沒有」，要驗「連結指不指得到」**，
         而 glob 與 `-e` 對 dangling symlink 的行為不同（glob 會命中、`-e` 不會）。
      ② **llvm-lit 的 python 套件裝進寫死的舊版本目錄**。`site.getpkgdir()` 在 Arch/Artix
         的 python 上**不存在**（本機 python 3.14.8 實測 `AttributeError`，那是 Debian 系
         補丁）→ 一定落到 `|| site=lib/python3.13/site-packages` 那個寫死的備援，
         `tar -tf llvm-lit-git-…` 查實整個 lit 被裝進 `/usr/lib/python3.13/…`，而系統
         python 是 3.14（`sysconfig.get_path("purelib")` 回 `/usr/lib/python3.14/site-packages`），
         本機 `python -c 'import lit'` 實測 ModuleNotFoundError（連 Artix 自己的 llvm-lit
         23.1.3 在本機也是同一個壞法）。改成向 sysconfig 要 purelib、要不到就硬紅，
         並補上官方同款 `/usr/bin/lit`（內容照抄系統那支 console script），最後用
         `PYTHONPATH=$pkgdir/… python -c 'import lit, lit.main'` 自我驗一次才放行。
      ③ 清掉我憑空發明的檔案名：`lld-rc／lld-elf／lld-macho／lld-macho-new／invoked／
         nvptx-arch`（`pacman -Ql lld` 查實官方只有五個入口；NVPTX 第二次裁參數時已拿掉）。

    驗證方式（全量llvm 交給 CI，本地只驗分割邏輯）：`/tmp/llvm-out/move-sim.sh` 造一個
    「本體＋相對符號連結」形貌的假 stage，`set -eu -o errtrace`（與 makepkg 同環境）
    逐顆呼叫 `package_*()`，25 條斷言全 ok——包含「ld.lld／lld-link／wasm-ld／ld64.lld／
    clang++／amdgpu-arch 必須在自己的包裡且 `-e` 指得到」與「llvm-git 不得再收到 ld.lld／
    clang++」。另外 `python scripts/check-pkg-split-overlap.py llvm-git/PKGBUILD` →
    `OK: 未發現跨包重疊樣式`；迷你 repo 實測 `pkgver()` 對 `llvmorg-24-init-<n>-g<sha>`／
    `llvmorg-23.1.3-<n>-g<sha>`／`llvmorg-24.0.0-rc1-<n>-g<sha>` 三種形貌分別算出
    `24_r<n>`／`23.1.3_r<n>`／`24.0.0_r<n>`，`vercmp` 三組單調性為
    `24_r13700 > 24_r13699`、`24_r13699 > 23.1.3`、`24.0.0_r5 > 24_r13699`（tag 往前進
    才換 base，不會倒掛）。**`makepkg --printsrcinfo` 不會跑 `pkgver()`**（實測印的是
    檔內靜態 `24.0.0_r0.g00000000000`），所以它不是版本探針，別拿它當證據。

  · **「六顆」的實測邊界**（expac 本機沒裝，改用 `LC_ALL=C pacman -Si` + 解 `.db`）：
    world-goblins 的 llvm 系九個名字 `llvm llvm-libs llvm-lit clang compiler-rt lld lldb
    openmp polly`（`tar -xf /var/lib/pacman/sync/world-goblins.db` 數出來的，另有 rocm-llvm*
    那批 10.0 與本線無關）；本機 `pacman -Qs` 只有前七顆、openmp／polly 沒裝且
    `pactree -r` 查無依賴者 → 不收。`pacman -Si mlir` 只命中 andontie-aur（Artix world 系
    根本沒這顆）、`pacman -Si polygeist` 任何啟用庫都查無 → 用戶提的 mlir／polygeist
    不屬於「取代 world-goblins 的 llvm 系」，不收。鏡像側 2026-10-12 重測
    （`curl -sI …/world-goblins/os/x86_64/<檔>`）：`lld-23.1.3-1` 與 `openmp-23.1.3-1`
    仍是 **404**，其餘七顆 200 → 当初開這題的「lld 補不上、-Syu 原子失敗」到現在還在。

  · ⚠️ **裝機順序仍欠（本檔唯一的未做完項）**：本機 **98 個已安裝檔**帶
    `libLLVM.so.23.1`／`libclang-cpp.so.23.1`／`libLLVMSPIRVLib.so.23.1` 的 NEEDED
    （`grep -rlF` 掃 /usr/{lib,bin,libexec}＋/opt，再 `pacman -Qo` 歸戶）。歸戶拆開看
    才是重點：**llvm 45／clang 28／lld 10／lldb 7／llvm-libs 3 共 93 個本來就在被取代的
    七顆裡**（換代一起消失，不是風險）；真正的損壞面只有兩個——
    **mesa-tkg-git 4 個**（`libgallium-26.3.0-devel.so`、`libvulkan_radeon.so`、
    `libvulkan_lvp.so`、`libRusticlOpenCL.so.1.0.0`＝GL/Vulkan 全黑）與
    **doxygen 1 個**（`/usr/bin/doxygen` 要 `libclang-cpp.so.23.1`，trunk 的 SONAME 是
    `.24.0git`）。另發現既有孤檔：`pacman -Qo /usr/lib/libLLVMSPIRVLib.so.23.1` 回
    「沒有軟體包擁有」，而 `libRusticlOpenCL.so` 照樣 NEEDED 它（不是這次造成的）。
    `-Syu` 目前**不會**自動換裝（包名不同、pacman 只按同名升級），但誰裝了 llvm-git 那批，
    GL 就黑——因為 `build-packages.yml:261` 的 mesa-tkg-git job 還是 `pacman -S llvm llvm-libs
    clang`（裝 stable 產物照鏈 `.23.1`）。發包前要做的是把那個 job 改成「先裝我們的
    llvm-libs-git 再編」，並讓它排在 llvm-git 之後（同 job 的 `.llvm-check` 探針本來就在
    比對「容器 llvm soname vs 產物 NEEDED」，改完會自己驗）。doxygen 不在本 feed，
    要嘛也自建、要嘛接受它不能用——**這條要用戶裁**。


---

## NVIDIA -beta 四顆（用戶 2026-10-11 點名全部進本倉，我方追蹤 #170）

⚠️ 先講清楚：**這四顆不是 in-tree 包**，本倉沒有它們的同名目錄，PKGBUILD 一律現取
AUR。列進本檔只因為「拉取对应的套件仓库」那步給它們開了**顯式分支**（按 pkgbase
clone），而那個 step 的說明按本檔開頭的規矩不寫回 workflow。

  · **為什麼要自己出**：Artix 的 world／lib32 與 Arch 的 extra／testing 只有 stable
    那條 nvidia（615.78.08），`nvidia-beta*` 在 Arch 端 API 實測 404、在本機啟用的倉
    裡 `pacman -Si` 也查無 → -beta 分支唯一的來源是 AUR，版號只能追 AUR。
  · **四顆包＝兩個 pkgbase（重要）**：實查 `~/.cache/yay/nvidia-utils-beta/` 的
    PKGBUILD 與 .SRCINFO，`pkgbase=nvidia-utils-beta`、
    `pkgname=('nvidia-utils-beta' 'opencl-nvidia-beta' 'nvidia-settings-beta')`，
    一次 makepkg 產三顆；`nvidia-beta-dkms` 是另一個 pkgbase、只產一顆。
    AUR 的 git 倉**以 pkgbase 命名**，所以矩陣只能有 `nvidia-utils-beta` 與
    `nvidia-beta-dkms` 兩條；拿 `opencl-nvidia-beta`／`nvidia-settings-beta` 去
    clone 會 404（AUR RPC 實查這兩個名字的 `PackageBase` 都是 `nvidia-utils-beta`），
    而且同 pkgbase 並行會打出兩份同版本產物在 repo-add 那裡互相打架。
    收集與 repo-add 都是 `pkg_dir/*.pkg.tar.zst` 的 glob，split 不需要額外接點
    （llvm-git／gstreamer 同形）。
  · **「本機裝的叫 nvidia-settings」是誤讀**：`pacman -Qi nvidia-settings` 是靠那顆的
    `provides = nvidia-settings=615.78.08` 解析過去的，實測 `%NAME%` 欄就是
    `nvidia-settings-beta`（DB 目錄 `/var/lib/pacman/local/nvidia-settings-beta-615.78.08-1`）。
    → 要收的就是 AUR 那顆 `nvidia-settings-beta`，它 `conflicts=('nvidia-settings')`、
    `provides=('nvidia-settings=…')`，裝下去會平順頂掉 world 的 nvidia-settings，
    **不需要**另收 Arch 官方那顆同名包。
  · **版本偵測（pkgver／pkgrel 的切分）**：plan 步用
    `curl 'https://aur.archlinux.org/rpc/?v=5&type=info&arg[]=<包名>'` 取
    `.results[0].Version`，AUR 回的是**含 pkgrel 的整串**（實測 `615.78.08-1`）→
    `TARGET_PKGVER="${_nvver%-*}"`、`TARGET_PKGREL="${_nvver##*-}"`，兩段分別驗形，
    驗不過就 `skip`。手法與 linux-cachyos-cjktty「tag 尾號即 pkgrel」一致。
    整串不拆會拼出 `nvidia-utils-beta-615.78.08-1-1-…` 的資產名，「已在 release 裡」
    永不命中，等於每天白下 530MB＋409MB 重編。這兩顆 PKGBUILD 都**沒有** `pkgver()`，
    所以 plan 尾部「makepkg 會把 pkgrel 重置為 1」那段不生效，AUR 只抬 pkgrel 時
    照樣會重建（這是我們要的行為）。
  · **kind 只能用 `aur`**：`kind: aur` 一次給齊四件事——(1)「拉取」步走 AUR（本輪另開了
    顯式分支，兩邊一致）；(2)「初始化容器環境（Arch／Artix）」把自有 `junlin03-aur` 掛成 pacman
    源（那個條件是 `kind` ∈ kde／wayland／aur，或 repo_name = nashira-git）；(3) 建置帶
    `--skipchecksums --nocheck`，AUR 輔助檔的 sha 過時時不會紅（run #225 實測過那類症狀）；
    (4)「更新校驗和並回推 PKGBUILD」的 giant if 有 `matrix.kind != 'aur'` → 自動不去
    push 不存在的 `Capricornus007/nvidia-utils-beta.git`（會被 push 就索要憑證、CI 無 TTY
    → exit 128）。
    反過來說 `kind: artix` 不能用：它**不在掛源的名單裡**（→ dkms 那顆的
    `nvidia-utils-beta=615.78.08` 解不開）、拿不到 `--skipchecksums`，而且要讓它別回推就
    必須把包名再點名塞進那條很長的 giant if（21000 字元上限的地雷區）。
    註：「artix 容器不能裝 devtools」那條是另一回事——「初始化」的代碼是
    `kind != artix` 才加 devtools（run #356 的教訓），與本組包選 aur 的理由無關。
  · **依賴就緒門檻（本輪補的，不是既有機制）**：`nvidia-beta-dkms` 的 depends 有
    `nvidia-utils-beta=${pkgver}`（**等號硬釘版號**）。本倉 plan 步既有的家族門檻只
    `grep -- '-git$'`，抓不到這條沒有 -git 後綴的兄弟包 → 冷啟動時 `makepkg -s` 會
    `target not found: nvidia-utils-beta` 直接判紅。已在 plan 的這條 case 點名補上
    `pacman -Si nvidia-utils-beta` 沒過就 `skip`，與 KDE／Wayland 家族同一套
    「本輪跳過、靠排程按依賴 DAG 逐層收斂」。
  · **與本倉既有包的關係（實測，不是推測）**：
      - `nvidia-utils-openrc`（本倉 low-freq 線，kind=artix）depends
        `openrc nvidia-utils elogind`。我們這顆 `nvidia-utils-beta` 的
        `provides` 有 `nvidia-utils=615.78.08` → 那條依賴照樣解得開，本機實測
        `pacman -Qi nvidia-utils-beta` 的 Required By 已含 `nvidia-utils-openrc`。
      - 本機 `lib32-nvidia-utils 615.78.08-1`（Artix lib32，packager ndowens）depends
        `nvidia-utils=615.78.08`——**等號**，靠我們的 provides 滿足。
      - `wlroots-git`（本倉 kind=wayland）depends `opengl-driver`，
        `nvidia-utils-beta` 也 provides 它 → 多個提供者，合法，不破洞。
      - `nvidia-settings-beta` depends `nvidia-utils-beta>=615.78.08`、
        `opencl-nvidia-beta` 是 `nvidia-utils-beta` 的 optdepends
        → 三顆同 pkgbase、同一次 build 產出，不會出現「發了半組」。
  · ⚠️ **沒動、留給用戶拍板的三件事**（見交付報告）：
      1. **等號釘依賴的換代窗口**：AUR beta 抬到 616.x 而 Artix 的 `lib32-nvidia-utils`
         仍寫 `nvidia-utils=615.78.08` 時，那顆 32 位包會一時找不到提供者，直到 Artix
         同步抬版。目前兩邊都是 615.78.08，所以是未來風險、不是現況。
      2. **產物是在 Arch 容器裡建的**：`kind: aur` 的容器是 `archlinux:base-devel`
         （不能換 artix 容器：見上條 kind 說明，而且 artix 容器 + kind≠artix 會去裝
         devtools 而恆紅，run #356 實測）。這四顆都是「解包 NVIDIA 官方 .run 再 install」
         、不編譯任何東西，`.PKGINFO` 的 depends 逐字取自 PKGBUILD（實測用戶本機那四顆
         的 `%DEPENDS%` 與 AUR 宣告的內容完全一致、沒有任何 soname 自動探測條目，且
         `nvidia-powerd`/`nvidia-persistenced`/`nvidia-settings` 的 NEEDED 裡沒有
         `libsystemd.so.0`）→ 不會重演 fcitx5「裝完載不到 libsystemd」那種事故。
         這個結論是用「本機 Artix 建出來的實物元數據」推的，CI 第一輪仍要用
         `pacman -Qp` 對產物再核一次 depends 才算坐實。
      3. **`--skipchecksums`**：`kind: aur` 的建置一併帶 `--skipchecksums --nocheck`
         （既有慣例），530MB 的 .run 不在 CI 裡比 sha256。信任錨是 AUR 的 HTTPS git 倉。
         要對這四顆破例（改 in-tree 自己留 PKGBUILD 才能驗 sums）是用戶的決定，沒動。

## librime-git（2026-10-11）

**動機不是「想要尖端」，是被動必須跟**：本機 capnproto-git 換代到 2.0（SONAME
`libcapnp.so.2.0-dev`）之後，world 倉 `librime 1:1.17.0-5.1` 的
`rime-plugins/librime-proto.so` 仍硬連結 `libcapnp.so.1.5.0`。實測全系統
`grep -rl libcapnp.so.1.5.0 /usr/lib/` **只有這一個檔**，後果是 fcitx5 每次啟動都印
`error loading plugin proto: ... 沒有此一檔案或目錄`。capnp 每次換代都要重來一次，
所以放進 feed 讓它自動跟，而不是每次手動救。

**四支補丁（逐支都有實測依據，見 `librime-git/PKGBUILD` 檔頭）**：

1. `cxx20-for-capnp-2.patch` — 上游 `CMakeLists.txt:6` 釘 `CMAKE_CXX_STANDARD 17`，
   而 capnp 2.0 的 `kj/common.h:67` 直接 `#error "This code requires C++20"`。
   抬到 20 這一筆就把 **420 個 error 壓到 12 個**。
2. `opencc-empty-conversion-chain.patch` — 上游 PR #1184（commit 96a55478）給
   `GetConversionChain()` 加了空鏈防護，但 8c5094fa「extract rime::Opencc into
   opencc.h/opencc.cc」把代碼搬走時**防護沒跟著搬**（實測
   `git show HEAD:src/rime/gear/opencc.cc` 搜 `GetConversionChain` 得 3 處、
   搜 `conversions.empty` 得 0 處）。因此**不能再用 cherry-pick**（實測直接衝突），
   改自帶等價補丁，並順手擋掉 `conversions.front()` 在空清單時的未定義行為。
3. `lua-u8string-cxx20.patch` — C++20 起 `path::u8string()` 回 `std::u8string`
   （`char8_t`），與 librime-lua 自己那份 `Opencc(const string&)` 對不上，2 處改 `.string()`。
4. `proto-capnp-2-text-reader.patch` — capnp 2.0 把 `Text::Reader` 換成
   `kj::StringPtr`，不再從 `std::string` 隱式轉換：11 處 setter 加 `.c_str()`、
   1 處讀取改 `cStr()`。

**SOVERSION 已核**：上游 `set(rime_soversion 1)`，產物仍是 `librime.so.1.17.0` +
`librime.so.1`；實測 `/usr/lib/fcitx5/librime.so` 的 `NEEDED` 正是 `librime.so.1`
→ 換成 -git 版不會把 fcitx5-rime 弄斷鏈。哪天上游抬到 2，要連 fcitx5-rime 一起重建。

**已知會紅在 check（不是本包引入）**：master 新增的 `test/simplifier_test.cc`
（d4c324ca，2026-07-03，PR #1191，自註「regression safety net for future OpenCC
upgrades」）有 5 個 `OpenccTest.ConvertWord_*` 失敗，130 通過。已用對照實驗證明
**拿掉本包補丁也一樣失敗**（原版遍歷空清單回 false，行為一致），根因是本機
opencc 1.3.2 而上游最新是 ver.1.4.2 → 解法是抬 opencc（待辦），**不是跳測試**。

## tcl-git / tk-git（用戶 2026-10-12 點名「把 tk 也弄成 -git」）

**為什麼走本倉目錄版**：Artix 的 world 目前停在 `tcl/tk 8.6.16-1`（實測
`pacman -Si` 兩顆都回 8.6.16；`tk` 是 `8.6.16-1.2`），而上游 `core-8-6-branch`
已經到 `core-8-6-18` tag 之後 1634 筆。差的那一段全是 X11 行為修正，
本機拿不到：`db7ddf035`（2026-09-28 X11 `<KeyRelease>` broken）、
`f05357988`（2026-10-04 deiconify 丟掉使用者挪過的位置）、
`7bf995a5e`（2026-10-07 `-zoomed` 被誤還原）、`a7cbed281`（2026-10-09 raise command
在近期 linux 失敗）、`06621cc07`（2026-10-03 grid 的 BadAlloc）。

**分支選 `core-8-6-branch` 而不是 `master`（實測決定，不是猜）**：
`master` 的 `generic/tk.h` 是 `TK_PATCH_LEVEL "8.7a4"`、`tcl/master` 是 `9.0a2`，
裝出來的庫叫 `libtk8.7.so`／`libtcl9.a.so`；而本機
`/usr/lib/python3.14/lib-dynload/_tkinter.cpython-314-x86_64-linux-gnu.so`
的 `NEEDED` 實測是 `libtk8.6.so` + `libtcl8.6.so`。吃 master 那条尖端會把
所有經 `_tkinter` 的程式（pysolfc 就是）打成 ImportError，除非連 python 重編。
`core-8-6-branch` 的 soname 不變 → 是現行套件的**直替**，同時仍是那條線的尖端。

**「8 跟 9 能不能合」**：不能 merge（同一專案的兩個大代，API/soname 不同），
能**並存**：`libtk8.6.so` 與 `libtk8.7.so` 檔名不同、`/usr/lib/tk8.6` 與 `/usr/lib/tk8.7`
目錄不同，會打的只有不帶版本號的 `/usr/bin/wish`、`tclConfig.sh`、`tk.h`、pkgconfig。
要做 9 那条就另建 `tcl9-git`/`tk9-git`，只裝帶版本號的檔、不碰不帶版本那顆
（Fedora 的 tcl9 並存就是這個做法）。本輪先落 8.6 這條能直接換上去的。

**依賴接線**：`tk-git` 依賴 `tcl-git`（不帶版本）。原本想钉成 `tcl-git=$pkgver-$pkgrel` 保證同代，
實測做不到：tcl 與 tk 各自的 commit 流不同步，同一輪探出來的版本一個是 `8.6.18.r767.g476b1c6`、
另一個是 `r1634`，钉版本會讓依賴永遠解析不到。soname 兩邊都是 8.6，差一天也不斷鏈。
`provides=('tcl=<ver>')`／`conflicts=(tcl)` 的可行性已實測：
`pacman -Qi sqlcipher` 與 `pysolfc-git` 的依賴字串都是**不帶版本**的 `tcl`／`tk`，
所以換代不會斷解析。

**check() 的處理（不是抄 Arch 的註解）**：Tcl 的 `make -j1 test` 照 Arch 跑整組；
Tk 的自帶測試要真的 display，Arch 的 PKGBUILD 是把它整行註解掉——
本包不放過這一關，改用 `xvfb-run` 起虛擬屏，讓建出來的 `wish8.6` 真的
`package require Tk`、開 toplevel、設 geometry、查 `TkDefaultFont` 的字型度量，
任一項不對就紅。缺環境就補環境（`makedepends+=xorg-server-xvfb`），不是關掉這一關。

## ccache-git（用戶 2026-10-12 問「那就也換去 -git？」，答：該換）

**為什麼非進 feed 不可（這次是實災，不是偏好）**：world 那顆 `ccache 4.14.1-1`
（建置日 2026-10-05）的 `DT_NEEDED` 釘死 `libhiredis.so.1.3.0`，而系統上的 hiredis
已是 `1.4.1`（實物 `/usr/lib/libhiredis.so.1.4.0`）。實測 `ldd /usr/bin/ccache`
→ `libhiredis.so.1.3.0 => not found`，也就是**從 10-06 起整台機器的 ccache 都是壞的**，
mgx 的原生編譯直接死在
`ccache: error while loading shared libraries: libhiredis.so.1.3.0`。
倉庫端沒有人在 hiredis 換代時重建 ccache ⇒ 這類「依賴換代→二進位靜默失效」只有讓它
每輪跟著 feed 重建才會自動補上，這正是放進本倉的意義。

**版本基線**：讀該 HEAD 自己的 `CMakeLists.txt` 裡 `project(ccache VERSION x.y.z)`，
不是只認 tag（上游常先抬版號再打 tag，只認 tag 會報舊版）。

**收口**：`package()` 最後直接跑一次 `$pkgdir/usr/bin/ccache --version`，
跑不起來就讓建置紅——「套件裝得上但二進位載不起來」不許再活到下一次編譯。
上游現況：最新 release `v4.14.1`（2026-09-27），master 最後一筆 2026-10-10。

---

## lib32-gstreamer-git（用戶 2026-10-12 裁定「務必」換 -git；本輪新增）

用戶機上現況（實測 `/var/lib/pacman/local/`）：`lib32-gstreamer 1.28.1-3`、
`lib32-gst-plugins-base-libs 1.28.1-3`，兩顆同屬 `[lib32]` 的 `pkgbase=lib32-gstreamer`
（packager ndowens@artixlinux.org），而 64 位元那 25 顆早已是本倉 `gstreamer-git`
（尖端 1.29.2.1）。留 32 位元在 1.28.1 就是「一半尖端一半舊版」，Wine／Steam 那類
真的載這批 .so 的軟體吃的正是這一層。

四接點全部已接（缺任何一個就是「裝得上但 feed 不會重建」）：
  1. `build-git-packages.yml` 矩陣：`{"key": "lib32-gstreamer-git", …, "kind": "multilib"}`，
     緊排在 `gstreamer-git` 之後、`lib32-glib2` 之前。註解一律寫在方括號外面
     （寫進 JSON 塊會讓整條矩陣解析失敗，run #436 踩過）。
  2. `build-packages.yml`「拉取对应的套件仓库」的 in-tree `case` 清單：加在這裡，
     不是加在 `逐包修正 AUR 的 PKGBUILD` 那步（那步的 `*)` 是 no-op）。
     不攔就會被通用規則「名字以 -git 結尾 → clone AUR」搶走，而 AUR 沒有這顆、
     `Capricornus007/lib32-gstreamer-git.git` 這個倉也不存在也不需要存在。
     通用 in-tree 分支是用 GitHub contents API 把目錄**全部**檔案抓下來，
     所以同目錄放的 `lib32-gstreamer-git.install` 會自動進建置（本目錄只有
     PKGBUILD 與這一個輔助檔，刻意不帶 0001-HACK 補丁，見下）。
  3. 「更新校驗和並回推 PKGBUILD」的 giant if：**不必**再加包名——該條已有
     `matrix.kind != 'multilib'` 子句（lib32-glib2 那輪加的），我們這顆 kind 就是
     multilib，直接命中排除。實測測得那條 `if:` 表達式現在是 2334 字元，
     離 21000 上限還有 18666。純 git 源跑 updpkgsums 會撕檔（mesa-tkg 的教訓），
     所以這一步對本包必須是跳過。
  4. 本檔（逐包理由寫這裡，不寫回 workflow）。

配方來源：逐字沿用 Arch multilib 打包倉 `lib32-gstreamer` 那份 PKGBUILD
（gitlab.archlinux.org/archlinux/packaging/packages/lib32-gstreamer，407 行、4 顆 split），
只 -git 化。為什麼要 32 位元單獨一份而不是重用 64 位元那顆：lib32 走
`--cross-file lib32` ＋ `--libexecdir lib32`、把 `introspection/doc/devtools/bad/ugly/
ges/libav/python/qt/rtsp/rs/sharp` 全關掉，是**另一套 configure 造型**，
兩側不能共用一個 build 目錄。

本輪只收用戶裝的那兩顆 split（core＋base-libs），上游另兩顆
`lib32-gst-plugins-base`／`lib32-gst-plugins-good` 不收。這帶來一個必須處理乾淨的問題：
`meson install` 的 destdir 裡一定有那兩顆的內容，沒包認領就會「靜默消失在產物外」。
做法是把它們的 78 條外掛 .so（實測 base 7 ＋ good 71，且**只有**外掛 .so，
沒有 lib/pc/bin/include）寫成 `drop=()` 逐檔清單，由 `_drop_siblings()` 記帳後丟掉。
一度想用「凡沒人認領的 `libgst*.so` 就丟」的模式規則，**已否掉**：那會讓
「尖端新增一顆外掛、該歸 base-libs 還是不發的那兩顆」這種事靜默通過。
收口守衛是「root 必須清空否則紅」，與 gstreamer-git 同一條原則
（靜默漏檔是最壞的失敗）。

守衛本身踩到一個**會靜默失效**的坑，記下來：gstreamer-git 的守衛寫在
`package_gstreamer-docs-git()`，那顆沒有 `cd root`，所以用相對路徑 `find root` 沒事；
本包的守衛寫在最後一顆 split 裡，而那個函式已經 `cd root` 了 → 照抄相對路徑會去找
`root/root`，`find` 報「沒有此一檔案或目錄」、`wc -l` 得 0，於是守衛**永遠自稱通過**。
已改成一律用 `$srcdir/root` 絕對路徑，離線測試（見下）也證實紅/綠方向正確。

**不帶 Arch multilib 那份的 0001-HACK-meson-Disable-broken-tests.patch（本輪實測後的決定）**。
理由不是偷懶，是量出來的：拿今天的 `main` 做 sparse 克隆後逐 hunk dry-run，11 個檔案裡
有 **2 处對不上**——`subprojects/gst-plugins-bad/tests/validate/meson.build`（tip 新增了
`{'path': 'h265parse/dsc_sei'}`）與 `subprojects/gst-plugins-base/tests/validate/meson.build`
（tip 新增了 `'videoconvert/to_rgba_f16le'`／`to_rgba_f16be'`），兩處都把 hunk 的尾部上下文
頂掉，直接套用 RC=1。也就是說本倉 gstreamer-git 那份 0001 現在是靠 `git apply -3`
的三方合併在撐，而撐不撐得住取決於克隆裡有沒有那些前置 blob。本包不需要把這個風險
再複製一次：(1) 那顆 patch 只關測試，而本包的 `check()` 不拿測試當門檻，它在這一側
沒有把關價值；(2) patch 觸及的 11 檔裡，gst-editing-services／gst-libav／gst-plugins-bad／
gst-python 那几个在本包造型根本沒建（`-D ges/libav/bad/python=disabled`）。
⚠️ 順帶記下**給 gstreamer-git 那條線的信號**（不属於本輪改動，但這是實測）：那 2 處
上下文漂移同樣會命中 `gstreamer-git/0001-HACK-…patch`，一旦哪天 `-3` 也撐不住，
25 顆包會全紅在 prepare()。要修的是**重繪那顆 patch 對齊今天尖端**，不是關掉測試。

版號與 epoch：不加 epoch。gstreamer-git 那輪的死教訓是「加了 epoch，所有精確等號依賴
就必須連 epoch 一起寫」——`depends` 寫 `gstreamer=$pkgver-$pkgrel`（不含 epoch）而包
自己版本是 `1:…` 時，pacman 精確等號永遠匹配不上、split 互相鎖死。這顆吃尖端 1.29.x
本來就比 [lib32] 的 1.28.1 新，不需要 epoch，也就不製造那個坑。對 64 位元
counterpart（`gstreamer`／`gst-plugins-base-libs`）刻意寫**不帶版本號**的包名：用戶機上
現在是 `-git` 頂掉穩定版、靠 provides 解析；寫不帶版本才同時解得開「已換 -git」與
「還在穩定版」兩種狀態，寫等號就是把其中一邊釘死。

`pkgver()` 是防禦式的（同 librime-git／gstreamer-git）：目錄可能不存在——CI 那步的
updpkgsums 會把 BUILDDIR 換成 mktemp 並在退出時刪掉，接著 `makepkg --printsrcinfo`
仍要跑 `pkgver()`，硬 `cd` 會 fatal 退出 128。
另有一個**只有這顆會踩**的探測坑：plan 步探尖端版號時是 blobless clone 後把一堆
「可能的源碼目錄名」軟鏈到 clone 出來的 repo 再跑 `pkgver()`，那個清單裡有
`${pkgname%-git}`——64 位元那顆展開正好是 `gstreamer`（對得上），本包展開是
`lib32-gstreamer`（對不上）→ `pkgver()` 找不到目錄會退回 PKGBUILD 寫死的佔位 pkgver，
「已在 release 裡」永不命中，等於每 3 小時白編一次。已在 PKGBUILD 用
`_gitrepo=gstreamer` 補上（plan 的軟鏈清單含 `${_gitrepo}` 這一項）。

check() 目前**照上游 multilib 的 `|| :`**（32 位元交叉建置的測試要跑 32 位元二進位，
容器缺的是整套 32 位元執行期，不是某支測試壞了）。這與「不准用跳測試換綠燈」有衝突，
已列入 needs-decision，沒有自行拍成硬失敗；妥協是測試照跑、失敗清單全部印成
`::warning::`，不靜默。
gstreamer-git 那顆專用的「還原 bwrap 權限」步驟（`if: matrix.repo_name == 'gstreamer-git'`）
本包**沒有**跟：它是為了讓 64 位元那邊的 gdk-pixbuf/glycin 沙箱測試能跑，本包的 check
不依賴它。

## spirv-llvm-translator-git（2026-10-12；用戶裁定「那你倒是讓它使用 24 版本編去啊」拉出來的必需包）

### 為什麼會出現這顆
用戶要 mesa 用 LLVM trunk（24）編。本機 `objdump -p` 實測兩條硬證據：

    /usr/lib/libgallium-26.3.0-devel.so   NEEDED libLLVM.so.23.1
    /usr/lib/libRusticlOpenCL.so.1.0.0    NEEDED libLLVM.so.23.1
                                        + NEEDED libLLVMSPIRVLib.so.23.1

第二行就是關鍵：RustiCL（mesa 的 OpenCL 實作）**直接**依賴 SPIRV-LLVM-Translator，
而这顆庫本身是配 LLVM 23.1 編的。換 LLVM 不換它，產物會同時拖 `libLLVM.so.24.0git`
與 `libLLVM.so.23.1` 兩個 soname —— 裝下去是 OpenCL 靜默失效或直接崩。用戶規則禁止
「關掉 RustiCL 換綠燈」，所以唯一出路是把 translator 一起抬到 trunk。

### 為什麼是 -git 而不是抬版（查證過程，不是推測）
    git ls-remote --tags --refs https://github.com/KhronosGroup/SPIRV-LLVM-Translator
      → 最新只有 v23.1.2（v22.1.x 一串在前，sort -V 後末三筆是 v23.1.0/v23.1.1/v23.1.2）
    git ls-remote --heads 同一倉
      → 分支只到 llvm_release_230，**沒有 llvm_release_240**；HEAD 的 symref 是 main

也就是上游的 tag／release 分支恆與「**已發布的最大 LLVM**」配對，而 LLVM 24 目前只有
trunk（`cmake/Modules/LLVMVersion.cmake` 實查 MAJOR=24 MINOR=0 PATCH=0 SUFFIX=git，
本倉 llvm-*-git 產物的 SONAME 是 `libLLVM.so.24.0git`）。所以「跟最新版本」這條路
不存在，只能吃 `main`（那條才是配 LLVM tip 開發的分支）。

### 目標機的另一個既存問題（這顆包順手治掉）
`pacman -Qo /usr/lib/libLLVMSPIRVLib.so.23.1` 回「沒有軟體包擁有它」，
而 `pacman -Qs spirv` 查實這臺只裝了 spirv-tools、**根本沒裝 spirv-llvm-translator**。
=> 這臺的 RustiCL OpenCL 一直靠一顆沒主人管的歷史残留库在跑：換代時不會被移除、
   也不會被更新，正是「CI 全綠但產物是壞的」那一類。本包進 feed 後該路徑由包擁有。

### ABI 鎖（這顆包存在的另一半意義）
`package()` 裡不寫死版本，而是從「建它時容器裡那顆 `/usr/lib/libLLVM.so` 的 SONAME」
反推依賴：`depends+=("llvm-libs-git" "llvm-libs-abi=<soname>")`，那顆虛擬名由本倉
`llvm-libs-git` 的 `package_llvm-libs-git()` 现场发放（`llvm-libs-abi=24.0git`）。

⚠️ 為什麼不用官方那形 `libLLVM.so=23.1-64` 來钉：本輪實測 **makepkg 7.1 直接拒**——
      `==> 錯誤： pkgver in depends 不能有 ; 斜線、- 連字號或空白`；而把 world.db 全倉
      `%DEPENDS%` 拆開查實**沒有一筆**帶 `-64`（`bsdtar -xf world.db` 後 grep 統計 = 0），
      那種形只出現在 `%PROVIDES%`。所以自製一個不含連字號的虛擬名，provides／depends
      兩邊都合法，而且只在 soname 相同時成立。教訓來源是 2026-10-12 那次 GL 黑屏：
CI 產出的 mesa 依賴只有 `llvm-libs>=8.0.0`（無上限）、而 makepkg 7.1 **不會**替 Mesa
自動抽 soname 依賴（拆產物 .PKGINFO 查實），於是 llvm 換代後 pacman 認為依賴仍滿足、
實物找不到 `libLLVM.so.23.1`，直接 `libGL error: failed to find suitable GL configuration`。

### 四接點
  1. `build-git-packages.yml` 矩陣：`{"key": "spirv-llvm-translator-git", …}`，排在
     `tk-git` 之後。不帶 `kind`（帶 kind=aur 會被 `--nocheck --skipchecksums` 命中，
     而用戶裁定「補環境、不跳測試」）。
  2. `build-packages.yml`「拉取对应的套件仓库」的通用 in-tree `case` 清單（那串
     `|librime-git|tcl-git|tk-git|ccache-git|spirv-llvm-translator-git)`）。不加就會被
     通用規則「名字以 -git 結尾 → clone AUR」搶走，AUR 那顆是配穩定 LLVM 的舊配方。
  3. 「更新校验和并回推 PKGBUILD」的 giant if：加了 `matrix.repo_name != 'spirv-llvm-translator-git'`
     （本包無 kind 可擋，必須点名；純 git 源跑 updpkgsums 會撕檔）。
  4. 本檔。

### 與 mesa job 的順序關係（跨 workflow，不能用 needs: 串）
`build-packages.yml` 新增一步「把容器 LLVM 換成自有 llvm-*-git 尖端（mesa 與 SPIRV
translator 共用）」：先從 release `current-repo` 抓自有 llvm 七顆（mesa 那邊再加抓
自有 translator），`pacman -U` 頂替 goblins 的穩定版，然後才 makepkg。兩邊都靠「抓
上一輪已發布的產物」銜接，所以**translator 落地的第一輪 mesa 仍可能紅**——紅是正確的
（mesa 的 soname 守門步會點名混版），下一輪兩邊就對齊了。守門步本輪同時修掉兩個既存
bug：① 舊正則 `libLLVM\.so\.[0-9][0-9.]*` 抓 `libLLVM.so.24.0git` 會截到 `24.0` 就停
（`g` 不在字元類裡），換代上 trunk 之後必然**假紅**；② 舊版把 64 與 32 位元產物倒進
同一目錄混著比，現在按包名分流各比各的 soname。

### ~~lib32 那半邊不動的理由~~（2026-10-13 作廢，見下面「lib32-llvm-git」）
本節原文寫「32 位元 trunk LLVM 全網路沒有人產，所以 lib32-mesa 繼續配 23.1」。
**這句話被用戶 2026-10-13 直接否決**：「llvm 並不止這些吧？clang 啊 rt 啥的呢？」＋
「你倒是也去建 32 位的啊？」——「沒人產」不是「我們不產」的理由，本倉就是那個人。
保留原文只為了留痕：真正的做法改看下一節。

## lib32-llvm-git（2026-10-13；用戶點名補上的 32 位元整條鏈）

### 「32 位元到底該有幾顆」是查出來的，不是印象
解開兩個 32 位元倉的 DB 逐條點名（`/var/lib/pacman/sync/{multilib,lib32}.files`）：

    lib32-clang  lib32-llvm  lib32-llvm-libs  lib32-spirv-llvm-translator  lib32-spirv-tools

只有這四顆 LLVM 系的（spirv-tools 不鏈 LLVM，另論）。**沒有** `lib32-lld`、
**沒有** `lib32-lldb`、**沒有** `lib32-compiler-rt`——lld／lldb 是宿主工具，32 位元
連結是 64 位元 lld 加 `-m32` 做的，所以那兩顆不該憑空發明。
而「rt 呢？」的答案不在 32 位元倉，在**同一顆 compiler-rt 裡**：查實
`extra` 與 `world-goblins` 的 compiler-rt 都帶 `libclang_rt.asan-i386.a`／
`clang_rt.crtbegin-i386.o`，而本機實裝的自有 `compiler-rt-git`
`pacman -Ql | grep -c i386` 回 **0** —— 因為我開了
`-DCOMPILER_RT_DEFAULT_TARGET_ONLY=ON`（只建預設 target）。本輪拿掉它、
makedepends 補 `lib32-gcc-libs`（Arch 在 llvm.PKGBUILD:17-18 同一件事，註解寫
“Build 32-bit compiler-rt libraries on x86_64 (FS#41911)”），並在
`package_compiler-rt-git()` 加第二道「找不到 `*i386*` 就紅」。

### 參數照官方兩份，不是自己發明的交叉編譯
存進 `docs/upstream-pkgbuilds/lib32-llvm.PKGBUILD` 與 `lib32-clang.PKGBUILD`
（gitlab.archlinux.org/archlinux/packaging/packages/{lib32-llvm,lib32-clang}）。
關鍵三條：`-m32` 進 CFLAGS/CXXFLAGS/LDFLAGS、`-DLLVM_LIBDIR_SUFFIX=32`（裝到
/usr/lib32）、`-DLLVM_TARGET_ARCH=i686 -DLLVM_DEFAULT_TARGET_TRIPLE=i686-pc-linux-gnu
-DLLVM_HOST_TRIPLE=x86_64-pc-linux-gnu`。

### 與官方的一處結構性差異（故意的）
官方把 llvm 與 clang 拆成兩個 package base，因為 lib32-clang 的 cmake 要吃
`llvm-config32`，而那支程式是 lib32-llvm 的產物（先有雞先有蛋，只能靠倉庫分兩輪）。
本倉一次 configure 就開 `LLVM_ENABLE_PROJECTS=clang`（與 64 位元那顆同一手法），
同一棵 build 樹裡 clang 直接吃 tree 裡的 llvm → 32 位元一輪出三顆。
代價：多建了官方用 `LLVM_DISTRIBUTION_COMPONENTS` 裁掉的靜態庫與工具，
所以 `package_lib32-llvm-git()` 結尾照官方範圍（lib32-llvm.PKGBUILD:126-127）
丟掉 include／share／其他 bin，**並把丟棄數量印出來**，不留靜默 rm。

### 三顆各自收什麼（實物清單為準）
- `lib32-llvm-libs-git`：`/usr/lib32/libLLVM.so*`、`libLTO`、`libRemarks`、
  `LLVMgold.so`，另**自己建** `usr/lib32/bfd-plugins/LLVMgold.so` 那條相對符號連結
  （官方也是自己 `ln -s ../LLVMgold.so`）。缺任何一個就紅。
- `lib32-clang-git`：`libclang.so*` ＋ `libclang-cpp.so*` ＋ `clang/*/include`
  （⚠️ `libclang-cpp.so*` 在 32 位元歸**這顆**，64 位元那邊歸 llvm-libs-git——
  兩邊官方歸屬本來就不同，照抄別自己統一）。
- `lib32-llvm-git`：`/usr/lib32/cmake/{llvm,clang}` ＋ `llvm-config32`。
  `llvm-config` 是**改名**來的（官方同款 `mv llvm-config{,32}`），因為 64 位元那支
  已佔 `/usr/bin/llvm-config`。自證用三個**實測存在**的值：`--libdir` 尾段 `/usr/lib32`、
  `--host-target` = `i686-pc-linux-gnu`、以及直接讀 ELF 檔頭第 5 元組 `EI_CLASS=1`（ELF32）。
  ⚠️ 記一笔教訓：這裡原先寫的是比 `--target-target`，**那個選項不存在**（llvm-config 的
  target 類只有 `--host-target`／`--targets-built`），傳錯選項它印 usage 並回非 0，
  變數恆空 → 把好的產物判成 FATAL（本機 /tmp/l32 那輪 `makepkg RC=1` 就是這樣來的，
  交叉參數其實是生效的）。位元寬度之所以改用 `od` 讀檔頭而不是 `file`／`readelf`：
  那兩支在本機位於 `/usr/sbin/`，builder 的 PATH 不一定含 `/usr/sbin`，拿空字串比對
  等於做一道永遠紅或永遠綠的假檢查。

### ABI 虛擬名為什麼必須是另一個名字
32 位元發的是 `lib32-llvm-libs-abi=<soname>`，**不共用** 64 位元的 `llvm-libs-abi`。
理由：pacman 判依賴只看名字，共用同一個虛擬名的話，64 位元 mesa 的依賴會被 32 位元
那顆 satisfy 掉，實物卻找不到 `/usr/lib/libLLVM.so.24.0git` → 又黑屏一次。

### 誰吃它
- `spirv-llvm-translator-git` 本輪多切一顆 `lib32-spirv-llvm-translator-git`
  （`provides=lib32-spirv-llvm-translator`，mesa 的 lib32 makedepends 點名的就是這個名字），
  第二棵 `build32` 用 `-m32 + LLVM_CONFIG=llvm-config32 + LLVM_LIBDIR_SUFFIX=32`，
  結尾用 `objdump -p` 驗它的 NEEDED 真是 `libLLVM.so.<abi>`、且與依賴鎖一致。
- `mesa-tkg-git` 的 CI 步：自有 lib32 四顆齊 → 改寫 `_lib32_llvm` 成 ABI 鎖並建兩半邊；
  不齊 → **本輪不建 32 位元**（`_lib32=false`）並印 `::warning::` 點名缺哪幾顆。
  刻意不允許「缺就退回用穩定版 lib32 繼續建」：那會發出 64 位元鎖 24、32 位元鏈 23.1
  而兩邊依賴都「滿足」的包。
- 產物端也驗：mesa 的 soname 守門步現在除了 64 位元的 `llvm-libs-abi=`，
  若這輪真有 `lib32-mesa-tkg-git-*.pkg.tar.zst`，也要求它的 `.PKGINFO` 帶
  `lib32-llvm-libs-abi=<容器 soname>`，否則紅。

### 四接點
1. `build-git-packages.yml` 矩陣：`{"key": "lib32-llvm-git", ..., "kind": "multilib"}`
   （`kind: multilib` 才會開 [multilib] 並預裝 lib32 底層鏈）。
2. `build-packages.yml` 的 in-tree case 清單：加 `lib32-llvm-git`。
3. 「更新校验和并回推 PKGBUILD」的 giant if：加 `matrix.repo_name != 'lib32-llvm-git'`
   （純 git 源，updpkgsums 會撕檔）。
4. 本檔。

## spirv-headers-git（2026-10-13；用戶裁定「那讓這個也走源碼直出不就也行了？」）

### 為什麼有意義（查實，不是「看起來比較新」）
`git ls-remote` 實測 `refs/heads/main = 86f980c731e6…` 而最新 tag
`refs/tags/vulkan-sdk-1.4.363.0 = 496543121ce6…` —— **不同 sha**，也就是最新 tag 之後
main 上還有未發佈提交（本機 makepkg 算出 `1.4.363.0.r6.g86f980c731e` ⇒ 6 筆）。
translator 那條鏈吃的是 LLVM trunk＋translator main，新 SPIR-V 能力通常先落 headers main，
標頭釘在 tag 就會出現「translator 有實作、標頭沒這個 enum」的錯位。

### 風險面先量過才動手
`pacman -Sii spirv-headers` 實測 `Required By: None`：這顆是 header-only（`arch=(any)`），
只有 spirv-tools／translator／mesa 在**建置期**吃標頭，執行期不鏈 → 換 -git 不會把
32/64 位元的執行期鏈拉進風險區。官方 `extra` 那顆是 `1:1.4.363.0-1`（**epoch 1**），
所以本檔也必須 `epoch=1`，否則 vercmp 判我們比較舊、這顆永遠裝不上去。

### 本地實跑過（不是只有 lint）
`makepkg -sf` 於 2026-10-13 12:58 產出
`spirv-headers-git-1:1.4.363.0.r6.g86f980c731e-1-any.pkg.tar.zst`。
過程中翻掉兩個我自己寫錯的地方，都留成檔裡的硬檢查：
① 我憑印象把 `usr/include/spirv/include.json` 列進「必含」，被自己的檢查擋紅——
   實物是 `usr/include/spirv/{1.0,1.1,1.2,unified1}` ＋ `spir-v.xml`（88 個檔），
   registry JSON 不屬於這個倉；
② 官方 `check()` 那條 `ctest --test-dir build` 在我們容器裡回
   `No tests were found!!!`（上游根本沒產生 `build/CTestTestfile.cmake`）——
   真正的檢查是 build 階段那三支柱 `spirv_headers_simple_test{,_c,_cpp11}`
   （拿標頭實際編 C／C++98／C++11）。所以 `check()` 改成「三支柱必須在、並各跑一次」，
   而不是留一條跑空卻看起來像驗過的 ctest。

### 四接點
1. `build-git-packages.yml` 矩陣：`{"key": "spirv-headers-git", "variant": "none"}`（無 kind）。
2. `build-packages.yml` in-tree case 清單 ＋ updpkgsums giant if 各加一顆。
3. `spirv-llvm-translator-git` 的 makedepends 從 `spirv-headers` 改成 `spirv-headers-git`，
   且 CI 那步「查不到這顆就紅」——不退回去吃 extra 的 tag 版。
4. 本檔。

### 那兩條 lit 紅是自己查、自己修的（用戶 2026-10-13「你自己修不好？確定自己修不好？」）
CI 上 translator 的 1156 條 lit 有兩條紅：`DebugInfo/Generic/debug-info-eis-option.ll`
與 `linear-dbg-value.ll`，報 `*** Bad machine code: Using an undefined physical register ***`
（`JCC_1 %bb.2, 5, implicit $eflags`）→ `LLVM ERROR: Found 1 machine code errors.`。
本機用已裝的 trunk 端到端重現（`llvm-as → llvm-spirv → llvm-spirv -r → llvm-dis → llc`），
查到的不是「LLVM 的排程器 bug 等上游修」，而是**我們測試檔少帶了上游自己的規避旗標**：

- 這兩個檔案是 LLVM 自己 `DebugInfo` 測試的副本，而**上游那份頂部寫著**
  `; FIXME: Fix machine verifier issues and remove -verify-machineinstrs=0 and`
  `; -disable-mir-output-verify. PR39452.`——也就是「在 `-stop-before=finalize-isel`
  這個切點停下來時，X86 還沒把 flag 的 def/use 收尾，machine verifier 本來就會抱怨」，
  上游對這個檔**自己就把 verifier 關了**。translator 的副本在 fork 時把那兩個旗標弄丟了。
- 對照實測（同一支 `llc`、同一份 round-trip 出来的 IR）：不帶旗標 → abort；
  帶旗標 → **FileCheck 通過**。所以這**不是跳測試**：測試真正要驗的東西
  （`bb.2.for.body` 裡那個變數的 `DBG_VALUE` 位置、EIS-option 的 debug value）照樣跑，
  關掉的只是「在这个阶段本来就不该跑」的那個 verifier。
- 落地方式（**2026-10-13 已改**）：原本是本目錄帶一顆
  `llvm24-pre-ra-sched-verifier-flags.patch` 進 `source=()`＋b2sums，`prepare()` 先
  `--dry-run` 再套、套不上就紅。**現在補丁已刪**，因為上游收了同一個修法：
  issue `KhronosGroup/SPIRV-LLVM-Translator#4082`（我方 2026-10-13 提）於 09:37Z 以
  COMPLETED 關閉，對應 commit `fc137e9fb`「Disable MI verification in 2 tests after
  llvm changes」(#4083)，改的正是 `test/DebugInfo/Generic/{linear-dbg-value,debug-info-eis-option}.ll`
  那兩條 RUN 行、旗標一致。→ 這是規則 61「跟隨上游＝連上游自己的 Remove/Delete 一起跟」的
  實際案例：上游把它變成來源的一部分，我方補丁就該消失，不是留著當保險。
  但**沒有刪了事**：`prepare()` 換成正向斷言，逐檔數 `-verify-machineinstrs=0`，
  命中總數 < 2 就紅並指示去查 `fc137e9fb` 之後的變動。實測對上游 main 現況：
  兩檔各命中 1 處、n=2，斷言通過。

## doxygen-git（2026-10-13；用戶「你加就是了？」＋「順帶記得給我裝上」）

### 為什麼必須有這顆（不是「也想 -git」，是穩定版已經壞了）
本倉 `llvm-*-git` 換到 trunk 之後，機上那顆 `doxygen 1.18.0-2` 實測起不來：

    ldd /usr/bin/doxygen
      libclang.so.23.1 => not found
      libclang-cpp.so.23.1 => not found

doxygen 是 `use_libclang=ON` 建的（Arch 同款），執行期載入 libclang；它 NEEDED 的是
**寫死帶版本**的 `.so.23.1`，而我們的 `clang-git` 發的是 `clang=24.0.0` 與無版本的
`libclang.so`／`libclang-cpp.so` 虛擬名，satisfy 不到那條 NEEDED。
→ 唯一正解是「用 24 重建 doxygen」，不是再塞一顆 23.1 橋接檔（那正是 10-12 GL 黑屏的
同款做法與同款下場：裝得上、一換代就靜默炸）。

### 收錄範圍是先查過的，沒有連坐
- `pactree -r doxygen` 實測只有它自己（沒有任何已裝包依賴它）。
- `pacman -Q doxygen-docs` 未裝 → **不做 docs 分割**，`build()` 用 `-Dbuild_doc=OFF`
  明確關掉。理由寫進 PKGBUILD：官方那條 `--target docs` 需要先有一支 doxygen 才能生成
  自己的文件（自我依賴循環），把它列進 makedepends 會繞成死結；既然本機沒有這半邊需求，
  就老實關掉，而不是「假裝建了、產物裡沒有」。
- `provides=('doxygen=<基號>')` ＋ `conflicts/replaces=(doxygen)`：頂替的是**安裝用的名字**
  `doxygen`（不是 `doxygen-git`），這條是 sway-git 那次學到的（`conflicts` 要寫包名）。

### 產物端自證（不認 build 綠、只認實物）
`package_doxygen-git()` 會 `objdump -p` 問 `/usr/bin/doxygen` 的 NEEDED，要求裡面真的有
`libclang-cpp.so.<容器此刻的 LLVM soname>`；查不到 soname、或 NEEDED 不是那一版，直接紅。
動機就是本輪這句話：**「CI 全綠、包也裝上了，但 NEEDED 指向一個不存在的 soname」**。

### 四接點
1. `build-git-packages.yml` 矩陣：`{"key": "doxygen-git", "variant": "none"}`（無 kind）。
2. `build-packages.yml` in-tree case 清單加 `doxygen-git`；updpkgsums 的 giant if 也點名排除
   （純 git 源，跑 updpkgsums 會撕檔）。
3. 掛 `junlin03-aur` 源的清單加 `doxygen-git`，並把它加進「把容器 LLVM 換成自有 llvm-*-git」
   那步的 `if`——**這顆必須建在自有 clang 上**，否則又發出一顆鏈 23.1 的 doxygen。
4. 本檔。

---

## 21000 上限的**精確語意**（2026-10-13 用 GitHub 的錯誤訊息反推出來，不再是猜）

本檔開頭與 build-kernels.yml:67 都寫過「那個 step 有 21000 字元的表達式上限、註解也
計入」，但**語意一直不準**，結果今天照舊踩雷。實測定義是：

* 單位是 **位元組不是字元**：繁中 1 字＝3 bytes，所以中文註解吃額度是英文的三倍。
* 適用對象是**任何含 `${{ }}` 的字串值**（`run:` 區塊、`if:`、`container.image` 都算），
  不限某一條 giant if。
* **不含表達式的字串不受這條限制**——同一 job 裡「检测目标版本并决定是否需要
  构建」那步 52249 bytes 照跑，因為它一個 `${{ }}` 都沒有。
* 反過來也成立：**shell 註解裡出現 `${{ }}` 這種空表達式，GitHub 照樣解析並判整條
  workflow 无效**（實測就在本輪：拆步那段註解寫了「含 \`\${{ }}\` 表達式的 step」，
  dispatch 回 `(Line: 250, Col: 14): An expression was expected`）。要引用這個記法就寫
  「dollar-brace」四個字，別把記法本身放進 run 區塊。
* 踩過的後果**不是該 job 紅，是整個 workflow 解析失敗、一個 job 都不起**，而且
  REST 查不到任何線索：run 的 `name` 直接顯示成檔案路徑、`jobs=0`、annotations 404、
  logs 404。今天（f5aa969）與 2026-10-09（e24262b）兩次都是這樣，當時都誤判成
  「heredoc 縮排炸掉」與「不明 transient」——**PyYAML 與 actionlint 全綠也不代表
  GitHub 收得到**。
* 唯一直接把話說清楚的管道是讓 GitHub 自己 parse：
  `gh workflow run <檔名> --ref <branch>` 無效時回
  `HTTP 422: failed to parse workflow: ... (Line: 49, Col: 14): Exceeded max
  expression length 21000`。這招**不消耗建置額度**（解析階段就擋掉），所以改
  workflow 後拿它當驗收入口最省。

守門工具：`scripts/workflow-step-budget.py`（本檔同輪新增）。改任何 workflow 前後各跑
一次：`python3 scripts/workflow-step-budget.py`。它管四件事——模板字串 ≥21000 bytes 紅、
≥19000 黃標（先知道快撞牆）、空表達式紅、表達式沒閉合紅。自我驗證做過兩個壞樣本：
f5aa969 那份印 `RED ... 模板字串 21147 bytes（上限 21000）`、`${{ }}` 註解樣本印
`RED ... 有空表達式`，兩者都 exit 0 之外的 1；修好版 exit 0。
（「沒閉合」不能靠比對 `${{` 與 `}}` 的總數——shell／awk 裡本來就有一堆單獨的 `}}`，
腳本第一版這樣寫，直接把 build-packages.yml 誤報兩條紅，已改成逐個 `${{` 往後找。）

修法不是「把註解刪一刪」——那樣只是把同一顆雷往後挪。今天是把「初始化容器環境（Arch／Artix）
环境」那步（21147 bytes）**從 tkg 區塊前拆成兩步**：拆後 11373／10796，兩邊都留
一倍以上餘裕。拆步安全的兩個前提已逐個核對：跨 step 只共享**檔案系統**
（/etc/pacman.conf、/etc/makepkg.conf、builder 使用者、git 全域設定都留得住），
**不共享 shell 變數**——前半段的 `_init_pkgs`／`_pi`／`cache_file` 不出現在後半段，
後半段的 `_r`／`synced`／`_try` 都在自己裡面定義。

## spirv-llvm-translator-git 也要 [multilib]（從 workflow 搬進本檔）

它現在多切一顆 `lib32-spirv-llvm-translator-git`，makedepends 點名
`lib32-spirv-tools`／`lib32-gcc-libs`，而 Artix/Arch 容器的 `[multilib]` 預設是
**註解掉的**，所以 build-packages.yml 那條 `if` 除了 `matrix.kind = multilib` 之外，
還得把包名點名進去（run #471 實測 `error: target not found: lib32-spirv-tools`）。
不跟 `kind:tkg` 共用分支的理由與 lib32 那半邊不動的取捨，見上面「lib32-llvm-git」那節。

## opencc-git（任務 #181，2026-10-13）

**為什麼存在**：本機 opencc 是 Artix world 的 `1.3.2-1`，上游最新發布 `ver.1.4.2`
（2026-08-22）、master 尖端更晚。librime master 那 5 個 OpenccTest 失敗吃的就是這個版本差，
而 world 那顆永遠不會自己動。用戶的常規指令是「全部轉源碼直出、追最新尖端」，所以自建 -git。

**四接點**：
1. 目錄 `opencc-git/PKGBUILD`（源只有 `git+…/BYVoid/OpenCC#branch=master` 一條，
   版號與校驗和都由 `pkgver()` 現算）。
2. `build-git-packages.yml` 矩陣：排在 `librime-git` 之後（同一個輸入法家族，先讀好懂）。
   ⚠️ 沒帶 `kind`，所以它會跑 `check()`（用戶裁定「補環境、不跳測試」）。
3. `build-packages.yml`「拉取对应的套件仓库」的 in-tree `case`：加了 `|opencc-git`。
   不加會被通用規則「名字以 `-git` 結尾 → clone AUR」搶走。
4. 「更新校验和并回推 PKGBUILD」那條 giant `if`：加了 `matrix.repo_name != 'opencc-git'`。
   純 git 源的包不該讓 updpkgsums 去撕檔（mesa-tkg 的教訓），而且它也不該被推去
   `Capricornus007/opencc-git.git` 那個不存在的倉。

**⚠️ 換代是跨 soname 的，裝機必須與 librime-git 同一筆交易**：實測本機
`/usr/lib/libopencc.so → .so.1.3 → .so.1.3.2`，而上游 `CMakeLists.txt` 是
`set(OPENCC_ABI_VERSION 1.4)`；本地建出來的產物實測為 `libopencc.so.1.4`／`.so.1.4.2`。
全系統掃「NEEDED libopencc.so.1.3」命中 8 個檔，其中 jieba 插件、CLI、python 綁定都出自本包
（重建即一致），**外部只剩 `librime.so.1.17.0` 與 `rime-plugins/librime-lua.so`** →
它們由本倉 `librime-git` 提供。所以順序是：opencc-git 先進 feed → 下一輪把 librime-git 的
`epoch` 抬一檔讓它重編 → 兩顆一起裝。只換一邊會讓輸入法直接起不來。

**本地實建抓到的兩個真錯（這就是「先照 CI 定義本地跑一遍」的價值，CI 上紅一次要等兩小時）**：
1. `prepare()` 裡的 `rm -r deps/!(darts-clone-0.32h)` 需要 `shopt -s extglob` 在**檔案頂層**；
   放在函式內部太慢——makepkg 是先 source 整份 PKGBUILD，函式定義時就要能解析那個 glob，
   實測 `rc=6：未預期的字組「(」附近有語法錯誤`。
2. `_license` 不是全域函式，是 `llvm-git/PKGBUILD` 自己檔內定義的小工具（第 336 行），
   別的包照抄會 `command not found`。opencc 這裡改成直接 `install -Dm644 LICENSE`。

**產物驗收**（本地 `makepkg -s` 實測）：`opencc-git 1.4.2.r18.g8cf737a4e19-1`、
上游自測 **20/20 通過**（`JiebaPluginIntegrationTest` 依官方同款排除——它斷言的是上游自帶
詞典的輸出，我們改用系統 `cppjieba` 詞典）、144 個檔 11 MB、
`provides=(opencc=1.4.2, libopencc.so)`、`conflicts/replaces=(opencc)`。

## tty-solitaire-git（2026-10-13；用戶回報「同一張牌留在兩個位置」）

原本這顆是 `kind: aur`（AUR 上 fredbezies 維護的 `tty-solitaire-git`）。轉 in-tree 的唯一理由是
**AUR-kind 沒辦法帶我方補丁**，而用戶看到的現象（左上角 stock 那格壓著一張正面 2♣，
同一張 2♣ 同時是第 4 欄那條 `K♥ Q♠ J♦ 10♣ 9♥ 8♣ 7♥ 6♣ 5♦ 4♠ 3♦ 2♣` 合法遞減串的底牌）
需要動到繪圖路徑才能修。

補丁 `ghost-card-repaint.patch`（43 行、2 檔）內容：
1. `gui.c:125` 的 `erase_card()` 少包 `COLOR_PAIR()`：`wbkgd(win, WHITE_ON_GREEN)` 而
   `gui.h:14` 的 `WHITE_ON_GREEN` 只是數字 6 → 背景被設成 pair 0（終端預設色）而不是綠桌布。
   獨立小程序實測兩種寫法發出的終端序列：`wbkgd(w,6)` → `ESC[39;49m`；
   `wbkgd(w,COLOR_PAIR(6))` → `ESC[37m ESC[42m`。
2. `keyboard.c` 的「自動送上基座」迴圈把 `destination` 當迴圈變數**無條件覆寫**：四格基座
   都不接受時它仍停在 `foundation[3]`，而後面只重畫 `*origin` 與 `*destination` →
   **真正動過的格子沒人重畫**，這才是殘影最可能的來源。改成只用區域變數，且只在真的
   有牌進去時才重畫那一疊。

⚠️ **尚未重現用戶現象**，所以這是「修掉兩處可證明的缺陷」，不是「已驗證治好」：
pyte 亂玩 24 seed（`m/M/n/N/空白/方向鍵`）與加「移牌中途改尺寸」8 seed 都是零觸發；
而第 1 點的 A/B（抽乾牌堆 30 次後數上排格子的背景）兩版**輸出相同**（green=0/default=5），
理由是那條路上 `erase_stack` 緊接著就有 `draw_stack`，錯色在同一次 refresh 內被蓋掉——
也就是說第 1 點是**潛在**缺陷、不是可見成因。第 2 點仍是用戶症狀最合理的解釋。

保留 AUR 那份的結構（`_name`、`pkgver()` 的 `cut -c2-48`、`epoch=1`、`conflicts/replaces`），
只加 `prepare()`，且**套不上就紅**（上游若自己修掉這兩處，要人來核對、不靜默退化）。

## spirv-tools-git（2026-10-14；用戶裁定第 1 條走 A「補環境、不跳測試」）
`spirv-llvm-translator-git` 的 check() 有 4 條 lit 紅，根因不在 translator：上游 877ae7ab
（PR #4081，10-13）才在這些測試的 RUN 裡加了 `spirv-val`，而 distro 那顆 SPIRV-Tools 停在
tag `vulkan-sdk-1.4.363.0`(ef96ed76，09-10)；三個 validator 誤報與一個 spirv-val 自身
`std::out_of_range` abort 都已在上游 main 修掉（PR #6946=`2a7f2309`、PR #6943=`47ed79f5`，
10-11），**但沒有任何已發布 tag 含這些修復**。上游 CI 綠是因為它每天從 main 自建 SPIRV-Tools。
⇒ 正解＝這顆也走源碼直出，並讓 translator 的 depends 點名 `spirv-tools-git`（寫 `spirv-tools`
會被 distro 同名包 satisfy，等於沒補環境）。
- 接點：矩陣 `{"key":"spirv-tools-git","variant":"none"}`；`build-packages.yml` 的 in-tree
  攔截分支；回推校驗和 giant if 加 `!= 'spirv-tools-git'`。
- **不需要專屬 TARGET_PKGVER case**：`source` 前綴寫成 `spirv-tools::`（＝`${pkgname%-git}`），
  通用探測克隆的目錄名與 `pkgver()` 的 `cd` 目標一致（xorg-xwayland-git 同款做法）。
- epoch：**4**（不是跟官方對齊的 1）。AUR 那顆 `spirv-tools-git` 是 `epoch=3`／`pkgver="2024.1".3932.fe7bae090`，
  且 930 天沒動；yay/topgrade 是拿「已安裝 vs AUR」比版本 ⇒ epoch 1 會被判比較舊，用戶端永遠掛著
  「AUR 有新版本」並以 `make dependency of spirv-llvm-translator-git` 的身分把舊包裝回去
  （2026-10-15 實物輸出與 AUR PKGBUILD 都查過）。取 4 一次壓過 AUR(3) 與官方(1)。
  `provides=('spirv-tools=<基號>' 'spirv-tools-libs')`＋conflicts/replaces 同名。
- ⚠️ 裝機影響：`pactree -r spirv-tools` 實測依賴鏈是 glslang → libplacebo →
  ffmpeg-full-git → mpv／librewolf／opencv／gst-libav-git。執行期鏈的是**無版本後綴**的
  `libSPIRV-Tools*.so`，trunk 不改 soname 就不斷鏈；換代改變的是 validator 行為（影響建置期）。
  裝完的 smoke test：`vulkaninfo` 之類＋跑一段 mpv。

## 2026-10-15：四顆紅的根因與修法（同一種病：裸名／死碼／硬釘）

run `38511938671`（164 成功 / 4 紅）逐顆查實後，四個紅其實是三種同源病灶。

### 病灶一：**裸名依賴會被 [extra] 的同名實包搶走**（成立於 pacman 的解析語義）
pacman 對「倉庫裡真有一顆叫這名字的包」優先於 provider，即使在裝的是本倉的 provider 也一樣。
- `librime-git`：`depends=('opencc')` → 解到 `[extra]/opencc 1.3.2-1`（日誌實物
  `-- Found opencc: /usr/lib/libopencc.so`），而 librime link 的是 **soname**（1.3 與 1.4 跨代）。
  同一份原始碼在本機把 opencc-git 1.4.2 裝好後重跑 `makepkg -dc` → **100% tests passed out of 2**、
  正常出包（不必改測試、不必 `--nocheck`）。⇒ depends 翻成 `opencc-git`。
- `spirv-llvm-translator-git`：`depends=(… spirv-tools)` → 解到 `[extra]/spirv-tools 1:1.4.363.0-1`，
  而那正是「validator 太舊」那 4 條 lit 紅的來源。⇒ 翻成 `spirv-tools-git`。
- `spirv-tools-git`：`depends=('spirv-headers')` → 解到 tag 版。⇒ 翻成 `spirv-headers-git`
  （本機實測 `-D SPIRV-Headers_SOURCE_DIR=/usr` 配 headers-git 照樣找得到、ctest 11/11 全過）。

### 病灶二：**依賴就緒閘門寫在永不執行的分支＝死碼**
`plan` 步的 `case "$PKG" in … esac` 是按包名分派，而 librime 那條閘門被寫進
`nvidia-utils-beta|nvidia-beta-dkms)` 分支內（`if [ "$PKG" = librime-git ]`）——那個分支對
librime-git **永遠不會執行**。實證：該 job 的 pacman 從頭到尾沒同步過 `junlin03-aur`
（日誌裡 0 筆 `junlin03-aur downloading`），照樣建置、照樣用 1.3 編、照樣紅。
⇒ 閘門搬到**通用分支**，改成按 `$PKG` 查表的 `_extra_gate_deps`：
`librime-git → opencc-git`、`spirv-llvm-translator-git → spirv-tools-git spirv-headers-git`、
`mesa-tkg-git → spirv-llvm-translator-git`（未就緒就 skip 等下輪，符合本倉 DAG 收斂設計）。
同時把 `librime-git`／`spirv-tools-git`／`spirv-headers-git` 加進 init 步的
「該 job 要掛 junlin03-aur」名單，否則閘門與 `makepkg -s` 都看不到本倉的包
（mesa 之所以看得到，就是它在名單裡：日誌有 ` junlin03-aur downloading...`）。

### 病灶三：**distro rust 對 LLVM 家族是等號硬釘，與自有 24.0git 家族互斥**
`mesa-tkg-git` 的 makedepends 有 `rust`／`rust-bindgen`（RustiCL 要用）。查實 `world/extra`
的 `rust-1:1.99.0-1` %DEPENDS% = `compiler-rt=23.1.1 lld=23.1.1 llvm-libs=23.1.1`
（**全同步庫唯一一筆等號硬釘**）⇒ 家族換成 24.0git 之後那個釘子不可能滿足，pacman 去拉
distro `compiler-rt 23.1.1` 撞 `compiler-rt-git`，`--noconfirm` 對「Remove compiler-rt-git?」
預設 N ⇒ `unresolvable package conflicts detected`，makepkg 死在「Checking buildtime dependencies」。
硬裝 distro rust 也不行：Arch 的 rust **動態鏈系統 LLVM**（`_llvmver=23.1.3` + `depends llvm-libs`，
產物 NEEDED `libLLVM.so.23.1`），換成 24.0git 後 rustc 連啟動都不行。
⇒ 改走 **rustup + nightly**（用戶 2026-10-15 裁定「編譯相關一律尖端」「去弄 24.0.0 而不是 23.x」）：
`extra/rustup` 的 `.PKGINFO` 實查 `provides=rust`＋`conflicts=rust`，工具鏈自帶 LLVM、不吃系統
libLLVM ⇒ 以 provider 身分满足 makepkg 的裸名 `rust`（與 opencc/spirv-tools 同一招）。
`RUSTUP_HOME=/opt/rustup`、`CARGO_HOME=/opt/cargo` 由「把容器 LLVM 換成自有」那步 export，
但 `su` 會剝環境（本倉 gstreamer 那步的實測結論）⇒ 真正生效要靠「云端编译」那步把兩個變數
**寫進 makepkg 命令字串**（`_mp_env`）。另把 `rust-bindgen-git` 預裝進去（同樣以 provider 頂替）。

### 附：spirv-tools-git 本體（同輪修掉、非 CI 可見）
1. `check()` 的自我舉證路徑原本寫 `build/tools/spirv-val/spirv-val`，上游從來不產那個子目錄
   （`tools/CMakeLists.txt` 的 `add_spvtools_tool` 直接出在 `tools/`）⇒ 好包被判紅。
2. `build()` 只寫 `-D SPIRV_TOOLS_BUILD_STATIC=OFF` 不夠：上游 `SPIRV_TOOLS_LIBRARY_TYPE`
   預設「BUILD_SHARED_LIBS 為真才 SHARED」，缺 `-D BUILD_SHARED_LIBS=ON` 會落到 STATIC ⇒
   產物只有 `libSPIRV-Tools.a` + `-shared.so`，**沒有** `libSPIRV-Tools.so`／
   `libSPIRV-Tools-{opt,link,reduce,lint,diff}.so`。那不是少幾個檔而是**斷鏈**：
   實測 `/usr/lib/libglslang.so` NEEDED 正是 `libSPIRV-Tools.so` 與 `libSPIRV-Tools-opt.so`
   ⇒ 裝下去 glslang → libplacebo → ffmpeg/mpv/librewolf/opencv 立刻找不到库。
   照官方旗標補齊（`BUILD_SHARED_LIBS=ON` + `SPIRV_TOOLS_BUILD_STATIC=OFF` + `SPIRV_WERROR=OFF`）。
3. 驗收：本機完整跑 `makepkg -dc`（build+check+package）**EXIT=0** 出包；包內
   `usr/lib/*.so` 七顆與 `pacman -Ql spirv-tools` 的檔案清單**逐檔一致**（零 `.a`），
   SONAME 與 NEEDED 也與 distro 那批一致。

## topgrade-git（2026-10-21；用戶「你直接復刻然後給我修理出來不就完了，同時兼容 sudo 跟 doas」）

原本是「AUR PKGBUILD + case 裡兩條 sed 注入」，現在整顆搬進本倉 `topgrade-git/`
（PKGBUILD + 一顆補丁檔），那條 sed case 已退役。**搬的動機不是整潔，是注入式改不動**：
doas 的修補要動 Rust 源碼，sed 只能改 PKGBUILD 的文字，改不了 crate 的行為。

### 壞的是什麼（都有實測，不是讀程式讀出來的）
`topgrade --only config_update --dry-run` 在本機必紅：
`config-update failed: 0: doas does not support the preserve_env_list option`
（Location 指到 `src/sudo.rs:506`）。根因是 `SudoKind::Doas` 跟 WinSudo/Gsudo/Pkexec
同組、遇到 `preserve_env_list` 一律回 `UnsupportedSudo`——**是用戶端自己拒的，沒去 exec doas**，
所以改 `/etc/doas.conf` 的 `keepenv`/`setenv` 一點機會都沒有（這條查過才敢講）。
全倉只有 `src/steps/os/linux.rs:1070` 會碰到它：`pacdiff` 要帶 `DIFFPROG`。

### 修法與證據
doas 一律清洗環境（實測 `DIFFPROG=meld doas /usr/bin/printenv DIFFPROG` → 空、rc=1），
所以照維護者在 issue #1435 讲的思路自己模擬：把目標包一層 `env VAR=value …`
（實測 `doas /usr/sbin/env 'DIFFPROG=meld' /usr/bin/printenv DIFFPROG` → `meld`、rc=0，
本機 `/etc/doas.conf` 只有 `permit nopass :wheel`，沒有命令白名單會擋）。
`SudoKind::Sudo` 那段完全沒動、仍走 `--preserve-env=`，**sudo 與 doas 兩邊都支援**。
源碼版對照（同一指令）：舊版 FAILED → 新版 `Dry running: /usr/sbin/doas /usr/sbin/env
'DIFFPROG=meld' /usr/sbin/pacdiff`、Summary `OK`；未設 `DIFFPROG` 時不塞 env 那層，
命令外形與修補前一致。同一份修補推在 fork 分支 `Capricornus007/topgrade:fix/doas-preserve-env`
（commit `77579740`，只動 `src/sudo.rs`）。

### 沒有順手扩大範圍（查過才收手）
`sudo.rs` 裡 doas 還會被拒的另外三類是 `login_shell`／`preserve_env`(All)／`set_home`。
逐一查可達性：`preserve_env+set_home` 只有 `gem update --system` 那條用，而它前面有閘門
`!Path::new("/usr/lib/ruby/vendor_ruby/rubygems/defaults/operating_system.rb").exists()`——
本機該檔**存在**（8月 11 2025 那顆 ruby 帶的）→ topgrade 直接 SkipStep，碰不到；
`login_shell` 全在 nix 那幾條，本機沒 nix。所以這輪只修真的會紅的那一處，
其余留字據在这里，将来誰在這臺機器上裝了 nix/asdf ruby 再回來補。

### 兩個構建層面的坑（都踩在同一輪）
1. **補丁必須在 `prepare()` 裡顯式打**。實測把 `.patch` 放進 `source=()` 而讓 makepkg
   自動套用，在「git clone 落在 `$srcdir/topgrade/` 子目錄」的情況下是**假成功**：
   第一次構建就產出一顆未修的包，裝機後照樣 FAILED，而 src tree 乾乾淨淨停在 c082f174。
   現在是 `patch -N -p1` + `grep -q 'skipping unset' src/sudo.rs || exit 1`，驗的是內容不是 rc。
2. **`-O*` 要从 CFLAGS/CXXFLAGS 摘掉**（原 sed case 的實質內容，搬進 `build()`）。
   aws-lc-sys 0.45 編 jitterentropy-base.c 有硬性 `#error` 不準最佳化，cc-rs 把環境
   CFLAGS 附加在 crate 的 `-O0` **後面**，makepkg 的 `-O2` 生效 → run #360 那樣紅。
   只摘 `-O[0-9s]+`，`-D_FORTIFY_SOURCE`／`-fstack-clash-protection`／`-fcf-protection` 全留。
3. 不設 AUR 那層的 `RUSTUP_TOOLCHAIN=stable`：本機 rustup 只裝了 nightly 與 1.99.1，
   沒有 stable，那行會直接「toolchain not installed」。上游根目錄 `rust-toolchain.toml`
   釘 `channel = "1.99.1"`，讓它自己生效；CI 容器那种非 rustup 的 cargo 會忽略該檔而用
   系統 rust（實查 Arch 倉 `rust = 1.99.1`，與釘選同版）→ 兩條路同一個編譯器。

### 四接點
* `topgrade-git/PKGBUILD`（epoch=1 的理由寫在檔頭：feed 已發佈同名未修產物，
  版號由 `pkgver()` 現算，不抬 epoch 會被契約 1 永久跳過）
* `topgrade-git/0001-fix-sudo-emulate-preserve_env_list-for-doas.patch`
* `build-packages.yml:620` 那條 in-tree 大 alternation 加 `|topgrade-git`（首命中即中，
  原来的 `topgrade-git)` sed case 已刪，`-O` 處理由 PKGBUILD 自己承担）
* `build-git-packages.yml` 的矩陣條目**沒動**：`"kind": "aur"` 繼續留著，
  作用是讓「更新校驗和並回推 AUR」那步（`matrix.kind != 'aur'`）不觸發——
  AUR 那顆是 Mark Wagie 的，本倉不該回推；llvm 那批用的是同一手法。

### 退場方式
上游把 doas 這處修掉之後，本補丁會**打不上而讓構建變紅**（`grep` 那道閘門會明講原因），
不是靜默失靈。那時刪掉 `.patch` 與 `prepare()` 裡那三行，必要時連 epoch 一起退。

## xorg-server-git（2026-10-21；用戶「鏈 libsystemd 你刪了不就好了？」）

在此之前 feed 只有 `xorg-xwayland-git`，`xorg-server-git` 一直吃 chaotic-aur；而那份是 **Arch 的建法**
（`-D systemd_logind=true`、depends 帶 `systemd-libs`），裝到 Artix 上就是鏈 libsystemd。
用戶點破得很對：那不是「不能建」，只是一個建置開關。所以改成 in-tree 自己建 **Artix 口味**：
`-D systemd_logind=false`、depends 不帶 systemd-libs。

### 為什麼這樣就沒有 libsystemd（實物依據）
本機 Artix 穩定版 `/usr/lib/Xorg` 的 NEEDED 逐條看過：`libudev.so.1`、`libdbus-1.so.3` 在，
**libsystemd 與 libelogind 都不在**。也就是 Artix 官方本身就是「udev 管裝置、不接 logind」，
本包照同一組開關建，產物自然一樣不鏈 systemd。

### 收哪些、不收哪些
切三顆：`xorg-server-git`／`xorg-server-common-git`／`xorg-server-xvfb-git`。
刻意不做 xephyr／xnest／devel／src：前兩顆本機與 CI 都沒用到；devel 只有編 xorg 驅動才需要
（本倉目前沒有這類包）；src 只是把整棵樹打包給人看。要補就照官方 PKGBUILD 加 `package_` 函式。

### 兩個不吃官方做法的點
1. **不套 `0001-Revert_damage_*.patch`**：那是 21.1.x 穩定版的上游回退補丁，master 早就改過，
   硬套打不上。
2. **拿掉 `-fno-plt` 與 `-Wl,-z,now`**（官方 PKGBUILD 同款理由，FS#55102／FS#54845）：
   xorg 模組會載入失敗（undefined symbol）。

### 四接點
* `xorg-server-git/PKGBUILD`（本倉 in-tree）
* `build-packages.yml:662` 那條 in-tree 大 alternation 加 `|xorg-server-git`
* `build-git-packages.yml` 矩陣加 `{"key": "xorg-server-git", "repo_name": "xorg-server-git", "variant": "none"}`
* 本檔

### 退場
本機跑的是 Artix 穩定版 xorg-server；這顆只是「尖端選項」，**不是**拿來日常替換的。
真要裝之前先確認顯卡驅動的 ABI：`provides` 的 `X-ABI-VIDEODRV_VERSION`／`X-ABI-XINPUT_VERSION`
會隨 master 變，驅動對不上就得一起升。
