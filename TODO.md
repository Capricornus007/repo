# TODO

## 2026-09-18（接手的 Qoder 四包接線一輪）

### 用戶 13:40 交代、目前仍未落地的待辦
- [ ] 監視 Qoder 四包（`qoder-cli`、`qoder-cli-cn`、`qoder-gui-bin`、`qoder-gui-cn`）的
      **首輪 CI**：重點看 `检测目标版本并决定是否需要构建` 有沒有把版本/校驗和讀對
      （`URL 模板與官方一致：…` 這四行是接線自己加的判據）、`预下载 Qoder 四包的上游源码`
      有沒有在半途被掐斷（國際 GUI 250MB、CN GUI 190MB）、`云端编译` 之後
      `current-repo` release 裡的資產與 `junlin03-aur.db` 是否都出現四個新包名。
      CI 由用戶本人盯（規則 2026-09-08），代理只負責推到遠端 ref 更新。
- [ ] 實機確認 **CN CLI 與 CN GUI 的 desktop / launcher 命名不碰撞**：
      `qoder-cli-cn` 佔 `/usr/bin/qoderclicn` + symlink `/usr/bin/qoder-cn`；
      `qoder-gui-cn` 主檔在 `/opt/Qoder-CN/qoder-cn`（2026-09-18 起打包時將上游
      "/opt/Qoder CN" 目錄改名、desktop Exec 同步重寫；同名但不在 PATH 上）、
      desktop 為 `/usr/share/applications/qoder-cn.desktop`、`StartupWMClass=qoder-cn`。
      本機已核對四包產物檔案清單交集為 0（只有 `/usr/`、`.PKGINFO` 這類共用目錄/元資料），
      還要在真機（Hyprland/sway + 桌面包管理器）上看：工作列/視窗清單會不會把
      CLI 的 `qoder-cn` 和 GUI 的 `qoder-cn` 視窗混在同一個 app 圖示群組裡。

### 這一輪順帶查出、需要用戶拍板的（拿不準，先記不動手）
- [ ] AUR 已有**同名**包 `qoder-gui-bin`（pakrohk，走 `download.qoder.com` 滾動址 +
      `pkgver=latest`）。自有倉這包與它同名→裝過 AUR 版的機器上會被直接取代（符合預期），
      但要不要在 `provides`/`conflicts` 上再做點什麼，等首輪 CI 綠了再定。
- [x] 給 CLI 兩包補 conflicts（用戶已拍板，2026-09-18 落地）：實查 AUR——zxp 的
      `qoder-bin` 塞 `/usr/bin/qoder`、`qoder-cn-bin` 塞 `/usr/bin/qoder-cn`，與本倉
      CLI 兩包的 symlink 對撞；`qoder-cli` conflicts 補 `('qoder-bin' 'qoder')`
      （`qoder`＝arch-lsf 那份 cp -a 舊滾動 RPM，同樣含 `/usr/bin/qoder`），
      `qoder-cli-cn` conflicts 補 `('qoder-cn-bin')`。**不**給 CLI 加
      `provides=('qoder')/('qoder-cn')`：實查 libalpm `conflict.c`（6.0.2 與 master
      同款 `check_conflict`→`_alpm_depcmp`），conflicts 單向命中對手 provides、無
      反向豁免，而自家 GUI 兩包已宣告 `conflicts=('qoder')`/`('qoder-cn')`，一提供
      就 GUI/CLI 互斥死鎖。`qoder-ide-bin` 實查只塞 `/usr/bin/qoder-ide`，與 CLI 包
      零文件重疊，不列入 CLI conflicts（它與國際 GUI 包的重疊由 `qoder-gui-bin`
      既有 conflicts 擋）。三包 pkgrel 同升 2，讓元數據/佈局改動經 CI 實際出包。
- [ ] 國際 GUI 的 RPM 自帶 `/usr/share/bash-completion/completions/qoder` 與
      `/usr/share/zsh/site-functions/_qoder`，是寫給 IDE 的 CLI 橋接
      （`/usr/share/qoder-ide/bin/qoder`）的；而 PATH 上的 `qoder` 是 `qoder-cli` 的
      symlink。也就是「補全列的選項屬於另一個程式」。屬上游命名地雷，用戶已拍板
      **國際 GUI 包不動**（2026-09-18），維持照原樣保留。
- [ ] 體積：`qoder-gui-bin` 壓縮後 339.7MiB / 裝後 774.15MiB，`qoder-gui-cn` 337.99MiB /
      644.64MiB。`current-repo` release 會因為「保留舊版本資產」快速膨脹（清理步驟只留
      資料庫引用的那份，理論上各只留一版），仍建議留意 release 總量。
- [ ] 架構覆蓋：國際 GUI 的 `linux-arm64` 更新通道是殭屍資料（回 0.2.7 且 url 是
      `qoder_amd64.deb`）、CN GUI 的 manifest 根本沒有 linux arm64 產物 → 兩個 GUI 包
      `arch=('x86_64')` 如實標。CLI 兩包上游有 arm64 tarball，但 CI 矩陣只有 x86_64
      runner，實際只出 x86_64；哪天要補 aarch64，得先解決「沒有 arm64 runner」這件事。
