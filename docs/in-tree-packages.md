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
