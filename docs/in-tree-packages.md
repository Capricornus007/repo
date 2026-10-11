# in-tree 包為什麼必須列進 build-packages.yml「拉取对应的套件仓库」

CI 的通用規則是「名字以 `-git` 結尾 → clone AUR，否則 clone `github.com/<owner>/<repo_name>.git`」。
本倉的目錄版（in-tree）包會被那條規則搶走，所以**必須**在那個 step 的 `case` 名稱清單裡先攔掉。
逐包理由原本寫在 workflow 內，但那個 step 有 21000 字元的表達式上限（**註解也計入**），故搬到這裡。
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
    「初始化 Arch Linux 環境」那步新增一段 `kind == 'multilib'`：開 [multilib]
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
    顯式分支，兩邊一致）；(2)「初始化 Arch Linux 環境」把自有 `junlin03-aur` 掛成 pacman
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
