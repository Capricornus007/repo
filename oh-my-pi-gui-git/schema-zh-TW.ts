/**
 * Taiwan Traditional Chinese (zh-TW) translations for the agent settings schema content:
 * group titles keyed by schema group name, setting labels/descriptions
 * keyed by setting path. SettingsWindow consults these only when the
 * active language is zh and falls back to the schema's English text
 * for anything missing.
 *
 * Boundary: the named tabs (appearance…providers) and the Advanced tab
 * (schema settings without ui metadata) are both fully covered.
 */

/** Section headings declared in the schema's TAB_GROUPS. */
export const ZH_TW_GROUP_TITLES: Record<string, string> = {
	Theme: "主題",
	"Status Line": "狀態列",
	Display: "顯示",
	Images: "圖片",
	Thinking: "思考",
	Sampling: "取樣",
	Prompt: "提示詞",
	"Retry & Fallback": "重試與回退",
	Advisor: "顧問（Advisor）",
	Prewalk: "Prewalk",
	Vision: "視覺",
	Input: "輸入",
	Approvals: "審批",
	Notifications: "通知",
	Speech: "語音",
	Collab: "協作",
	"Magic Keywords": "魔法關鍵詞",
	"Startup & Updates": "啟動與更新",
	"Power (macOS)": "電源（macOS）",
	Power: "電源",
	Agent: "Agent",
	Git: "Git",
	General: "常規",
	Chat: "聊天",
	Compaction: "壓縮",
	"Rules (TTSR)": "規則（TTSR）",
	Experimental: "實驗性",
	"Auto-Learn": "自動學習",
	Mnemopi: "Mnemopi",
	Hindsight: "Hindsight",
	Editing: "編輯",
	Reading: "讀取",
	"Read Summaries": "讀取摘要",
	LSP: "LSP",
	Bash: "Bash",
	"Eval & Runtimes": "Eval 與執行時",
	"Available Tools": "可用工具",
	Todos: "待辦",
	"Grep & Browser": "Grep 與瀏覽器",
	Computer: "桌面控制",
	GitHub: "GitHub",
	"Output Limits": "輸出上限",
	Execution: "執行",
	"Discovery & MCP": "發現與 MCP",
	Extensions: "擴充套件",
	Developer: "開發者",
	Modes: "模式",
	Composer: "輸入框",
	Sharpshooter: "Sharpshooter",
	Skills: "技能",
	"IDA Pro": "IDA Pro",
	Stream: "直播",
	Subagents: "子代理",
	Isolation: "隔離",
	"Commands & Skills": "命令與技能",
	Services: "服務",
	Fireworks: "Fireworks",
	"Tiny Model": "微型模型",
	Protocol: "協議",
	Timeouts: "超時",
	Privacy: "隱私",
};

/** Per-setting row text, keyed by schema setting path. */
export const ZH_TW_SETTINGS: Record<string, { label: string; description?: string }> = {
	"providers.openai-codex.codeMode": {
		label: "Codex 程式碼模式",
		description: "通過 eval 使用程式碼模式模型；其他工作階段工具由 eval 呼叫。自動模式跟隨模型目錄的能力標記。",
	},
	"providers.openai-codex.codeModeDirectTools": {
		label: "程式碼模式額外直接工具",
		description: "除 eval、ask、todo、yield、think、checkpoint 和 rewind 外，允許直接呼叫的工具。",
	},
	"update.channel": {
		label: "Core 更新通道",
		description: "omp update 與 Core 啟動更新檢查使用的通道。桌面應用更新在“更新”頁面管理。",
	},
	"edit.autoRepair.enabled": {
		label: "自動修復解析錯誤",
		description: "編輯導致檔案無法解析時，請小模型修復出錯區域，並重新解析驗證；修復失敗時顯示警告。",
	},
	"providers.cacheRetention": {
		label: "提示詞快取保留時間",
		description: "向支援的服務商傳送快取保留策略；自動模式使用服務商預設值，關閉會同時停用快取親和路由。",
	},
	"commit.mapReduceThreshold": { label: "分批生成提交資訊的閾值" },
	"commit.mapBatchTokenBudget": { label: "提交分析每批 Token 預算" },
	"commit.cacheEnabled": { label: "快取提交分析結果" },
	"commit.cacheTtlDays": { label: "提交分析快取天數" },
	"extensionHandlers.toolCallTimeoutMs": {
		label: "擴充套件工具呼叫超時（毫秒）",
		description: "擴充套件 tool_call 處理器的有效工作超時；等待 OMP 對話方塊期間不計時，無效值回退為 30000 毫秒。",
	},
	// ── appearance ──────────────────────────────────────────────────────────
	"theme.dark": { label: "深色主題", description: "TUI 與 GUI 使用深色外觀時的主題配色" },
	"theme.light": { label: "淺色主題", description: "TUI 與 GUI 使用淺色外觀時的主題配色" },
	symbolPreset: { label: "符號預設", description: "圖示與符號的字形集（Unicode、Nerd Font 或 ASCII）" },
	colorBlindMode: { label: "色盲模式", description: "差異新增行使用藍色而非綠色" },
	"statusLine.preset": { label: "狀態預設", description: "TUI 狀態列與 GUI 底部狀態列共用的佈局預設" },
	"statusLine.separator": { label: "狀態列分隔符", description: "各分段之間分隔符的樣式" },
	"statusLine.sessionAccent": { label: "工作階段強調色", description: "將工作階段名稱的顏色用於編輯器邊框和狀態列間隙" },
	"statusLine.transparent": {
		label: "透明狀態列",
		description:
			"狀態列使用終端預設背景而非主題的 `statusLineBg`。Powerline 端帽會被丟棄，因為它們需要對比色填充來過渡到周圍的終端區域。",
	},
	"statusLine.compactThinkingLevel": {
		label: "緊湊思考等級",
		description: "在模型名稱上以單個圖示顯示思考等級，而不是附加獨立的 ` · <等級>` 字尾。",
	},
	"statusLine.showHookStatus": { label: "顯示鉤子狀態", description: "在狀態列下方顯示鉤子狀態訊息" },
	"terminal.showImages": { label: "顯示內聯圖片", description: "在終端中內聯繪製圖片" },
	"images.autoResize": { label: "自動縮放圖片", description: "將大圖縮放至最大 2000x2000，以獲得更好的模型相容性" },
	"images.blockImages": { label: "遮蔽圖片", description: "阻止圖片傳送給 LLM 服務商" },
	"terminal.showProgress": {
		label: "原生執行進度",
		description: "顯示原生執行進度：終端使用 OSC 9;4，GUI 使用 Dock 徽標與視窗進度條",
	},
	"tui.textSizing": {
		label: "大標題（Kitty）",
		description:
			"使用 Kitty 的 OSC 66 文本尺寸協議將 Markdown H1 標題以 2 倍縮放繪製。僅在 Kitty 終端上生效，其他終端忽略。預設關閉。",
	},
	"tui.renderMermaid": {
		label: "繪製 Mermaid 圖表",
		description: "允許 Agent 使用 Mermaid 圖表：TUI 繪製為 ASCII，GUI 繪製為圖形",
	},
	"tui.reactions": {
		label: "Agent 表情回應",
		description: "允許 Agent 在回覆氣泡上用表情徽章回應你的訊息",
	},
	"tui.codexResetFireworks": {
		label: "Codex 重置煙花",
		description: "當 Codex 每週用量意外重置或有新存入的儲存重置時，在螢幕頂部三分之一處放煙花慶祝，直到按 Escape",
	},
	"tui.titleState": {
		label: "標題執行狀態",
		description: "在終端標題或 GUI 視窗標題中顯示 Agent 的工作、等待和輪到使用者狀態",
	},
	"tui.hyperlinks": {
		label: "終端超連結",
		description:
			"將路徑和 URL 包裹為 OSC 8 超連結，以便終端原生點選開啟（auto：偵測支援；off：從不；always：無條件）",
	},
	"tui.tight": { label: "緊湊介面密度", description: "壓縮 TUI 輸出與 GUI 介面間距" },
	"tui.scrollbackRebuild": {
		label: "重寫滾動歷史",
		description:
			"當塊的最終形態替換其即時預覽時，擦除並重放終端滾動歷史。關閉時（預設），過時的預覽副本保留在歷史中，最終內容追加在下方。",
	},
	"display.shimmer": { label: "微光動畫", description: "工作/載入訊息的動畫樣式" },
	"display.smoothStreaming": { label: "平滑流式輸出", description: "在資料塊到達時平滑地展現助手文本和流式工具輸入" },
	"display.showTokenUsage": { label: "顯示 Token 用量", description: "在助手訊息上顯示每輪 token 用量" },
	"display.cacheMissMarker": {
		label: "快取未命中標記",
		description: "當某輪助手請求丟失（未命中）提示詞快取時，在其上方顯示分隔線",
	},
	"display.collapseCompacted": {
		label: "摺疊已壓縮歷史",
		description: "在即時轉錄中把壓縮前的歷史摺疊到摘要分隔線之後；停用則保留完整轉錄，並在每個壓縮點顯示分隔線",
	},
	showHardwareCursor: { label: "顯示硬體游標", description: "顯示終端游標以支援輸入法（IME）" },
	"tui.imeSafeCursor": {
		label: "輸入法安全的提示符佈局",
		description: "把提示符底邊框移到單獨一行，避免 macOS 輸入法預編輯文本使其移位",
	},
	"task.showResolvedModelBadge": {
		label: "顯示解析後模型徽章",
		description: "在任務部件狀態行中顯示每個子代理實際使用的模型 ID",
	},

	// ── model ───────────────────────────────────────────────────────────────
	"advisor.enabled": {
		label: "啟用顧問",
		description: "搭配第二個模型（分配給 'advisor' 角色），被動審查每一輪並注入批註。",
	},
	"prewalk.enabled": {
		label: "啟用 Prewalk",
		description:
			"先以目前模型開始，在計劃提示的待辦列表生成後、首次編輯/寫入時切換到快速/便宜的模型（預設 'smol' 角色）——強模型負責規劃、提交待辦並開始實現，然後交接。可用 --prewalk / --no-prewalk 按工作階段覆寫。",
	},
	"prewalk.auto": {
		label: "自動 Prewalk",
		description:
			"通過 'judge' 角色解析出的原生判定模型，判斷每個新的頂層使用者任務是否把困難推理集中在前期。需要原生判定模型；沒有時不做分類。與“啟用 Prewalk”相互獨立。",
	},
	"prewalk.autoTarget": {
		label: "自動 Prewalk 目標",
		description: "自動 Prewalk 在首次編輯/寫入時交接到的模型或角色（預設 '@smol'）。",
	},
	// 17.3.0 移除了全域 advisor.subagents（遷移至 task.agentAdvisor）。
	"task.agentAdvisor": {
		label: "子代理顧問（按 agent）",
		description:
			'按 agent 名稱設定顧問模型（取代已移除的 advisor.subagents），例如 { task: "on" } 表示對 task 子代理啟用預設顧問。',
	},
	"advisor.syncBacklog": {
		label: "顧問同步積壓",
		description: "當顧問落後此輪數時，暫停主 Agent 最多 30 秒。Off 表示停用追趕延遲。",
	},
	"advisor.immuneTurns": {
		label: "顧問免疫輪數",
		description: "顧問的疑慮或阻斷打斷一次之後，在此數量的主輪次內將後續的疑慮/阻斷以非打斷方式路由。",
	},
	modelRoleStorage: { label: "模型角色儲存", description: "模型選擇器中角色分配的儲存位置" },
	"images.describeForTextModels": {
		label: "為純文本模型描述圖片",
		description: "當圖片附加到不支援視覺的模型時，將其儲存到 local:// 下，並注入來自視覺模型的描述，而不是丟棄",
	},
	"images.urls.enabled": {
		label: "以 URL 傳送圖片",
		description: "通過設定的後端釋出圖片，並向可抓取 URL 的服務商傳送短連結；全部後端失敗時自動回退為內聯圖片",
	},
	"images.urls.backends": { label: "圖片 URL 後端", description: "釋出圖片時按順序嘗試的目標" },
	"images.urls.options": { label: "圖片 URL 後端選項", description: "各發布後端使用的 JSON 選項" },
	"images.urls.credentials": { label: "圖片 URL 後端憑據", description: "各發布後端使用的憑據；介面會隱藏其值" },
	"images.urls.command": { label: "圖片上傳命令", description: "command 後端使用的 argv 模板" },
	"images.urls.publicBaseUrl": { label: "圖片公共 URL", description: "代理圖片服務的外部可訪問基礎 URL" },
	"images.urls.ttlHours": {
		label: "圖片 URL 有效期",
		description: "圖片連結的有效小時數；0 表示 broker 執行期間持續有效",
	},
	"images.urls.bindHost": { label: "圖片服務監聽位址", description: "圖片 blob 服務監聽的主機位址" },
	"images.urls.sshTarget": { label: "圖片 SSH 目標", description: "建立 SSH 反向轉發的 user@host 目標" },
	"images.urls.sshRemotePort": { label: "圖片 SSH 遠端埠", description: "SSH 反向轉發使用的遠端監聽埠" },
	defaultThinkingLevel: { label: "思考等級", description: "支援思考的模型的推理深度" },
	hideThinkingBlock: { label: "隱藏思考塊", description: "在助手回覆中隱藏思考塊" },
	proseOnlyThinking: { label: "僅散文思考", description: "從思考摘要中省略程式碼塊，並以省略號替代" },
	omitThinking: { label: "省略思考摘要", description: "指示上游服務商在回覆中完全省略思考摘要（在支援的情況下）" },
	"model.loopGuard.enabled": { label: "迴圈守衛", description: "為模型推理和散文輸出啟用自動流式迴圈偵測" },
	"model.loopGuard.checkAssistantContent": {
		label: "迴圈守衛掃描散文",
		description: "除思考日誌外，還對助手散文訊息應用迴圈守衛",
	},
	"model.loopGuard.toolCallReminder": {
		label: "迴圈守衛工具呼叫提醒",
		description:
			"當 Gemini 推理流連續輸出多個規劃標題卻不呼叫工具時，中斷它並注入一條要求發起工具呼叫的提醒（需啟用迴圈守衛）",
	},
	"model.toolCallLoopGuard.enabled": {
		label: "工具呼叫迴圈守衛",
		description: "偵測跨輪次的連續相同工具呼叫，並注入糾正性引導",
	},
	"model.toolCallLoopGuard.threshold": {
		label: "工具呼叫迴圈閾值",
		description: "注入糾正性引導所需的連續相同工具呼叫次數",
	},
	"model.toolCallLoopGuard.exemptTools": {
		label: "迴圈豁免工具",
		description: "允許連續重複而不觸發跨輪迴圈守衛的工具名稱",
	},
	inlineToolDescriptors: {
		label: "內聯工具描述符",
		description:
			"在系統提示詞中繪製完整的工具描述符，並從服務商工具 schema 中剝離頂層/巢狀描述，使描述文本只發送一次。Auto 對 Gemini 模型啟用，其他模型停用",
	},
	includeModelInPrompt: {
		label: "在提示詞中包含模型",
		description: "在系統提示詞中暴露目前模型識別符號，讓 Agent 知道自己使用的是哪個模型",
	},
	includeWorkspaceTree: {
		label: "包含工作區目錄樹",
		description: "在系統提示詞中繪製工作區目錄樹。警告：檔案修改時可能破壞跨工作階段的提示詞快取。",
	},
	skillful: {
		label: "在提示詞中列出技能",
		description: "在系統提示詞中列出可用技能；關閉可節省上下文，並可用 /skillful 按工作階段切換",
	},
	personality: { label: "性格", description: "繪製到系統提示詞性格塊中的溝通風格" },
	temperature: { label: "溫度", description: "取樣溫度（0 = 確定性，1 = 創造性，-1 = 服務商預設）" },
	topP: { label: "Top P", description: "核取樣截斷（0-1，-1 = 服務商預設）" },
	topK: { label: "Top K", description: "從機率最高的 K 個 token 中取樣（-1 = 服務商預設）" },
	minP: { label: "Min P", description: "最小機率閾值（0-1，-1 = 服務商預設）" },
	presencePenalty: { label: "存在懲罰", description: "對引入已出現 token 的懲罰（-1 = 服務商預設）" },
	repetitionPenalty: { label: "重複懲罰", description: "對重複 token 的懲罰（-1 = 服務商預設）" },
	textVerbosity: { label: "文本詳細度", description: "OpenAI Responses 與 Codex 的回覆詳細度（low、medium 或 high）" },
	"tier.openai": {
		label: "服務等級 — OpenAI",
		description:
			"OpenAI / OpenAI-Codex 請求以及經 OpenRouter 路由的 OpenAI 系模型的處理等級（none = 不傳送）。以 `service_tier` 傳送。",
	},
	"tier.anthropic": {
		label: "服務等級 — Anthropic",
		description:
			'Claude 請求的處理等級。`priority` 在支援的 Anthropic 直連模型上實現快速模式（`speed: "fast"`）；在 Bedrock/Vertex Claude 及經 OpenRouter 時忽略。',
	},
	"tier.google": {
		label: "服務等級 — Google",
		description:
			"Gemini（Google AI Studio + Vertex）請求以及經 OpenRouter 路由的 Google 系模型的處理等級（none = 不傳送）。以頂層 `serviceTier` 欄位傳送。",
	},
	"tier.subagent": {
		label: "服務等級 — 子代理",
		description:
			"派生的 task/eval 子代理的服務等級。Inherit = 跟隨主 Agent 目前的按廠商等級（隨 /fast 變化）；選擇具體值則應用於子代理模型所屬的廠商。",
	},
	"tier.advisor": {
		label: "服務等級 — 顧問",
		description:
			"顧問模型的服務等級。None = 標準處理；Inherit = 跟隨主 Agent 目前的按廠商等級；選擇具體值則應用於顧問模型所屬的廠商。",
	},
	"retry.maxRetries": { label: "重試次數", description: "API 出錯時的最大重試次數" },
	"retry.maxDelayMs": {
		label: "最大重試延遲",
		description:
			"重試之間的最長等待時間（毫秒）。當服務商要求等待超過此值、且沒有憑據或模型回退成功時，請求會快速失敗而不是睡眠等待（例如 Anthropic 長達 3 小時的限流視窗）。",
	},
	"retry.modelFallback": { label: "重試模型回退", description: "允許重試恢復時切換到設定的回退模型" },
	"retry.waitForUsageReset": {
		label: "等待額度重置",
		description:
			"服務商回傳明確的額度重置時間時，等待到重置後再重試，即使超過最大重試延遲。可隨時中止等待；子任務也會一同等待。",
	},
	"retry.usageAwareFallback": {
		label: "用量感知回退",
		description:
			"利用可靠的程式設計套餐額度報告，在硬性用量限制前優先選擇同服務商賬戶，其次是設定的回退模型。普通設定的 API 金鑰不參與。",
	},
	"retry.usageReservePct": {
		label: "預留餘量",
		description: "剩餘額度低於此百分比時，將程式設計套餐模型視為接近上限。用量未知或未對映時保持主模型。",
	},
	"retry.usageReservePolicy": {
		label: "預留策略",
		description: "當所有同服務商程式設計套餐賬戶都進入預留餘量時的處理方式。",
	},
	"retry.fallbackChains": {
		label: "重試回退鏈",
		description:
			'將模型角色、模型選擇器（"provider/model-id"）或服務商萬用字元（"provider/*"）對映為有序回退選擇器的 JSON 物件，例如 {"default":["openai/gpt-4o-mini"],"google-antigravity/*":["google/*","google-vertex/*"]}。面向模型的鍵在該模型/服務商啟用時生效，與角色無關；"provider/*" 條目保留失敗模型的 id 並更換服務商。帶 id 字首的萬用字元（"openrouter/google/*"）會為失敗模型的裸 id 重新新增字首（google-antigravity/gemini-x -> openrouter/google/gemini-x），用作鍵時僅匹配該服務商在該字首下的 id。',
	},
	"retry.fallbackRevertPolicy": { label: "回退恢復策略", description: "回退之後何時回傳主模型" },
	"retry.fallbackOn": { label: "回退觸發條件", description: "哪些失敗請求可以切換到已設定的回退模型" },
	"providers.anthropic.serverSideFallback": {
		label: "Anthropic 服務端回退（Fable 5）",
		description:
			"當 Claude Fable 5 / Mythos 5 請求被 Anthropic 安全分類器攔截時，在服務端改用 Claude Opus 4.8 重試（Anthropic `server-side-fallback-2026-06-01` beta）。需手動開啟——保持關閉則所有請求維持回退前的行為。",
	},
	"providers.autoThinkingModel": {
		label: "自動思考模型",
		description: "`auto` 思考等級的難度分類器：預設線上（/models 中的 TINY 角色，否則為 smol），或本地端側模型",
	},
	"providers.autoThinkingMaxEffort": {
		label: "自動思考強度上限",
		description:
			"`auto` 分類器可解析的最高強度。`xhigh` 使分類器比最高檔低一級，因此只有顯式的 `ultrathink` 才能達到 `max`；`max` 則允許分類器判定為異常的輪次在暴露該檔位的模型上按最高檔計費。",
	},

	// ── interaction ─────────────────────────────────────────────────────────
	autoResume: { label: "自動恢復", description: "自動恢復目前目錄中最近的工作階段" },
	"power.sleepPrevention": {
		label: "防止睡眠",
		description: "在活動工作階段期間防止 macOS 睡眠。每個等級是累積的——它會疊加所有更低等級的標誌。",
	},
	"git.enabled": { label: "啟用 Git 整合", description: "在 TUI 中顯示 git 分支、狀態和 PR 資訊，並監視倉庫後設資料。" },
	steeringMode: { label: "引導模式", description: "Agent 工作時如何處理排隊的訊息" },
	followUpMode: { label: "跟進模式", description: "一輪結束後如何逐出跟進訊息" },
	interruptMode: { label: "中斷模式", description: "引導訊息何時中斷工具執行" },
	"loop.mode": { label: "迴圈模式", description: "/loop 迭代之間、重新提交提示詞之前執行什麼操作" },
	doubleEscapeAction: { label: "雙擊 Escape 動作", description: "編輯器為空時連續按兩次 Escape 觸發的動作" },
	treeFilterMode: { label: "工作階段樹過濾", description: "開啟工作階段樹時的預設過濾模式" },
	autocompleteMaxVisible: { label: "自動補全條目數", description: "自動補全下拉框中最大可見條目數（3-20）" },
	emojiAutocomplete: {
		label: "Emoji 自動補全",
		description: "根據 `:name:` 短程式碼建議 emoji，並展開 `:D` 或 `:-)` 之類的文本表情",
	},
	"paste.largeMenuThreshold": {
		label: "大段貼上選單",
		description:
			"當貼上達到此行數時，提供選單將其包裹為程式碼塊、包裹進 XML 標籤或儲存為檔案。0 表示停用該選單（大段貼上仍會摺疊為 [Paste] 標記）。",
	},
	"startup.quiet": { label: "靜默啟動", description: "跳過歡迎介面和啟動狀態訊息" },
	"startup.showSplash": {
		label: "顯示啟動畫面",
		description: "正常互動式啟動時顯示完整的動畫設定畫面，而不重新執行設定。靜默啟動仍會抑制它。",
	},
	"startup.setupWizard": { label: "設定嚮導", description: "每個設定版本展示一次新增的入門引導步驟" },
	"startup.checkUpdate": { label: "檢查更新", description: "啟動時檢查 omp 更新" },
	"marketplace.autoUpdate": { label: "外掛市場自動更新", description: "啟動時檢查外掛更新" },
	"startup.changelogMode": { label: "啟動更新日誌", description: "選擇更新說明以摘要、完整詳情開始，或保持隱藏" },
	"magicKeywords.enabled": {
		label: "魔法關鍵詞",
		description: "為獨立的 ultrathink、orchestrate、workflowz 和 jevify 關鍵詞啟用隱藏提示",
	},
	"magicKeywords.ultrathink": {
		label: "Ultrathink 關鍵詞",
		description: "允許獨立的 ultrathink 請求最大自動思考並附加其隱藏提示",
	},
	"magicKeywords.orchestrate": {
		label: "Orchestrate 關鍵詞",
		description: "允許獨立的 orchestrate 附加其隱藏的多代理編排提示",
	},
	"magicKeywords.workflow": {
		label: "Workflow 關鍵詞",
		description: "允許獨立的 workflowz 附加其隱藏的 eval 工作流提示",
	},
	"magicKeywords.jevify": {
		label: "Jevify 關鍵詞",
		description: "允許獨立的 jevify 附加其隱藏的批次 judge 分類提示",
	},
	"completion.notify": { label: "完成通知", description: "Agent 完成一輪時通知" },
	"error.notify": { label: "錯誤通知", description: "Agent 因錯誤停止時通知" },
	"ask.timeout": { label: "詢問超時", description: "經過此秒數後自動選擇推薦的詢問選項（0 表示停用）" },
	"ask.notify": { label: "詢問通知", description: "ask 工具等待輸入時通知" },
	"recap.enabled": { label: "空閒回顧", description: "終端空閒一段時間後，生成一段簡短的 LLM 回顧說明目前進展" },
	"recap.idleSeconds": { label: "空閒回顧延遲", description: "空閒等待多少秒後顯示回顧" },
	"collab.relayUrl": { label: "中繼 URL", description: "/collab 使用的中繼（wss://host[:port]）" },
	"collab.webUrl": {
		label: "Web UI URL",
		description: "/collab 連結使用的瀏覽器 UI；留空則從 collab.relayUrl 推導；顯式 http:// 僅限 localhost",
	},
	"collab.displayName": { label: "顯示名稱", description: "向其他協作參與者顯示的名字（預設：作業系統使用者名稱）" },
	"share.serverUrl": {
		label: "分享伺服器",
		description: "/share 使用的分享檢視/上傳基礎位址（加密 blob 上傳 + 檢視器；連結形如 <base>/<id>#<key>）",
	},
	"share.store": { label: "分享儲存", description: "/share 上傳加密工作階段 blob 的位置" },
	"share.redactSecrets": {
		label: "分享金鑰脫敏",
		description: "上傳前對 /share 快照執行金鑰混淆器（使用 secrets.* 設定）",
	},
	"stt.enabled": { label: "語音轉文字", description: "啟用通過麥克風的語音轉文字輸入" },
	"stt.modelName": {
		label: "語音識別模型",
		description:
			"本地端側語音模型。Parakeet TDT v3（sherpa-onnx）是 SoTA 預設；Whisper base/small/large-v3-turbo 各檔（transformers.js）以體積換取多語言覆寫。首次使用時下載。",
	},
	"stt.submitTrigger": {
		label: "語音聽寫提交觸發",
		description: "選擇語音聽寫何時自動提交：從不、鬆手（2 個以上詞）、鬆手且句子完整、或當我說“提交”。",
	},
	"tools.approval": {
		label: "工具審批策略",
		description:
			"按工具設定審批策略。設為 'allow' 自動批准，'prompt' 需要確認，'deny' 阻止。這些覆寫在任何審批模式下都生效。",
	},
	"tools.approvalMode": {
		label: "工具審批",
		description:
			"工具呼叫的預設審批行為。'總是詢問' 僅自動批准只讀工具；'詢問並記住' 讀取前也詢問，且授權可按檔案或資料夾記住；'寫入' 自動批准讀取和工作區寫入工具；'Yolo' 自動批准所有層級，但使用者策略仍可提示或阻止。",
	},
	"features.unexpectedStopDetection": {
		label: "偵測意外停止",
		description: "使用小模型偵測助手聲稱要繼續卻沒有呼叫工具就停止的情況；自動提示它繼續。",
	},

	// ── context ─────────────────────────────────────────────────────────────
	"workspace.additionalDirectories": {
		label: "額外工作區目錄",
		description:
			"作為額外根目錄加入每個工作階段的工作區目錄（多根工作區）。可通過 /add-dir 和 /remove-dir 即時管理。路徑相對於 cwd 解析，建議使用絕對路徑。Agent 會被告知這些根目錄存在，並可對它們 read/grep/glob。",
	},
	"contextFiles.extra": {
		label: "額外上下文檔案",
		description:
			'與 AGENTS.md 一同載入的額外指令檔名。使用檔名（而非路徑）的 JSON 列表，例如 ["AGENTS.local.md"]；[] 表示不載入額外檔案。新工作階段開始後生效。',
	},
	"contextPromotion.enabled": {
		label: "自動提升上下文",
		description: "上下文溢位時提升到更大上下文的模型，而不是壓縮",
	},
	extendedContext: {
		label: "擴充套件上下文",
		description: "在支援的模型上啟用更大的上下文視窗，可能增加費用；關閉後使用預設或標準計費視窗。",
	},
	"chat.systemPrompt": {
		label: "聊天系統提示詞",
		description:
			"未單獨設定的聊天（omp --chat、GUI 聊天分頁）預設使用的系統提示詞，替換內建的聊天提示詞。留空則使用內建提示詞",
	},
	"chat.history": {
		label: "聊天曆史",
		description: "未單獨設定的聊天，每條訊息讓模型看到哪些內容。頁面仍顯示全部輪次",
	},
	"chat.historyTurns": { label: "聊天曆史深度", description: "未單獨設定的連續對話，每條訊息附帶多少輪之前的對話" },
	"compaction.enabled": { label: "自動壓縮", description: "上下文過大時自動壓縮" },
	"compaction.midTurnEnabled": {
		label: "輪中壓縮",
		description: "在下一次服務商請求之前，於安全的輪中工具迴圈邊界檢查閾值",
	},
	"compaction.methodOrder": {
		label: "壓縮方法順序",
		description: "自動維護上下文時按此順序嘗試；目前方法不可用或失敗後會繼續下一個。",
	},
	"compaction.thresholdPercent": {
		label: "壓縮閾值",
		description: "上下文維護的百分比閾值；設為 Default 使用舊的基於預留的行為",
	},
	"compaction.thresholdTokens": {
		label: "壓縮 Token 上限",
		description: "上下文維護的固定 token 上限；設定後覆寫百分比閾值",
	},
	"compaction.handoffSaveToDisk": {
		label: "儲存交接檔案",
		description: "為自動交接流程把生成的交接檔案儲存為 markdown 檔案",
	},
	"compaction.remoteStreamingV2Enabled": {
		label: "遠端壓縮 V2",
		description: "對相容的遠端壓縮模型使用 Responses 流式壓縮",
	},
	"compaction.asyncEnabled": {
		label: "非同步壓縮",
		description: "接近閾值時在後臺預先生成壓縮結果，達到閾值後立即接入目前工作階段。",
	},
	"compaction.idleEnabled": { label: "空閒壓縮", description: "token 數超過閾值時在空閒時壓縮上下文" },
	"compaction.idleThresholdTokens": { label: "空閒壓縮閾值", description: "觸發空閒壓縮的 token 數" },
	"compaction.idleTimeoutSeconds": { label: "空閒壓縮延遲", description: "空閒等待多少秒後開始壓縮" },
	"compaction.supersedeReads": {
		label: "取代過期讀取",
		description: "當同一檔案被再次讀取時，修剪較舊的讀取結果（快取感知，每輪執行）",
	},
	"compaction.dropUseless": {
		label: "省略無用結果",
		description: "工具結果被消費後，修剪被標記為上下文無用（無匹配、等待超時）的結果（快取感知）",
	},
	"snapcompact.systemPrompt": {
		label: "Snapcompact 系統提示詞",
		description:
			"實驗性：將選定的系統提示詞文本繪製為密集 PNG 圖片並附加到首條使用者訊息（僅限視覺模型）。節省 token，但被成像的文本會失去提示詞快取。",
	},
	"snapcompact.toolResults": {
		label: "Snapcompact 工具結果",
		description:
			"實驗性：將大型歷史工具結果繪製為密集 PNG 圖片而非文本（僅限視覺模型）。節省累積的讀取/搜尋輸出的 token。",
	},
	"tools.format": {
		label: "工具呼叫模式",
		description:
			"控制工具如何暴露給模型。Auto 使用服務商原生工具呼叫，除非所選模型被標記為不支援，則回退到 GLM 自有方言。Native 強制服務商原生工具；其他值強制使用指定的自有方言。工作階段啟動時生效。",
	},
	"snapcompact.shape": {
		label: "Snapcompact 形狀",
		description: "snapcompact 列印文本所用的畫框形狀（壓縮歸檔與內聯成像）。Auto 選擇針對目前模型調優的形狀。",
	},
	"branchSummary.enabled": { label: "分支摘要", description: "離開分支時提示生成摘要" },
	"ttsr.enabled": {
		label: "TTSR",
		description: "當輸出匹配規則模式時中斷 Agent 流式輸出（時間旅行流規則，Time-Traveling Stream Rules）",
	},
	"ttsr.contextMode": { label: "TTSR 上下文模式", description: "TTSR 觸發時如何處理部分輸出" },
	"ttsr.interruptMode": { label: "TTSR 中斷模式", description: "何時在流中直接中斷，何時在完成後再注入警告" },
	"ttsr.repeatMode": { label: "TTSR 重複模式", description: "規則如何重複觸發：每工作階段一次，或間隔若干訊息後" },
	"ttsr.repeatGap": { label: "TTSR 重複間隔", description: "規則再次觸發前需要的訊息數" },
	"ttsr.builtinRules": {
		label: "內建規則",
		description: "載入 Agent 自帶的預設規則（可用 ttsr.disabledRules 單獨覆寫）",
	},
	"ttsr.disabledRules": { label: "停用規則", description: "完全忽略的規則名稱（對內建預設規則和你自己的規則都生效）" },

	// ── memory ──────────────────────────────────────────────────────────────
	"memory.backend": {
		label: "記憶後端",
		description: "關閉、本地摘要管線、Mnemopi SQLite、Hindsight 遠端記憶，或 Sharpshooter 專案決策記憶",
	},
	"sharpshooter.model": {
		label: "Sharpshooter 模型",
		description: "用於提取和合並專案決策的模型選擇器；留空則使用 smol 角色",
	},
	"sharpshooter.intervalMinutes": {
		label: "Sharpshooter 合併間隔",
		description: "後臺合併待處理專案決策的間隔分鐘數",
	},
	"sharpshooter.injectionTokenLimit": {
		label: "Sharpshooter 注入上限",
		description: "每輪最多注入到上下文中的專案決策記憶 token 數",
	},
	"autolearn.enabled": {
		label: "自動學習（實驗性）",
		description: "Agent 停止後，提醒它把經驗教訓沉澱到記憶，並建立/完善隔離的受管技能",
	},
	"autolearn.autoContinue": {
		label: "停止時自動沉澱",
		description: "開啟時，停止後自動執行一個私密的沉澱輪次（消耗額外 token）。關閉時，僅保留常駐的自動學習引導。",
	},
	"mnemopi.dbPath": { label: "Mnemopi 資料庫路徑", description: "可選的 SQLite 資料庫路徑。預設為 Agent 記憶目錄。" },
	"mnemopi.bank": {
		label: "Mnemopi 記憶庫",
		description: "可選的共享記憶庫基礎名稱。按專案模式會由它派生專案本地記憶庫。",
	},
	"mnemopi.scoping": {
		label: "Mnemopi 作用域",
		description:
			"global = 一個共享記憶庫；per-project = 每個 cwd 獨立記憶庫；per-project-tagged = 專案本地寫入 + 全域召回可見",
	},
	"mnemopi.embeddingVariant": {
		label: "嵌入模型變體",
		description:
			"本地嵌入模型家族。en = 更強的英文模型；multilingual = 跨語言模型。更改後會在下次啟動時重建現有記憶嵌入。",
	},
	"mnemopi.autoRecall": { label: "Mnemopi 自動召回", description: "在每個工作階段的第一輪召回本地記憶" },
	"mnemopi.autoRetain": { label: "Mnemopi 自動留存", description: "把完成的對話輪次留存到本地 Mnemopi 記憶" },
	"mnemopi.polyphonicRecall": {
		label: "Mnemopi 多聲部召回",
		description: "啟用 4 路召回（向量、圖、事實、時序），以倒數排名融合（RRF）合併",
	},
	"mnemopi.enhancedRecall": { label: "Mnemopi 增強召回", description: "為重複和相似的召回查詢啟用分層查詢結果快取" },
	"mnemopi.proactiveLinking": {
		label: "Mnemopi 主動連結",
		description: "新記憶儲存時即納入情景圖，連結到相關實體與記憶",
	},
	"mnemopi.noEmbeddings": { label: "Mnemopi 停用嵌入", description: "強制使用確定性的純 FTS 召回，而非向量嵌入" },
	"mnemopi.embeddingModel": {
		label: "Mnemopi 嵌入模型",
		description: "高級：顯式嵌入模型 id，覆寫變體設定。留空則使用 mnemopi.embeddingVariant。",
	},
	"mnemopi.embeddingApiUrl": { label: "Mnemopi 嵌入 API URL", description: "傳給 Mnemopi 的可選 OpenAI 相容嵌入端點" },
	"mnemopi.embeddingApiKey": { label: "Mnemopi 嵌入 API 金鑰", description: "傳給 Mnemopi 的可選嵌入 API 金鑰" },
	"mnemopi.llmMode": {
		label: "Mnemopi LLM 模式",
		description: "不使用 LLM、使用線上微型模型（/models 中的 TINY 角色，否則為 @smol），或遠端 OpenAI 相容端點",
	},
	"mnemopi.llmBaseUrl": { label: "Mnemopi LLM Base URL", description: "Mnemopi 遠端模式的可選 OpenAI 相容 LLM 端點" },
	"mnemopi.llmApiKey": { label: "Mnemopi LLM API 金鑰", description: "Mnemopi 遠端模式的可選 LLM API 金鑰" },
	"mnemopi.llmModel": { label: "Mnemopi LLM 模型", description: "Mnemopi 遠端模式的可選 LLM 模型名稱" },
	"hindsight.apiUrl": { label: "Hindsight API URL", description: "Hindsight 伺服器 URL（雲端或自託管）" },
	"hindsight.apiToken": { label: "Hindsight API 令牌", description: "用於需要認證的 Hindsight 伺服器的 Bearer 令牌" },
	"hindsight.bankId": { label: "Hindsight 記憶庫 ID", description: "記憶庫識別符號（預設：專案名）" },
	"hindsight.scoping": {
		label: "Hindsight 作用域",
		description:
			"global = 一個共享記憶庫；per-project = 每個 cwd 獨立記憶庫；per-project-tagged = 共享記憶庫帶專案標籤，召回時合併全域與專案記憶",
	},
	"hindsight.autoRecall": { label: "Hindsight 自動召回", description: "在每個工作階段的第一輪召回記憶" },
	"hindsight.autoRetain": { label: "Hindsight 自動留存", description: "每 N 輪及工作階段邊界處留存轉錄" },
	"hindsight.retainMode": {
		label: "Hindsight 留存模式",
		description: "full-session = 每工作階段更新插入一份檔案；last-turn = 分塊",
	},
	"hindsight.mentalModelsEnabled": {
		label: "Hindsight 心智模型",
		description:
			"啟動時把精選的反思摘要（心智模型）讀入開發者指令。載入記憶庫上已有的模型——不寫入。搭配 hindsight.mentalModelAutoSeed 可同時自動建立內建種子集。",
	},
	"hindsight.mentalModelAutoSeed": {
		label: "Hindsight 心智模型自動播種",
		description:
			"工作階段啟動時，建立記憶庫上尚不存在的內建心智模型（project-conventions、project-decisions、user-preferences）。",
	},
	"providers.memoryModel": {
		label: "記憶模型",
		description:
			"Mnemopi 用於事實提取與整合的 LLM：預設線上（/models 中的 TINY 角色，否則為 smol/遠端），或本地端側模型",
	},

	// ── files ───────────────────────────────────────────────────────────────
	"edit.mode": { label: "編輯模式", description: "選擇編輯工具變體（replace、patch、hashline 或 apply_patch）" },
	"edit.fuzzyMatch": { label: "模糊匹配", description: "對空白差異接受高置信度的模糊匹配" },
	"edit.fuzzyThreshold": { label: "模糊匹配閾值", description: "接受模糊匹配的相似度閾值（0-1）" },
	"edit.streamingAbort": { label: "預覽失敗即中止", description: "補丁預覽失敗時中止流式編輯工具呼叫" },
	"edit.recoverInlineEdits": {
		label: "恢復內聯編輯內容",
		description: "把模型以普通文本輸出的編輯內容轉換為 edit 工具呼叫並執行",
	},
	"edit.blockAutoGenerated": {
		label: "阻止自動生成的檔案",
		description: "阻止編輯看似自動生成的檔案（protoc、sqlc、swagger 等）",
	},
	"edit.enforceSeenLines": {
		label: "強制執行已見行守衛",
		description: "拒絕錨定在先前讀取/搜尋從未完整展示過的行上的編輯",
	},
	"edit.blackbox.enabled": {
		label: "記錄編輯解析迴歸",
		description: "編輯導致 AST 解析失敗時，將修改前後原始碼及呼叫資訊追加到本地診斷日誌",
	},
	readLineNumbers: { label: "行號", description: "預設在讀取工具輸出前新增行號" },
	"read.defaultLimit": { label: "預設讀取行數", description: "Agent 呼叫 read 且不指定行數上限時預設回傳的行數" },
	"read.renderMarkdown": {
		label: "Markdown 預覽",
		description: "將 Markdown 讀取結果繪製為格式化的終端 Markdown 預覽，而非原始原始碼",
	},
	"read.summarize.enabled": { label: "讀取摘要", description: "當 read 不帶顯式選擇器呼叫時回傳結構化程式碼摘要" },
	"read.summarize.prose": { label: "散文摘要", description: "對 Markdown 和純文本讀取回傳結構化摘要" },
	"read.summarize.minBodyLines": {
		label: "摘要摺疊正文行數",
		description: "多行函式體或字面量超過此行數後才在讀取摘要中摺疊",
	},
	"read.summarize.minCommentLines": {
		label: "摘要摺疊註釋行數",
		description: "多行塊註釋超過此行數後才在讀取摘要中摺疊",
	},
	"read.summarize.minTotalLines": {
		label: "摘要最小檔案行數",
		description: "總行數少於此值的檔案按原文讀取，而不做結構化摘要",
	},
	"read.summarize.unfoldUntil": {
		label: "摘要展開目標",
		description: "BFS 展開可省略區段，直到摘要至少達到此可見行數。0 表示僅保留最外層省略。",
	},
	"read.summarize.unfoldLimit": {
		label: "摘要展開上限",
		description:
			"BFS 展開時摘要大小的硬上限。若某次展開後可見行數將超過此值，則跳過該展開（該區段保持摺疊），並繼續展開其餘區段。",
	},
	"read.toolResultPreview": { label: "內聯讀取預覽", description: "在轉錄中內聯繪製讀取工具結果，而非摘要行" },
	"lsp.enabled": { label: "LSP", description: "啟用 lsp 工具以獲得程式碼智慧（定義、引用、診斷、重新命名）" },
	"lsp.lazy": {
		label: "延遲啟動 LSP",
		description: "首次使用（lsp 工具或編輯匹配檔案型別）時才啟動語言伺服器，而非工作階段啟動時",
	},
	"lsp.formatOnWrite": { label: "寫入後格式化", description: "寫入程式碼檔案後自動使用 LSP 格式化" },
	"lsp.diagnosticsOnWrite": { label: "寫入後診斷", description: "寫入程式碼檔案後回傳 LSP 診斷" },
	"lsp.diagnosticsOnEdit": { label: "編輯後診斷", description: "編輯程式碼檔案後回傳 LSP 診斷" },
	"lsp.requestTimeout": {
		label: "請求超時",
		description:
			"代理未指定超時時，等待語言伺服器診斷、懸停等應答的秒數；編輯後的延遲診斷至少等待這麼久。冷啟動較慢的伺服器可調高。lsp 工具的 timeout 引數仍可按次調高或調低。",
	},
	"lsp.diagnosticsDeduplicate": {
		label: "診斷去重",
		description: "抑制檔案中已展示過的編輯後 LSP 診斷，只呈現新增或變化的",
	},

	// ── shell ───────────────────────────────────────────────────────────────
	"bash.enabled": { label: "Bash", description: "啟用 bash 工具以執行 shell 命令" },
	"bash.allowCompoundCommands": {
		label: "逐條審批覆合命令",
		description: "對使用 && 連線的簡單命令逐條匹配審批規則；未匹配的命令仍遵循常規 Bash 審批策略。",
	},
	"bash.autoBackground.enabled": {
		label: "Bash 自動後臺",
		description: "自動將長時間執行的 bash 命令轉入後臺，稍後交付結果",
	},
	"bash.patterns": {
		label: "Bash 審批模式",
		description: "有序的 bash 命令審批規則。每項含 match 和 approval 欄位；僅支援 '*' 萬用字元。",
	},
	"bash.gitGuard": {
		label: "Git 防護",
		description:
			"在 bash 工具中拒絕會丟棄或移動共享工作的 git 命令：stash、reset --hard 或重置到其他提交，以及在合併/變基衝突之外的 checkout/switch/restore",
	},
	"bashInterceptor.enabled": { label: "Bash 攔截器", description: "阻止已有專用工具的 shell 命令" },
	"bash.direnv": {
		label: "direnv 自動載入",
		description:
			"自動將倉庫的 direnv/devenv `.envrc` 載入到 bash 工作階段中，無需手動 `direnv exec` 即可使用 devenv 工具和環境變數。遵循 direnv 的允許列表：未經 `direnv allow` 的 `.envrc` 絕不會被執行",
	},
	"bash.direnvLoadTimeoutMs": {
		label: "direnv 載入超時（毫秒）",
		description:
			"首次 `direnv export` 的最長等待時間（冷啟動的 devenv shell 可能較慢）；超時後工作階段將在沒有 direnv 環境的情況下執行",
	},
	"shellMinimizer.enabled": {
		label: "Shell 輸出壓縮",
		description: "在回傳給 Agent 前壓縮冗長的 shell 輸出（git、npm、cargo 等）",
	},
	"shellMinimizer.sourceOutlineLevel": {
		label: "Shell 壓縮原始碼大綱",
		description: "cat/read 原始碼檔案時的原始碼大綱模式：default 或 aggressive",
	},
	"eval.py": { label: "Python Eval 後端", description: "允許 eval 工具把 Python 單元格派發到 IPython 核心" },
	"eval.js": { label: "JavaScript Eval 後端", description: "允許 eval 工具把 JavaScript 單元格派發到進程內執行時" },
	"eval.tools.enabled": {
		label: "Eval 定義的工具",
		description: "允許 eval 單元格定義可供 task、agent() 和 workpool() 子代理呼叫的工具",
	},
	"eval.workpool.freshAgents": {
		label: "Workpool 使用全新 Agent",
		description: "為每個 workpool 項啟動新的子代理，不復用 worker 或批次處理排隊項",
	},
	"eval.rb": { label: "Ruby Eval 後端", description: "允許 eval 工具把 Ruby 單元格派發到持久 Ruby 核心" },
	"eval.jl": { label: "Julia Eval 後端", description: "允許 eval 工具把 Julia 單元格派發到持久 Julia 核心" },
	"python.kernelMode": {
		label: "Python 核心模式",
		description: "在 eval 呼叫之間保持 IPython 核心存活，或每次全新啟動",
	},
	"python.interpreter": {
		label: "Python 直譯器",
		description: "指向精確 Python 執行檔的可選路徑。設定後跳過自動 Python 執行時探測。",
	},
	"ruby.interpreter": {
		label: "Ruby 直譯器",
		description: "指向精確 Ruby 執行檔的可選路徑。設定後跳過自動 Ruby 執行時探測。",
	},
	"julia.interpreter": {
		label: "Julia 直譯器",
		description: "指向精確 Julia 執行檔的可選路徑。設定後跳過自動 Julia 執行時探測。",
	},

	// ── tools ───────────────────────────────────────────────────────────────
	"tools.artifactSpillThreshold": {
		label: "Artifact 溢位閾值（KB）",
		description: "超過此大小的工具輸出儲存為 artifact；尾部保留內聯",
	},
	"tools.artifactTailBytes": {
		label: "Artifact 尾部大小（KB）",
		description: "輸出溢位為 artifact 時保留內聯的尾部內容量",
	},
	"tools.artifactHeadBytes": {
		label: "Artifact 頭部大小（KB）",
		description: "輸出溢位為 artifact 時與尾部一起保留內聯的頭部內容量（中間省略）。0 表示停用——僅保留尾部。",
	},
	"tools.outputMaxColumns": {
		label: "輸出列上限",
		description:
			"流式工具輸出（bash、python、js eval）和 `read` 的每行位元組上限。超過此寬度的行以省略號截斷；到下一個換行符之間的剩餘位元組被丟棄。0 表示停用。",
	},
	"tools.artifactTailLines": {
		label: "Artifact 尾部行數",
		description: "輸出溢位為 artifact 時保留內聯的最大尾部行數",
	},
	"todo.enabled": { label: "待辦", description: "啟用 todo 工具進行任務跟蹤" },
	"todo.reminders": { label: "待辦提醒", description: "提醒 Agent 在停止前完成待辦" },
	"todo.remindersMax": { label: "待辦提醒上限", description: "放棄前的最大待辦提醒次數" },
	"todo.eager": { label: "自動建立待辦", description: "首條訊息後推動自動建立待辦列表的力度" },
	"glob.enabled": { label: "Glob", description: "啟用 glob 工具進行 glob 模式檔案查詢" },
	"grep.enabled": { label: "Grep", description: "啟用 grep 工具進行正則內容搜尋" },
	"grep.contextBefore": { label: "Grep 前置上下文", description: "每個 grep 匹配前顯示的上下文行數" },
	"grep.contextAfter": { label: "Grep 後置上下文", description: "每個 grep 匹配後顯示的上下文行數" },
	"astGrep.enabled": { label: "AST Grep", description: "啟用 ast_grep 工具進行結構化 AST 搜尋" },
	"astEdit.enabled": { label: "AST Edit", description: "啟用 ast_edit 工具進行結構化 AST 重寫" },
	"debug.enabled": { label: "Debug", description: "啟用 debug 工具進行基於 DAP 的除錯" },
	"launch.enabled": { label: "Launch", description: "啟用 launch 工具以監管共享的長期專案進程" },
	"speechgen.enabled": {
		label: "語音生成",
		description: "啟用 tts 工具進行端側（Kokoro）或 xAI Grok Voice 語音檔案合成",
	},
	"generate_image.enabled": {
		label: "生成圖片",
		description: "啟用 generate_image 工具（文生圖與圖片編輯）。tools.xdev 開啟時以 xd:// 裝置形式暴露。",
	},
	"computer.enabled": { label: "桌面控制", description: "啟用原生桌面截圖與輸入，用於 OpenAI computer use" },
	"computer.backend": { label: "桌面控制後端", description: "選擇自動或顯式指定平臺原生的桌面捕獲與輸入" },
	"computer.display": { label: "桌面控制顯示器", description: "合成所有顯示器，或選擇一個原生顯示器 id" },
	"computer.maxWidth": { label: "截圖寬度上限", description: "合成截圖的最大寬度（畫素）" },
	"computer.maxHeight": { label: "截圖高度上限", description: "合成截圖的最大高度（畫素）" },
	"images.questionTimeoutMs": {
		label: "圖片提問超時",
		description: "read 工具通過 ?q= 向視覺模型提問時的單次請求超時（毫秒）。服務商卡頓時快速失敗；設為 0 停用超時。",
	},
	"checkpoint.enabled": { label: "檢查點/回退", description: "啟用 checkpoint 與 rewind 工具進行上下文檢查點管理" },
	"fetch.enabled": { label: "讀取 URL", description: "允許 read 工具抓取並處理 URL" },
	"vault.enabled": {
		label: "Obsidian 倉庫",
		description:
			"啟用 vault:// 內部 URL，通過 Obsidian CLI 讀寫 Obsidian 倉庫內容。停用時 vault:// 解析被拒絕，系統提示詞中的 vault:// 條目也會被省略。",
	},
	"github.enabled": {
		label: "GitHub CLI",
		description:
			"啟用 github 工具（基於 op 的派發，覆寫倉庫、issue、pull request、diff、搜尋、checkout、push 與 Actions 監視工作流）",
	},
	"github.cache.enabled": {
		label: "GitHub 檢視快取",
		description: "把繪製好的 issue/PR 檢視輸出快取到 ~/.omp/cache/github-cache.db，重複讀取零開銷",
	},
	"github.cache.softTtlSec": {
		label: "GitHub 快取軟 TTL",
		description: "在此時間窗內直接回傳快取的 issue/PR 檢視行（秒；預設 5 分鐘）",
	},
	"github.cache.hardTtlSec": {
		label: "GitHub 快取硬 TTL",
		description: "超過軟 TTL 後回傳快取行並在後臺重新整理；超過硬 TTL 後丟棄（秒；預設 7 天）",
	},
	"web_search.enabled": { label: "網路搜尋", description: "啟用 web_search 工具獲取即時網路結果" },
	"security.enabled": {
		label: "安全",
		description: "啟用 OMP 原生安全掃描的規劃、執行，以及只讀的 security:// 資源名稱空間",
	},
	"ask.enabled": { label: "Ask", description: "啟用 ask 工具進行互動式使用者提問" },
	"browser.enabled": { label: "瀏覽器", description: "啟用 browser 工具進行指令碼化 Chromium 自動化（puppeteer）" },
	"browser.cdpUrl": {
		label: "瀏覽器 CDP URL",
		description:
			"預設的 HTTP CDP 發現端點（例如 http://127.0.0.1:9222），用於附著到已有瀏覽器而不是啟動新瀏覽器。工具呼叫中顯式的 app.cdp_url 或 app.path 優先。",
	},
	"browser.headless": { label: "無頭瀏覽器", description: "以無頭模式啟動瀏覽器（停用則顯示瀏覽器介面）" },
	"browser.cmux": {
		label: "cmux 瀏覽器",
		description:
			"有 cmux socket 可用時，使用 cmux WKWebView 表面進行瀏覽器自動化。可用 PI_BROWSER_CMUX=0 或 PI_BROWSER_CMUX=1 覆寫。",
	},
	"browser.screenshotDir": {
		label: "截圖目錄",
		description:
			"儲存截圖的目錄。未設定時截圖寫入臨時檔案。支援 ~。示例：~/Downloads、~/Desktop、/sdcard/Download（Android）",
	},
	"tools.intentTracing": { label: "意圖追蹤", description: "要求 Agent 在執行每個工具呼叫前描述其意圖" },
	"tools.abortOnFabricatedResult": {
		label: "捏造工具結果即中止",
		description:
			"使用帶內工具呼叫時，模型一旦在輪次中開始幻覺編造工具結果便立即停止。停用則讓模型完成生成並丟棄編造的後續內容。",
	},
	"tools.maxTimeout": { label: "工具超時上限", description: "Agent 可為任何工具設定的最大超時秒數（0 = 不限制）" },
	"async.enabled": { label: "非同步執行", description: "啟用非同步 bash 命令和後臺任務執行" },
	"async.widgets": {
		label: "後臺任務即時元件",
		description:
			"為每個執行中的後臺任務繪製即時元件（由輸出推導的圖表、進度條、狀態格），顯示在等待卡片、任務膠囊和任務面板中。`widget` 模型角色（預設走 smol）為每個任務生成一次展示規則，此後更新不再消耗模型呼叫。",
	},
	"async.pollWaitDuration": {
		label: "最大輪詢時間",
		description:
			"`hub` 等待監視後臺任務的時長。固定值每次等待該時長。`smart` 自適應：從 5 秒開始，連續等待時逐漸加長（最長 5 分鐘），約一分鐘不再等待後重置為 5 秒。",
	},
	"irc.timeoutMs": {
		label: "IRC 超時",
		description: "hub 訊息等待（以及 send await:true）的預設超時（毫秒）；0 表示停用超時",
	},
	"tools.xdev": {
		label: "xd:// 工具",
		description:
			"把不常用（可發現）的工具掛載到 xd:// 裝置 URL 下，通過 read/write 驅動，而不是每次請求都攜帶它們的 schema。停用則把所有已啟用工具頂層暴露。",
	},
	"tools.xdevDocs": {
		label: "xd:// 提示詞檔案",
		description:
			"選擇哪些掛載裝置的檔案與 schema 內聯進系統提示詞。Built-ins 保持核心工具內聯，MCP 與擴充套件工具保持按需。",
	},
	"tools.xdevInlineDevices": {
		label: "xd:// 內聯裝置",
		description:
			"當 xd:// 提示詞檔案為“僅內建”時，內聯名稱匹配這些 glob 模式的動態裝置（例如 mcp__context_mode_*）。“僅目錄”忽略此設定。",
	},
	"mcp.enableProjectConfig": { label: "MCP 專案設定", description: "從專案根載入 .mcp.json/mcp.json" },
	"mcp.renderMarkdownResults": {
		label: "MCP Markdown 結果",
		description: "把非 JSON 的 MCP 文本結果在轉錄中繪製為 Markdown",
	},
	"mcp.notifications": { label: "MCP 更新注入", description: "把 MCP 資源更新注入 Agent 對話" },
	"mcp.notificationDebounceMs": { label: "MCP 通知防抖", description: "MCP 資源更新注入對話前的防抖視窗（毫秒）" },
	"tasks.todoClearDelay": { label: "待辦自動清除延遲", description: "已完成或已放棄的待辦從待辦部件中移除前的延遲" },
	"dev.autoqa": {
		label: "自動 QA",
		description:
			"自動工具問題上報（xd://report_issue）。預設開啟；首次上報會徵求同意，拒絕則停止上報，直到顯式重新啟用",
	},
	"dev.autoqaPush.endpoint": {
		label: "自動 QA 推送端點",
		description: "接收自動 QA JSON 報告的完整 URL（預設 https://qa.omp.sh/v1/grievances）",
	},

	// ── tasks ───────────────────────────────────────────────────────────────
	"plan.enabled": { label: "計劃模式", description: "啟用計劃模式：執行前先進行只讀探索與規劃" },
	"plan.defaultOnStartup": { label: "以計劃模式啟動", description: "每個新工作階段開始時自動進入計劃模式" },
	"goal.enabled": { label: "目標模式", description: "啟用按工作階段的目標模式和隱藏的 goal 工具" },
	"goal.statusInFooter": { label: "在底欄顯示目標狀態", description: "在狀態列的目標指示旁顯示 token 預算" },
	"goal.continuationModes": { label: "目標續行模式", description: "活動目標可在輪次之間自動續行的執行模式" },
	"title.refreshOnReplan": {
		label: "重新規劃時重新整理標題",
		description: "待辦初始化導致重新規劃後重新整理生成的工作階段標題，除非標題由使用者設定",
	},
	"task.isolation.enabled": {
		label: "隔離子代理",
		description: "在檢出的隔離副本中執行子代理，並在完成後整合更改",
	},
	"isolation.backend": {
		label: "隔離後端",
		description: "用於子代理隔離與 worktree 克隆的後端",
	},
	"worktree.clone": {
		label: "將目前檢出克隆到 Worktree",
		description:
			"新 worktree 優先使用寫時複製克隆目前檢出，使 node_modules、target 等忽略的構建產物一併保留；不支援時回退為普通檢出",
	},
	"worktree.cleanSource": {
		label: "建立 /wt 後清理源檢出",
		description: "使用 /wt 建立 worktree 並帶走更改後，重置源檢出的已跟蹤更改並刪除未跟蹤檔案",
	},
	"task.isolation.apply": {
		label: "應用隔離更改",
		description: "自動把成功的隔離任務更改應用到父檢出；停用則保留 patch 或分支產物",
	},
	"task.isolation.merge": { label: "隔離合並策略", description: "隔離任務更改的整合方式（應用 patch 或合併分支）" },
	"task.isolation.commits": { label: "隔離提交風格", description: "巢狀倉庫更改的提交訊息風格（通用或 AI 生成）" },
	"worktree.base": {
		label: "Worktree 基礎目錄",
		description:
			"Agent 管理的 worktree 的基礎目錄——任務隔離副本、`github` PR 檢出和 `omp worktree` 清理都位於此處。未設定時使用 ~/.omp/wt。必須是絕對路徑或 ~ 相對路徑；相對路徑會被忽略。OMP_WORKTREE_DIR 環境變數可覆寫此項。",
	},
	"task.eager": { label: "優先任務委派", description: "推動把工作委派給子代理的力度" },
	"task.batch": {
		label: "批次任務呼叫",
		description:
			"把 task 工具切換為批次形態：一次呼叫攜帶 { context, tasks[] }——每項一個子代理，可選按項指定 agent（預設為工作階段派生策略 agent）、按項隔離，並帶有一份前置到每個任務的共享上下文。async.enabled=true 時，每個派生作為獨立後臺 agent 執行，走正常的 idle/parked 生命週期；否則呼叫阻塞等待合併結果。停用則恢復扁平的單次派生 schema。",
	},
	"task.enableEffort": {
		label: "按任務指定強度",
		description: "在任務派生上暴露可選的 effort 引數，允許呼叫方覆寫每個子代理的思考等級",
	},
	"task.maxConcurrency": { label: "最大併發任務數", description: "併發執行的子代理最大數量" },
	"task.enableLsp": {
		label: "子代理使用 LSP",
		description:
			"允許 task 工具派生的子代理使用 lsp 工具。預設關閉以保持子代理低成本；當 LSP 感知的委派值得額外 token 時啟用。",
	},
	"task.maxRecursionDepth": { label: "任務遞迴深度上限", description: "子代理可以派生自己子代理的層級深度" },
	"task.maxRuntimeMs": {
		label: "子代理執行時長上限",
		description:
			"每個子代理的硬性牆鍾時限（毫秒）。0 表示停用。用於防禦逃脫推理層看門狗的服務商側流式掛起；觸發時按“超時”原因正常中止子代理。",
	},
	"task.agentIdleTtlMs": {
		label: "Agent 空閒 TTL",
		description:
			"空閒子代理在記憶體中保持存活的時長，之後被停泊到磁碟（毫秒）。被停泊的 agent 在收到訊息或被恢復時自動喚醒。0 表示空閒 agent 保持存活直到結束。",
	},
	"task.softRequestBudget": {
		label: "子代理軟請求預算",
		description:
			"每個子代理的軟請求預算（每次執行的助手請求數）。超過時注入一條收尾引導提示（見 task.softRequestBudgetNotice）；達到預算 1.5 倍時強制停止執行，agent 必須交出部分結論。0 表示停用該守衛。內建 scout/sonic agent 有更低的內建預算上限，因此低於該上限的值對它們仍然生效。",
	},
	"task.softRequestBudgetNotice": {
		label: "軟請求預算提示",
		description: "當子代理越過軟請求預算時注入一條引導提示，要求它在 1.5 倍強制交出停止前收尾。",
	},
	"task.maxEffort": {
		label: "單次派生強度上限",
		description:
			"task 工具按派生 effort 提示所允許的最大推理強度。較低的值防止呼叫方把子代理提升到超過此上限；預設值保留模型的完整範圍。",
	},
	"task.prewalk": {
		label: "通用任務 Prewalk",
		description:
			"為內建的通用 `task` 子代理啟用 prewalk：它以解析出的模型啟動，規劃並開始實現，然後在首次編輯/寫入時交接給 'smol' 角色。按 agent 的覆寫（task.agentPrewalk，在 /agents 中按 P 切換）和使用者 agent 的 `prewalk` frontmatter 不受此開關影響。",
	},
	"skills.enableSkillCommands": { label: "技能命令", description: "把技能註冊為 /skill:name 命令" },
	"commands.enableClaudeUser": { label: "Claude 使用者命令", description: "從 ~/.claude/commands/ 載入命令" },
	"commands.enableClaudeProject": { label: "Claude 專案命令", description: "從 .claude/commands/ 載入命令" },
	"commands.enableOpencodeUser": {
		label: "OpenCode 使用者命令",
		description: "從 ~/.config/opencode/commands/ 載入命令",
	},
	"commands.enableOpencodeProject": { label: "OpenCode 專案命令", description: "從 .opencode/commands/ 載入命令" },

	// ── providers ───────────────────────────────────────────────────────────
	"providers.maxInFlightRequests": {
		label: "最大併發請求數",
		description:
			'每個服務商 id 的最大併發 LLM 請求數（例如 "openai" 或 "anthropic"），在使用此設定根目錄的本地 OMP 進程間共享。未列出的服務商不受限制。',
	},
	"secrets.enabled": {
		label: "隱藏金鑰",
		description: "傳送給 AI 服務商前，混淆已設定的金鑰並對憑據形態的 token 脫敏",
	},
	"providers.ollama-cloud.maxConcurrency": {
		label: "Ollama Cloud 最大併發",
		description: "每個進程的 Ollama Cloud 子代理併發執行上限；0 表示停用該服務商專屬限制",
	},
	"providers.webSearchOrder": {
		label: "網路搜尋服務商順序",
		description: "web_search 工具的優先服務商排序；未列出的服務商按預設順序排在其後",
	},
	"providers.webSearchExclude": {
		label: "排除的網路搜尋服務商",
		description: "web_search 絕不使用的服務商，即使作為兜底",
	},
	"providers.webSearchGeminiModel": {
		label: "Gemini web_search 模型",
		description: "Gemini Google 搜尋接地所用的模型 ID。預設 gemini-2.5-flash。",
	},
	"providers.antigravityEndpoint": {
		label: "Antigravity 端點模式",
		description: "google-antigravity 服務商的端點路由策略（chat、search、image、discovery）",
	},
	"providers.imageOrder": {
		label: "圖片生成服務商順序",
		description: "圖片生成的優先服務商排序；未列出的服務商跟隨目前工作階段服務商及內建順序",
	},
	"providers.fireworksTier": { label: "Fireworks 等級", description: "預設服務路徑（不帶 service_tier）" },
	"live.voice": { label: "即時語音音色", description: "Codex 支援的即時語音工作階段所用的音色" },
	"providers.tts": {
		label: "文字轉語音服務商",
		description: "tts 工具的後端：本地端側神經網路 TTS（Kokoro-82M）或 xAI Grok Voice",
	},
	"tts.localModel": { label: "本地 TTS 模型", description: "本地 TTS 後端使用的端側神經網路 TTS 模型（Kokoro-82M）" },
	"tts.localVoice": { label: "本地 TTS 音色", description: "本地 TTS 後端使用的 Kokoro 音色（美式/英式，女聲/男聲）" },
	"tts.localSpeed": {
		label: "本地 TTS 語速",
		description: "本地 TTS 後端（tts 工具、omp say）的語速。1 = 正常；限制在 0.5–2.5",
	},
	"speech.enabled": { label: "語音朗讀", description: "助手輸出在流式到達時通過揚聲器朗讀出來" },
	"speech.mode": {
		label: "語音朗讀模式",
		description: "朗讀內容：all = 助手訊息 + 思考；assistant = 僅訊息；yield = 僅回合結束時的最終訊息",
	},
	"speech.enhanced": {
		label: "增強語音改寫",
		description:
			"合成前用微型/smol 模型把助手輸出改寫為自然的口語文本（描述程式碼、去掉連結和 markdown）。失敗時回退到機械式清理",
	},
	"speech.voice": { label: "語音朗讀音色", description: "朗讀助手輸出時使用的 Kokoro 音色" },
	"speech.speed": { label: "語音朗讀語速", description: "朗讀助手輸出時的語速。1 = 正常；限制在 0.5–2.5" },
	"providers.tinyModel": {
		label: "微型模型",
		description: "工作階段標題模型：預設線上（/models 中的 TINY 角色，否則為 @smol），或本地端側模型",
	},
	"providers.tinyModelDevice": {
		label: "微型模型裝置",
		description:
			"本地微型模型（標題 + 記憶）的 ONNX 執行服務商。預設僅 CPU 推理。PI_TINY_DEVICE 環境變數可覆寫此項。",
	},
	"providers.tinyModelDtype": {
		label: "微型模型精度",
		description:
			"本地微型模型的 ONNX 量化/精度。預設使用各模型自帶的 dtype（q4）；更低精度更快，更高精度更保真。PI_TINY_DTYPE 環境變數可覆寫此項。",
	},
	"providers.unexpectedStopModel": {
		label: "意外停止偵測模型",
		description: "意外停止偵測的分類器：預設線上（/models 中的 TINY 角色，否則為 smol），或本地端側模型。",
	},
	"providers.kimiApiFormat": {
		label: "Kimi API 格式",
		description: "Kimi Code 服務商的 API 格式（auto 跟隨即時模型後設資料）",
	},
	"providers.openaiWebsockets": {
		label: "OpenAI WebSockets",
		description: "OpenAI Codex 模型的 websocket 策略（auto 使用模型預設值，on 強制開啟，off 停用）",
	},
	"providers.streamFirstEventTimeoutSeconds": {
		label: "流首個事件超時",
		description: "等待模型流首個事件的秒數；-1 使用服務商/環境變數預設值，0 停用看門狗",
	},
	"providers.streamIdleTimeoutSeconds": {
		label: "流空閒超時",
		description: "模型流在事件之間允許保持靜默的秒數；-1 使用服務商/環境變數預設值，0 停用看門狗",
	},
	"providers.openrouterVariant": {
		label: "OpenRouter 路由",
		description: "附加到 OpenRouter 模型 ID 的預設路由變體字尾（當選擇器已指定變體時被覆寫）",
	},
	"providers.fetch": { label: "抓取服務商", description: "fetch/read URL 工具的閱讀器後端優先順序" },
	"codexResets.autoRedeem": {
		label: "Codex 自動兌換已存重置",
		description:
			"自動使用儲存的 Codex 限流重置：當輪次被卡、且沒有其他賬戶可接管時，恢復因 5 小時或每週視窗耗盡而被鎖的賬戶；並挽救即將過期的額度。unset 會在首次使用前詢問，yes 不提示直接使用，no 停用兩類檢查。",
	},
	"codexResets.minBlockedMinutes": {
		label: "Codex 自動兌換最小鎖定時長",
		description:
			"僅當自然解鎖——已耗盡的 5 小時/每週視窗中最晚的那個重置——距今至少此分鐘數時才自動兌換（不要為省去短暫等待而花掉稀缺額度）。調大（如 360）可忽略僅 5 小時視窗的鎖定。",
	},
	"codexResets.keepCredits": {
		label: "Codex 自動兌換保留量",
		description:
			"儲存的重置低於此數量時絕不自動使用（0 = 最後一份額度也可自動使用）。即將過期的額度例外——保留的額度過期等於什麼都沒保住。",
	},
	"codexResets.salvageHorizonHours": {
		label: "Codex 重置挽救視窗",
		description:
			"當儲存的 Codex 重置將在此小時數內過期、且任一聊天視窗（5 小時或每週）有可恢復的有效用量時，自動將其用掉（0 表示停用過期挽救）。",
	},
	"provider.appendOnlyContext": {
		label: "僅追加上下文",
		description:
			"快取系統提示詞 + 工具規格並保持僅追加的訊息日誌，使服務商字首快取（DeepSeek、Xiaomi/SGLang、Anthropic）以最大比率命中。Auto 對已知支援字首快取的服務商啟用。",
	},
	"exa.enabled": { label: "Exa", description: "所有 Exa 搜尋工具的總開關" },
	"exa.enableSearch": { label: "Exa 搜尋", description: "啟用 Exa 基礎搜尋、深度搜索、程式碼搜尋和抓取工具" },
	"exa.searchDelayMs": {
		label: "Exa 搜尋延遲",
		description: "Exa 網路搜尋請求之間的最小延遲（毫秒）；設為 0 停用節流",
	},
	"exa.enableResearcher": { label: "Exa 研究員", description: "啟用 Exa researcher 工具進行 AI 驅動的深度調研" },
	"exa.enableWebsets": { label: "Exa Websets", description: "啟用 Exa webset 管理與增強工具" },
	"searxng.endpoint": { label: "SearXNG 端點", description: "用於網路搜尋的自託管 SearXNG 例項基礎 URL" },

	// ── advanced（無 ui 後設資料，歸入 Advanced 選項卡）─────────────────────────
	// 常規
	setupVersion: { label: "設定嚮導版本", description: "記錄最近執行過的設定嚮導版本，用於按版本只展示新增的引導步驟" },
	"auth.broker.url": {
		label: "認證代理 URL",
		description: "遠端 `omp auth-broker serve` 主機位址，憑據經它代理；通常由 OMP_AUTH_BROKER_URL 環境變數設定",
	},
	"auth.broker.token": {
		label: "認證代理令牌",
		description: "訪問認證代理的令牌；通常由 OMP_AUTH_BROKER_TOKEN 環境變數設定",
	},
	shellPath: { label: "Shell 路徑", description: "自定義 shell 執行檔路徑，覆寫自動探測結果" },
	extensions: { label: "擴充套件路徑", description: "啟動時額外載入的擴充套件路徑列表" },
	enabledModels: {
		label: "啟用模型白名單",
		description: "限定可用模型的選擇器模式列表；為空表示不限制（支援按路徑作用域設定）",
	},
	enabledProviders: {
		label: "啟用的能力服務商",
		description: "額外啟用的能力發現服務商 id 列表（支援按路徑作用域設定）",
	},
	disabledProviders: {
		label: "停用的服務商",
		description: "停用的服務商 id 列表——能力發現來源與模型選擇器中的服務商通用",
	},
	disabledExtensions: { label: "停用的擴充套件", description: "按 id 停用的擴充套件列表（在擴充套件面板中管理）" },
	modelRoles: { label: "模型角色分配", description: "角色（default、smol、slow、advisor 等）到模型選擇器的對映" },
	modelTags: { label: "模型標籤", description: "自定義模型標籤的名稱、顏色與可見性設定" },
	modelProviderOrder: { label: "服務商排序", description: "模型選擇器中服務商的顯示順序" },
	cycleOrder: { label: "快速切換迴圈", description: "模型快速切換迴圈的角色順序（預設 smol → default → slow）" },
	// 狀態列與內聯圖片
	"statusLine.leftSegments": { label: "狀態列左側分段", description: "狀態列左側按順序顯示的分段 id 列表" },
	"statusLine.rightSegments": { label: "狀態列右側分段", description: "狀態列右側按順序顯示的分段 id 列表" },
	"statusLine.segmentOptions": {
		label: "狀態列分段選項",
		description: "按分段 id 覆寫各分段的繪製選項（鍵為分段 id）",
	},
	"tui.maxInlineImageColumns": {
		label: "內聯圖片列寬上限",
		description: "內聯圖片的最大寬度（終端列數，預設 100）。設為 0 表示不限制（僅受終端寬度約束）。",
	},
	"tui.maxInlineImageRows": {
		label: "內聯圖片行高上限",
		description: "內聯圖片的最大高度（終端行數，預設 20）。設為 0 表示僅使用基於視口的限制（終端高度的 60%）。",
	},
	"tui.maxInlineImages": {
		label: "內聯圖片數量上限",
		description:
			"作為即時終端圖形保留的內聯圖片最大數量（預設 8）。超出上限後較舊的圖片經完整重繪回退為文本佔位符。設為 0 表示保留所有圖片（無限制）。",
	},
	// 重試
	"retry.enabled": { label: "啟用重試", description: "API 請求失敗時自動重試的總開關" },
	"retry.baseDelayMs": { label: "重試基礎延遲", description: "重試之間指數退避的基礎等待時間（毫秒，預設 500）" },
	// 語音
	"stt.language": { label: "語音識別語言", description: "語音轉文字的識別語言程式碼（預設 en）" },
	// 壓縮
	"compaction.reserveTokens": {
		label: "壓縮預留 Token",
		description: "壓縮後為模型回覆預留的 token 數。不設定表示未顯式選擇——小視窗恢復時可能換用按比例計算的預留。",
	},
	"compaction.keepRecentTokens": {
		label: "壓縮保留最近 Token",
		description: "壓縮時原樣保留的最近訊息 token 數（預設 20000）",
	},
	"compaction.autoContinue": { label: "壓縮後自動繼續", description: "自動壓縮完成後自動繼續目前輪次" },
	"compaction.remoteEndpoint": { label: "遠端壓縮端點", description: "遠端壓縮服務的端點 URL；未設定時使用預設端點" },
	"compaction.v2RetainedMessageBudget": {
		label: "遠端壓縮 V2 保留預算",
		description: "遠端壓縮 V2 中原樣保留的訊息 token 預算（預設 64000）",
	},
	"branchSummary.reserveTokens": {
		label: "分支摘要預留 Token",
		description: "為分支摘要生成預留的上下文 token 數（預設 16384）",
	},
	// 本地記憶管線
	"memories.enabled": {
		label: "本地記憶（舊版開關）",
		description: "舊版本地記憶開關，僅為向後相容遷移保留——請改用 memory.backend",
	},
	"memories.maxRolloutsPerStartup": {
		label: "每次啟動提取上限",
		description: "單次啟動最多執行的記憶提取（rollout）批次數（預設 64）",
	},
	"memories.maxRolloutAgeDays": {
		label: "提取工作階段最大年齡",
		description: "納入記憶提取的工作階段最大年齡（天，預設 30）",
	},
	"memories.minRolloutIdleHours": {
		label: "提取工作階段空閒時長",
		description: "工作階段至少空閒此小時數後才納入記憶提取（預設 12）",
	},
	"memories.threadScanLimit": {
		label: "執行緒掃描上限",
		description: "啟動時掃描記憶提取候選的工作階段執行緒數上限（預設 300）",
	},
	"memories.maxRawMemoriesForGlobal": {
		label: "全域彙總原始記憶上限",
		description: "觸發全域彙總前允許的原始記憶條數上限（預設 200）",
	},
	"memories.stage1Concurrency": { label: "階段一併發數", description: "階段一（逐執行緒提取）的併發任務數（預設 8）" },
	"memories.stage1LeaseSeconds": { label: "階段一租約時長", description: "階段一提取任務的租約時長（秒，預設 120）" },
	"memories.stage1RetryDelaySeconds": {
		label: "階段一重試延遲",
		description: "階段一失敗任務的重試延遲（秒，預設 120）",
	},
	"memories.phase2LeaseSeconds": {
		label: "階段二租約時長",
		description: "階段二（全域彙總）任務的租約時長（秒，預設 180）",
	},
	"memories.phase2RetryDelaySeconds": {
		label: "階段二重試延遲",
		description: "階段二失敗後的重試延遲（秒，預設 180）",
	},
	"memories.phase2HeartbeatSeconds": { label: "階段二心跳間隔", description: "階段二執行時的心跳間隔（秒，預設 30）" },
	"memories.rolloutPayloadPercent": {
		label: "提取負載上下文佔比",
		description: "單個提取批次輸入允許佔模型上下文視窗的比例（預設 0.7）",
	},
	"memories.phase1InputTokenLimit": {
		label: "階段一輸入 Token 上限",
		description: "階段一每個執行緒輸入的 token 上限（預設 4000）",
	},
	"memories.fallbackTokenLimit": {
		label: "回退 Token 上限",
		description: "模型上下文視窗未知時使用的兜底 token 上限（預設 16000）",
	},
	"memories.summaryInjectionTokenLimit": {
		label: "記憶摘要注入上限",
		description: "注入工作階段的記憶摘要 token 上限（預設 5000）",
	},
	"autolearn.minToolCalls": {
		label: "自動學習最小工具呼叫數",
		description: "工作階段中的工具呼叫達到此數量後才觸發自動學習沉澱（預設 5）",
	},
	// Mnemopi
	"mnemopi.retainEveryNTurns": { label: "Mnemopi 留存間隔", description: "每隔多少輪留存一次轉錄（預設 4）" },
	"mnemopi.recallLimit": { label: "Mnemopi 召回條數上限", description: "每次召回回傳的記憶條數上限（預設 8）" },
	"mnemopi.recallContextTurns": {
		label: "Mnemopi 召回上下文輪數",
		description: "構造召回查詢時納入的最近對話輪數（預設 3）",
	},
	"mnemopi.recallMaxQueryChars": {
		label: "Mnemopi 召回查詢長度上限",
		description: "召回查詢的最大字元數（預設 4000）",
	},
	"mnemopi.injectionTokenLimit": {
		label: "Mnemopi 注入 Token 上限",
		description: "注入提示詞的召回記憶 token 上限（預設 5000）",
	},
	"mnemopi.debug": { label: "Mnemopi 除錯日誌", description: "輸出 Mnemopi 記憶後端的除錯日誌" },
	// Hindsight
	"hindsight.bankIdPrefix": { label: "Hindsight 記憶庫 ID 字首", description: "為自動生成的記憶庫 ID 新增此字首" },
	"hindsight.bankMission": {
		label: "Hindsight 反思使命",
		description: "建立記憶庫時寫入的反思使命（reflect mission），引導該庫的反思方向",
	},
	"hindsight.retainMission": {
		label: "Hindsight 留存使命",
		description: "建立記憶庫時寫入的留存使命（retain mission），引導從轉錄中提取哪些記憶",
	},
	"hindsight.retainEveryNTurns": { label: "Hindsight 留存間隔", description: "每隔多少輪留存一次轉錄（預設 3）" },
	"hindsight.retainOverlapTurns": {
		label: "Hindsight 留存重疊輪數",
		description: "相鄰留存塊之間重疊的輪數，避免邊界處上下文丟失（預設 2）",
	},
	"hindsight.retainContext": {
		label: "Hindsight 留存上下文標籤",
		description: "留存檔案附帶的上下文標籤（預設 omp）",
	},
	"hindsight.recallBudget": { label: "Hindsight 召回預算", description: "召回深度檔位：low、mid 或 high（預設 mid）" },
	"hindsight.recallMaxTokens": {
		label: "Hindsight 召回 Token 上限",
		description: "注入召回記憶的最大 token 數（預設 1024）",
	},
	"hindsight.recallContextTurns": {
		label: "Hindsight 召回上下文輪數",
		description: "構造召回查詢時納入的最近對話輪數（預設 1）",
	},
	"hindsight.recallMaxQueryChars": {
		label: "Hindsight 召回查詢長度上限",
		description: "召回查詢的最大字元數（預設 800）",
	},
	"hindsight.recallTypes": {
		label: "Hindsight 召回型別",
		description: "參與召回的記憶型別（預設 world 與 experience）",
	},
	"hindsight.debug": { label: "Hindsight 除錯日誌", description: "輸出 Hindsight 記憶後端的除錯日誌" },
	"hindsight.requestTimeoutMs": {
		label: "Hindsight 請求超時",
		description: "Hindsight 一般請求的超時（毫秒，預設 30000）",
	},
	"hindsight.reflectTimeoutMs": {
		label: "Hindsight 反思超時",
		description: "Hindsight 反思請求的超時（毫秒，預設 120000）",
	},
	"hindsight.recallTimeoutMs": {
		label: "Hindsight 召回超時",
		description: "Hindsight 召回請求的超時（毫秒，預設 30000）",
	},
	"hindsight.retainTimeoutMs": {
		label: "Hindsight 留存超時",
		description: "Hindsight 留存請求的超時（毫秒，預設 60000）",
	},
	"hindsight.mentalModelRefreshIntervalMs": {
		label: "Hindsight 心智模型重新整理間隔",
		description: "重新讀取心智模型的間隔（毫秒，預設 5 分鐘）",
	},
	"hindsight.mentalModelMaxRenderChars": {
		label: "Hindsight 心智模型繪製上限",
		description: "心智模型繪製進指令時的最大字元數（預設 16000）",
	},
	// Shell 與工具
	"bashInterceptor.patterns": {
		label: "Bash 攔截規則",
		description: "有序的 bash 攔截規則：正則模式命中時提示改用對應的專用工具",
	},
	"shellMinimizer.settingsPath": {
		label: "Shell 壓縮設定檔案",
		description: "覆寫壓縮器欄位預設值的可選 TOML 設定檔案路徑（支援 ~）",
	},
	"shellMinimizer.only": {
		label: "Shell 壓縮白名單",
		description: "僅對這些程式名啟用輸出壓縮（如 git）；為空表示啟用所有內建過濾器",
	},
	"shellMinimizer.except": { label: "Shell 壓縮排除列表", description: "明確不做輸出壓縮的程式名" },
	"shellMinimizer.maxCaptureBytes": {
		label: "Shell 壓縮捕獲上限",
		description: "每條命令捕獲的最大位元組數，超過則回退為原始未壓縮輸出（預設 4 MiB）",
	},
	"shellMinimizer.legacyFilters": {
		label: "Shell 舊版過濾器",
		description: "回退到 grep/find/pytest 的舊版過濾行為；未設定時由 OMP_MINIMIZER_LEGACY_FILTERS 環境變數決定",
	},
	"async.maxJobs": { label: "後臺任務數上限", description: "併發執行的後臺任務最大數量（預設 100）" },
	"bash.autoBackground.thresholdMs": {
		label: "自動後臺閾值",
		description: "bash 命令執行超過此毫秒數後自動轉入後臺（預設 60000）",
	},
	"eval.autoBackground.enabled": {
		label: "Eval 自動轉後臺",
		description: "自動把長時間執行的 eval 單元轉入後臺，完成後再投遞結果。",
	},
	"eval.autoBackground.thresholdMs": {
		label: "Eval 自動後臺閾值",
		description: "eval 單元執行超過此毫秒數後自動轉入後臺（預設 60000）。",
	},
	// 任務
	"task.disabledAgents": {
		label: "停用的子代理",
		description: "被停用的子代理名稱列表，task 工具不再提供（在 /agents 面板中管理）",
	},
	"task.agentModelOverrides": {
		label: "按子代理的模型覆寫",
		description: "子代理名稱到模型選擇器的對映，覆寫各 agent 的預設模型（在 /agents 面板中管理）",
	},
	"task.agentPrewalk": {
		label: "按子代理的 Prewalk 覆寫",
		description: "子代理名稱到 prewalk 開關狀態的對映（在 /agents 面板中按 P 切換）",
	},
	// 技能
	"skills.enabled": { label: "啟用技能", description: "技能發現與載入的總開關" },
	"skills.enableCodexUser": { label: "Codex 使用者技能", description: "從 ~/.codex/skills 載入技能" },
	"skills.enableClaudeUser": { label: "Claude 使用者技能", description: "從 ~/.claude/skills 載入技能" },
	"skills.enableClaudeProject": { label: "Claude 專案技能", description: "從 .claude/skills 載入技能" },
	"skills.enablePiUser": { label: "Pi 使用者技能", description: "從 ~/.omp/agent/skills 載入技能" },
	"skills.enablePiProject": { label: "Pi 專案技能", description: "從 .omp/skills 載入技能" },
	"skills.enableAgentsUser": {
		label: "Agents 使用者技能",
		description: "從 ~/.agent/skills 與 ~/.agents/skills 載入技能",
	},
	"skills.enableAgentsProject": {
		label: "Agents 專案技能",
		description: "從 .agent/skills 與 .agents/skills 載入技能",
	},
	"skills.customDirectories": { label: "自定義技能目錄", description: "額外掃描技能的自定義目錄列表" },
	"skills.ignoredSkills": { label: "忽略的技能", description: "按名稱 glob 模式忽略的技能列表" },
	"skills.includeSkills": { label: "僅包含的技能", description: "非空時僅載入名稱匹配這些 glob 模式的技能" },
	// SearXNG
	"searxng.token": { label: "SearXNG 訪問令牌", description: "SearXNG 例項的訪問令牌（token 認證）" },
	"searxng.basicUsername": { label: "SearXNG Basic 使用者名稱", description: "SearXNG 例項 HTTP Basic 認證的使用者名稱" },
	"searxng.basicPassword": { label: "SearXNG Basic 密碼", description: "SearXNG 例項 HTTP Basic 認證的密碼" },
	"searxng.categories": { label: "SearXNG 分類", description: "限定搜尋的分類（逗號分隔，如 general,news）" },
	"searxng.engines": { label: "SearXNG 引擎", description: "限定使用的搜尋引擎（逗號分隔）" },
	"searxng.language": { label: "SearXNG 語言", description: "搜尋結果的偏好語言程式碼" },
	// 提交
	"commit.mapReduceEnabled": {
		label: "提交分析 Map-Reduce",
		description: "大 diff 的提交資訊生成改用逐檔案並行分析再彙總的 map-reduce 流程",
	},
	"commit.mapReduceMinFiles": {
		label: "Map-Reduce 最小檔案數",
		description: "變更檔案數達到此值才啟用 map-reduce 分析（預設 4）",
	},
	"commit.mapReduceMaxFileTokens": {
		label: "Map-Reduce 單檔案 Token 上限",
		description: "單檔案 diff 超過此 token 數時啟用 map-reduce 分析（預設 50000）",
	},
	"commit.mapReduceTimeoutMs": { label: "Map-Reduce 超時", description: "map-reduce 分析的超時（毫秒，預設 120000）" },
	"commit.mapReduceMaxConcurrency": {
		label: "Map-Reduce 最大併發",
		description: "map-reduce 逐檔案分析的併發上限（預設 5）",
	},
	"commit.changelogMaxDiffChars": {
		label: "更新日誌 Diff 字元上限",
		description: "生成更新日誌時提供給模型的 diff 最大字元數（預設 120000）",
	},
	// 開發者
	"dev.autoqaPush.token": { label: "自動 QA 推送令牌", description: "推送自動 QA 報告時使用的認證令牌" },
	"dev.autoqaConsent": {
		label: "自動 QA 同意狀態",
		description:
			"是否同意分享自動工具問題報告：unset = 首次上報時詢問；granted = 記錄並（設定推送時）傳送；denied = 靜默忽略",
	},
	// 儲存 GC
	"gc.blobs": { label: "GC 清理 Blob", description: "`omp gc` 時清理不再被引用的工作階段 blob" },
	"gc.archive": { label: "GC 歸檔冷工作階段", description: "`omp gc` 時將長期未活動的工作階段移入歸檔" },
	"gc.wal": { label: "GC 處理 WAL", description: "`omp gc` 時處理工作階段儲存的預寫日誌（WAL）" },
	"gc.coldArchiveAfterDays": { label: "冷歸檔天數", description: "未活動超過此天數的工作階段才會被歸檔（預設 30）" },
	"gc.retainNewestGlobal": {
		label: "全域保留最新工作階段數",
		description: "無論多舊都保留的最新未活動工作階段數量（全域，預設 20）",
	},
	"gc.retainNewestPerCwd": {
		label: "每目錄保留最新工作階段數",
		description: "每個工作目錄無論多舊都保留的最新未活動工作階段數量（預設 10）",
	},
	// 思考預算
	"thinkingBudgets.minimal": {
		label: "思考預算（minimal）",
		description: "minimal 思考等級的推理 token 預算（預設 1024）",
	},
	"thinkingBudgets.low": { label: "思考預算（low）", description: "low 思考等級的推理 token 預算（預設 2048）" },
	"thinkingBudgets.medium": {
		label: "思考預算（medium）",
		description: "medium 思考等級的推理 token 預算（預設 8192）",
	},
	"thinkingBudgets.high": { label: "思考預算（high）", description: "high 思考等級的推理 token 預算（預設 16384）" },
	"thinkingBudgets.xhigh": {
		label: "思考預算（xhigh）",
		description: "xhigh 思考等級的推理 token 預算（預設 32768）",
	},
	"thinkingBudgets.max": { label: "思考預算（max）", description: "max 思考等級的推理 token 預算（預設 32768）" },
	"display.hideToolActivity": {
		label: "隱藏工具活動",
		description: "在轉錄中隱藏模型發起的工具呼叫及其結果",
	},
	externalThinking: {
		label: "外部思考",
		description: "使用私有 think 工具，並將推理工作交給 GPT Responses 模型",
	},
	"lsp.shared": {
		label: "共享語言伺服器",
		description: "通過常駐程式代理，讓同一專案的 omp 例項共享語言伺服器；不可用時回退到私有伺服器",
	},
	"browser.relay": {
		label: "瀏覽器中繼",
		description:
			"通過 omp 瀏覽器中繼控制自己的 Chrome 分頁。只需安裝一次擴充套件（`omp browser-relay install`）；瀏覽器工具需要時會自動啟動中繼伺服器。它優先於瀏覽器 CDP URL；可設定 PI_BROWSER_RELAY=0 或 PI_BROWSER_RELAY=1 覆寫。",
	},
	"browser.relayUrl": {
		label: "瀏覽器中繼 URL",
		description: "omp 瀏覽器中繼端點（預設 http://127.0.0.1:9224）",
	},
	"providers.webSearchTimeoutSeconds": {
		label: "網路搜尋超時",
		description: "每個服務商的搜尋傳輸硬超時；超時後 web_search 會嘗試下一個回退項，單位為秒（最大 300）",
	},
	"searxng.safesearch": { label: "SearXNG 安全搜尋" },
	// ── omp 18.2.x 上游新增設定 ─────────────────────────────────────────────
	"advisor.maxNotesPerUpdate": {
		label: "Advisor 每次更新最大筆記數",
		description: "Advisor 單次更新允許寫入的筆記上限；較低值更嚴格、可防刷屏。",
	},
	"browser.freezeOnTurnEnd": {
		label: "回合結束時凍結瀏覽器標籤",
		description: "回合結束時凍結由 OMP 管理的瀏覽器標籤，避免後臺標籤繼續活動。",
	},
	"browser.idleCloseSec": {
		label: "瀏覽器空閒關閉超時",
		description: "空閒多久後關閉由 OMP 啟動的瀏覽器（秒）；0 表示從不關閉。",
	},
	"collab.autoStart": {
		label: "協作自動啟動",
		description:
			"off 僅在執行 /collab 時共享；view 自動託管並由登錄檔分發只讀連結；control 自動託管並分發可操控工作階段的連結。",
	},
	"compaction.experimentalContextManagement": {
		label: "基於筆記的上下文視窗（實驗性）",
		description: "實驗性壓縮策略：用筆記支撐上下文視窗，可能改變壓縮與召回行為。",
	},
	"composer.recallClearedDrafts": {
		label: "召回已清空的草稿",
		description: "清空輸入框後仍可在歷史中召回該草稿。",
	},
	"composer.shape": {
		label: "輸入框形態",
		description: "輸入編輯器與狀態行的視覺佈局。",
	},
	"composer.tokenRate": {
		label: "生成速率顯示",
		description: "在標題欄用量區顯示平滑的每秒 token 生成速率，並在回合之間保持可見。",
	},
	"display.pinnedAgents": {
		label: "固定代理列表",
		description: "編輯器上方固定的活躍代理跳轉列表（off 隱藏；collapsed 顯示少量行並提供展開器；full 列出全部）。",
	},
	"display.showTurnTime": {
		label: "顯示回合耗時",
		description: "在助手訊息的用量行顯示從提示到產出的總耗時（含工具呼叫）。",
	},
	"find.enabled": {
		label: "Find（語義搜尋）",
		description: "啟用語義工作區搜尋工具，讓代理用自然語言定位行為與符號；行為類查詢優先於 grep/glob。",
	},
	"loop.conditionTimeoutMs": {
		label: "迴圈條件超時（毫秒）",
		description: "loop 條件求值的超時；0 表示不限時。",
	},
	"plan.autosave": {
		label: "自動儲存計劃",
		description: "計劃模式完成時自動把已批准的計劃儲存到磁碟。",
	},
	"plan.autosaveDir": {
		label: "自動儲存目錄",
		description: "計劃自動儲存的目標目錄；留空使用預設位置。",
	},
	"spelling.autocomplete": {
		label: "單詞自動補全（macOS）",
		description: "以行內提示顯示 macOS 詞典補全，按 Tab 接受。",
	},
	"spelling.autocorrect": {
		label: "自動更正（macOS）",
		description: "對已完成的詞應用有把握的 macOS 拼寫更正。",
	},
	"spelling.typoDetection": {
		label: "拼寫錯誤偵測（macOS）",
		description: "用目前 macOS 詞典標記提示詞中的拼寫錯誤。",
	},
	"statusLine.contextLine": {
		label: "上下文響應線",
		description:
			"左右段之間的分隔線如何反映上下文佔用（僅 box 輸入框）：off 為實心強調線；percentage 已用部分著強調色、其餘變暗。",
	},
	"stream.redactPatterns": {
		label: "額外脫敏模式",
		description: "直播螢幕資料發出前額外匹配的脫敏模式。",
	},
	"stream.serverUrl": {
		label: "直播伺服器",
		description: "omp stream 使用的直播伺服器位址。",
	},
	"task.agentServiceTierOverrides": {
		label: "子任務服務層級覆寫",
		description: "按代理/任務覆寫服務層級的鍵值對映。",
	},
	"tools.speculativeExecution.enabled": {
		label: "實驗性推測執行",
		description: "允許在正常派發前先執行已驗證的本地讀操作，以降低延遲。",
	},
	"tools.speculativeExecution.maxInFlight": {
		label: "推測執行併發",
		description: "正常派發前允許並行執行的已驗證本地讀操作上限。",
	},
	"tui.mouse": {
		label: "滑鼠點選聚焦",
		description: "允許滑鼠點選聚焦終端窗格。",
	},
	"tui.resizeScrollback": {
		label: "重排回滾區",
		description:
			"終端尺寸穩定後如何重新整理回滾區中的轉錄行：append 在保留歷史下方按新寬度重放；rebuild 清空回滾區後重放一份目前寬度轉錄。",
	},
	"tui.titleSpinner": {
		label: "終端標題旋轉符",
		description: "終端標題中工作態旋轉符的字形集。",
	},
	"tui.vimMode": {
		label: "Vim 編輯模式",
		description: "在輸入框啟用 Vim 鍵位編輯。",
	},
	"tui.vimModeDisplay": {
		label: "Vim 模式指示",
		description: "顯示目前 Vim 模式（如 NORMAL / INSERT）。",
	},

	// ── 18.9.x 合併後補充 ──────────────────────────────────────────────────
	// model / providers
	"providers.anthropic.slowMode": {
		label: "Anthropic 慢速模式",
		description:
			"Anthropic 訂閱的低優先順序通道：auto 時，Claude 訂閱達到 5 小時上限且 Anthropic 提供該通道便自動切換；也可在 Anthropic 模型上用 /slow on|off 切換。",
	},
	"providers.openaiLiveSteering": {
		label: "OpenAI 即時引導",
		description:
			"在 GPT-6 響應流式輸出時，通過 Codex WebSocket 把此刻輸入的訊息直接送入該響應，而不必等到下一個工具邊界。",
	},
	"providers.muse-code.storeResponses": {
		label: "Muse Code 服務端存稿",
		description:
			"把 Muse Code 結果儲存在 Meta 伺服器上，連線中斷的輪次可以恢復而非重跑；儲存的執行會在 Meta 側保留提示詞和輸出。",
	},
	"providers.cacheWarming": {
		label: "快取保溫",
		description: "在提示詞快取條目即將過期前，以單 token 輸出預算重發上一次請求",
	},
	"claudeResets.autoRedeem": {
		label: "Claude 重置自動兌換",
		description:
			"自動使用符合條件的 Claude Cedar 或 Juniper 重置額度。Cedar 僅用於其覆寫的限額；Juniper 只能恢復單獨的 5 小時封鎖。unset 在首次使用前詢問（無提示介面時僅使用 5 分鐘內過期的重置）；yes 不詢問直接使用；no 停用封鎖恢復與過期打撈。",
	},
	"claudeResets.minBlockedMinutes": {
		label: "Claude 自動兌換最小封鎖時長",
		description:
			"僅當自然解封——已耗盡的受覆寫視窗中最晚的重置——距今至少此分鐘數時才自動兌換；單獨的 5 小時重置絕不會用於每週或按模型的封鎖。",
	},
	"claudeResets.keepCredits": {
		label: "Claude 自動兌換保留量",
		description:
			"至少保留此數量的 Claude 重置額度（0 表示最後一個符合條件的也可自動用掉）；保留量適用於提前打撈，但不適用於 5 分鐘內過期的重置。",
	},
	"claudeResets.salvageHorizonHours": {
		label: "Claude 重置打撈視窗",
		description:
			"啟用自動兌換時，當伺服器選擇的 Cedar 重置將在此小時數內過期、且其覆寫視窗有可恢復的用量時提前用掉；0 停用提前打撈。無論用量或保留量如何，5 分鐘內過期的符合條件重置仍會被嘗試；服務商限額要求仍然適用。",
	},
	"telemetry.otlpExportEnabled": {
		label: "OTLP 遙測匯出",
		description: "允許 OMP 通過 OTEL_* 端點匯出 trace、日誌與指標；更改在下次啟動時生效。",
	},
	// advisor
	"advisor.reviewMode": {
		label: "顧問審查模式",
		description: "沒有 WATCHDOG.yml 名單時的預設顧問節奏：turn 審查每個主輪次；agent-end 僅在最終產出時審查。",
	},
	"advisor.reviewInterval": {
		label: "顧問審查間隔",
		description:
			"沒有 WATCHDOG.yml 名單時的預設顧問節奏：每第 N 次符合條件的主更新審查一次；1 = 每次更新；跳過的更新隨下一次計劃的審查一併傳送。",
	},
	"advisor.evictStaleResults": {
		label: "清理顧問過期結果",
		description: "每次審查前，用簡短佔位符替換顧問更早審查產生的 read/grep/glob 輸出；最近一次審查保留。",
	},
	// context / files
	"compaction.modelThresholds": {
		label: "按模型的壓縮閾值",
		description:
			"模型選擇器（provider/model-id 或 provider/…* 字首）到壓縮閾值的對映；可用 token 數或百分比，覆寫全域閾值。",
	},
	"compaction.modelThresholdsEnabled": {
		label: "啟用按模型的壓縮閾值",
		description: "控制 compaction.modelThresholds 對映是否生效。",
	},
	"ttsr.judge": {
		label: "判定規則（judge）",
		description:
			"讓 judge 模型角色對每條 `question` 規則評判已完成的回覆、推理與工具呼叫；判定為是則把該規則注入為警告。",
	},
	"edit.modelVariants": {
		label: "按模型的編輯變體",
		description:
			"模型選擇器模式到編輯工具變體（replace、patch、hashline、apply_patch、sloppy）的對映；首個匹配生效。",
	},
	// tools / tasks
	"tools.artifactMaxBytes": {
		label: "Artifact 檔案上限（MB）",
		description:
			"為流式工具輸出（bash、python、js eval）儲存的 artifact 檔案最大體積；超出時保留開頭（最多 3 MB）與最新的末尾，中間以截斷提示分隔。0 = 不限。",
	},
	"ratchet.enabled": {
		label: "Ratchet",
		description: "啟用 ratchet eval/調優前奏；/ratchet 可為目前工作階段開啟。",
	},
	"archive.enabled": {
		label: "Archive（歸檔）",
		description: "啟用只讀的 archive eval 前奏：提示詞歷史、最近專案、過往工作階段與回顧。",
	},
	"eval.autoProvision": {
		label: "Eval 環境自動設定",
		description: "首次安裝時自動建立託管的 JavaScript eval 包環境。",
	},
	"worktree.onStart": {
		label: "啟動時建 Worktree",
		description: "新的互動式工作階段是否在新的關聯 worktree 中開始。",
	},
	"worktree.onExit": {
		label: "結束時處理 Worktree",
		description: "結束時如何處理 omp 啟動以來（啟動時或通過 /wt）建立的 worktree。",
	},
	"task.speculativeLaunch": {
		label: "投機式任務啟動",
		description:
			"批次子代理在其 tasks[] 項流式解析完成時立即啟動，而不等待整個 task 呼叫結束；若最終呼叫校驗失敗、被阻止或引數變化，已啟動的 agent 會被中止。需要 task 自動批准且沒有擴充套件工具生命週期處理器。",
	},
	"task.completionProbe": {
		label: "子代理完成度探測",
		description:
			"通過類似 /btw 的快取旁路請求，詢問執行中的子代理任務完成度：分別在 2、5、10、30 分鐘後及此後每小時估算一次；估算值顯示在 wait 與 task 檢視中。僅互動式工作階段主 Agent 派生的子代理會被詢問；print、RPC、ACP 與 SDK 執行從不探測。",
	},
	"task.agentCompactionThresholdOverrides": {
		label: "按 agent 的壓縮閾值覆寫",
		description: "agent 名稱到壓縮閾值的對映；命中時覆寫 compaction.modelThresholds 與全域閾值。",
	},
	"task.agentAccountPools": {
		label: "按 agent 的賬號池",
		description: "agent 名稱到可用 OAuth 賬號（按服務商列出身份鍵）的對映；限制該子代理只能使用列出的賬號。",
	},
	"title.icons": {
		label: "標題圖示",
		description: "新生成或 /rename 工作階段標題前新增的圖示與短程式碼。",
	},
	"title.generator": {
		label: "標題生成器",
		description: "根據使用者訊息為未命名工作階段命名的方式。",
	},
	"skills.registryUrl": {
		label: "技能登錄檔",
		description: "`omp skill` 用於安裝、搜尋與釋出技能的 Skillshare 登錄檔（https://host[:port]）。",
	},
	"browser.tern": {
		label: "Tern 瀏覽器",
		description:
			"在 Tern 面板中把瀏覽器標籤以畫中畫覆寫在 omp 面板上（原生 WebView），而非無頭 Chromium；無可用 Tern 視窗時回退 Chromium。顯式 app 選項、relay 與瀏覽器 CDP URL 優先；app.tern:false 可單獨結束。可用 PI_BROWSER_TERN=0 或 =1 覆寫。",
	},
	"ida.enabled": {
		label: "IDA Pro",
		description: "用 IDA Pro（idalib）開啟 read 讀取的執行檔並啟用 ida 工具；未找到 IDA 安裝時無效。",
	},
	"ida.python": {
		label: "IDA Python",
		description: "能匯入 ida_domain 與 idapro 的 Python 直譯器；留空自動偵測。",
	},
	"ida.installDir": {
		label: "IDA 安裝目錄",
		description: "包含 libidalib 的目錄，匯出為 IDADIR；留空自動偵測（$IDADIR、ida-config.json、標準安裝路徑）。",
	},
	"ida.maxOpen": {
		label: "IDA 同時開啟上限",
		description:
			"每個專案最多同時開啟的 IDA 資料庫數（omp ps 中的 omp.ida.* 常駐程式）；再開啟時儲存並關閉最久未用的空閒庫。",
	},
	"ida.idleCloseSec": {
		label: "IDA 空閒關閉超時",
		description: "空閒超過此秒數的 IDA 資料庫將被儲存並關閉（0 = 從不）；exec 名稱空間在重新開啟時重置。",
	},
	"mcp.startupTimeoutMs": {
		label: "MCP 啟動等待視窗",
		description: "等待初始 MCP 工具發現的毫秒數；0 表示一直等到連線就緒。",
	},
	// advanced（無 ui 後設資料，歸入 Advanced 選項卡）
	"auth.accountPolicies": {
		label: "賬號策略",
		description: "按賬號的認證路由與配額策略（JSON 陣列），通常由 omp auth-gateway / usage 工作流寫入。",
	},
	modelPresets: {
		label: "模型預設",
		description: "命名模型預設的對映；由 /modelpreset 命令與模型中心管理。",
	},
	"gc.stale": {
		label: "GC 清理陳舊檔案",
		description: "`omp gc --apply` 時同時刪除陳舊的使用者可見檔案（過期除錯報告、協作副本、懸空標記等）；預設關閉。",
	},
	"gc.staleRetainNewest": {
		label: "陳舊清理保留最新數",
		description: "陳舊清理階段始終保留的最新條目數（預設 20）。",
	},
	"gc.staleRetainDays": {
		label: "陳舊清理保留天數",
		description: "陳舊清理保留此天數內的條目（預設 30）。",
	},
	"advisor.continueSeverity": {
		label: "顧問喚醒級別",
		description:
			"顧問批註在 Agent 已給出最終答覆後喚醒它所需的最低級別；低於此級別的批註只作為卡片留在轉錄末尾，隨你的下一條訊息送達 Agent。",
	},
	"computer.backgroundFallback": {
		label: "後臺輸入降級",
		description:
			"視窗輸入的後臺通道不可用時的處理方式：以接管方式重跑並把焦點還給你的應用（macOS；其他平臺為普通接管），或拒絕——同時阻止 Agent 自行搶佔前臺或開啟 macOS 選單。",
	},
	"task.structured": {
		label: "結構化任務結果",
		description:
			"在 task 工具上暴露 outputSchema/schemaMode，子代理結果通過 yield 工具回傳並按呼叫方或 agent 的輸出 schema 校驗。關閉時 task 子代理沒有 yield 工具、以純文本回傳最終訊息（定義中設 structured: true 的 agent 除外）；eval agent()/workpool 產生的子代理始終回傳結構化結果。",
	},
	"task.agentSoftRequestBudget": {
		label: "按 Agent 的軟請求預算",
		description: "按 agent 名覆寫 task.softRequestBudget 的對映；某 agent 的值為 0 時關閉其預算保護。",
	},
	"sharpshooter.minPromptLength": {
		label: "Sharpshooter 最短訊息長度",
		description: "短於此字元數的使用者訊息跳過 Sharpshooter 提取（預設 16）。",
	},
	"gc.compress": {
		label: "壓縮冷工作階段檔案",
		description: "通過檔案系統透明壓縮（APFS、NTFS）就地重寫冷工作階段檔案；需顯式開啟。",
	},
	"gc.compressAfterDays": {
		label: "壓縮閒置天數",
		description: "壓縮閒置超過此天數的工作階段檔案（預設 7）。",
	},
	// omp 18.14–18.15
	"btw.inject": {
		label: "/btw 引導注入",
		description:
			"讓 /btw 起草引導提示時，把它放在 <inject> 標籤中並在回答裡高亮；按 Alt+I（app.btw.inject）將其傳送到主工作階段。",
	},
	"hindsight.globalScope": {
		label: "Hindsight 全域作用域",
		description:
			"允許 retain 和 learn 使用 scope: global，不帶專案標籤儲存記憶，所有專案都能召回。需要 global 或 per-project-tagged 作用域。",
	},
	"judgment.attemptTimeoutMs": {
		label: "判斷模型嘗試超時（毫秒）",
		description: "設定了備用模型時，判斷模型超過此時長（預設 3000 毫秒）未完成即改用備用模型，並短暫跳過超時的路由。",
	},
	"prewalk.from": {
		label: "Prewalk 規劃模型",
		description: "/prewalk restart 回傳用於規劃的模型或角色（預設 '@default'）。",
	},
	"prewalk.into": {
		label: "Prewalk 目標",
		description:
			"Prewalk 在首次編輯/寫入時交接到的模型或角色（預設 '@smol'），用於 /prewalk、/prewalk restart、啟用 Prewalk 和 --prewalk。自動 Prewalk 使用自己的目標。",
	},
	"providers.openai-codex.daybreak": {
		label: "Codex Daybreak Blue",
		description:
			"在符合條件的 ChatGPT 賬號上自動申請 Daybreak Blue 網路安全訪問計劃。OpenAI 可能使用 Daybreak Blue 工作階段內容改進模型。不影響專用 Daybreak Blue 模型（gpt-daybreak-blue-*），它們仍可能以 Daybreak 工作階段執行。",
	},
	"task.perCallModel": {
		label: "按呼叫指定模型",
		description:
			"是否允許子代理呼叫用一個精確的 provider/model-id[@upstream][:level] 選擇器指定模型。@upstream 固定屬於模型身份，僅聚合服務支援。只接受設定中已可路由的模型。專案設定只能關閉、不能開啟，也不能批准模型。",
	},
	"task.perCallModelAllow": {
		label: "按呼叫模型允許列表",
		description:
			"精確選擇器：`provider/model-id`，僅固定的 OpenRouter/Vercel 路由可帶 `@upstream`（如 `openrouter/x@y`）。設定後，按呼叫指定的模型還必須在此列表中。留空表示設定允許的所有模型。專案列表只能進一步收窄。",
	},
	"title.refreshAfterPrompts": {
		label: "每 N 次提示重新整理標題",
		description:
			"單位是你傳送的提示次數，不是時間；0 表示關閉。每隔這麼多次提示，讓判斷模型檢查自動生成的工作階段標題是否仍符合對話，不符合時重新生成。你自己設定的標題不會被替換。",
	},
};
