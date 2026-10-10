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
