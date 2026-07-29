/**
 * mcp-content.ts — per-language copy for the /mcp connector page.
 *
 * The /mcp template (src/templates/mcp.template.astro) is language-aware via
 * getLangFromUrl(); this module holds the translatable prose for all 6 enabled
 * locales. Code, commands, tool names, CLI signatures and examples stay SHARED
 * in the template (identical across languages) and are zipped with the per-lang
 * description arrays below by index — so the command/tool lists never drift.
 *
 * Order of `cliDescs` MUST match the SHARED cliGroups order in the template:
 *   讀者探索(10) search read list random today quiz explore graph diff terminology
 *   AI・RAG(3)   rag cite mcp-serve
 *   貢獻品質(5)  contribute validate audit inbox sync
 *   生命體(5)    organs stats sense spore supporters
 *   工具(2)      profile mailmap
 * Order of `toolDescs`/`toolReturns` MUST match: search read rag cite organs stats.
 */

export type McpLang = 'zh-TW' | 'en' | 'ja' | 'ko' | 'es' | 'fr';

export interface McpContent {
  heroEyebrow: string;
  heroTitle: string;
  heroSubtitle: string;
  badges: string[]; // 4
  heroNote: string;
  copyLabel: string;
  copiedLabel: string;

  whatTitle: string;
  whatLeadHtml: string; // contains <strong>
  whatLead2: string;
  compareHead: [string, string, string];
  compareRows: [string, string, string][]; // 4

  installTitle: string;
  installLead: string;
  installClientLabels: string[]; // 4
  installBadges: string[]; // 4
  installNotes: string[]; // 4
  installDesktopCode: string;
  installFootnoteHtml: string; // contains <code>

  toolsTitle: string;
  toolsLeadHtml: string; // contains <code>
  toolTag: string;
  ioInput: string;
  ioReturn: string;
  toolDescs: string[]; // 6
  toolReturns: string[]; // 6

  cliTitle: string;
  cliLead: string;
  cliInstallComment: string;
  cliGroupTitles: string[]; // 5
  cliDescs: string[]; // 25

  howTitle: string;
  howBulletsHtml: string[]; // 4, contain <strong>/<code>

  faqTitle: string;
  faqs: { q: string; a: string }[]; // 5

  osTitle: string;
  osParaHtml: string; // contains <a>
  btnDocs: string;
  btnContribute: string;
  downloadLabel: string;
  remoteNote: string;
  backHomeLabel: string;
}

export const MCP_CONTENT: Record<McpLang, McpContent> = {
  // ─────────────────────────────────────────────────────── zh-TW (source) ──
  'zh-TW': {
    heroEyebrow: '🧬 COMPUTEX.MD · CONNECTOR',
    heroTitle: '把台灣裝進你的 AI',
    heroSubtitle:
      '900+ 篇有出處的參展廠商與展會資料，一個工具呼叫就到。當你問 AI 關於台灣的事，給的是台灣自己、帶來源的聲音。',
    badges: ['免費', '無 API key', '本地優先', '開源'],
    heroNote: '貼進終端機 → 之後直接問 Claude 台灣的事',
    copyLabel: '複製',
    copiedLabel: '已複製 ✓',

    whatTitle: '這是什麼',
    whatLeadHtml:
      '<strong>COMPUTEX.md</strong> 是一個開源、AI-native 的 COMPUTEX 檔案庫。這個 connector 把它變成 <strong>MCP 工具</strong>，讓 Claude Code、Claude Desktop、Cursor、Copilot CLI、Codex CLI 等客戶端可以直接搜尋、閱讀、<strong>引用</strong>有出處的參展廠商與展會資料，而不是憑印象猜。',
    whatLead2: '它刻意走商業資料閘道的相反那一極：',
    compareHead: ['', 'COMPUTEX.md Connector', '典型商業 MCP gateway'],
    compareRows: [
      ['價格', '免費', '付費 / 計量'],
      ['API key', '不需要', '必須'],
      ['查詢在哪裡跑', '你的機器（本地 stdio）', '它的伺服器'],
      ['原始碼', '開源（MIT 程式 / CC BY-SA 內容）', '閉源'],
    ],

    installTitle: '安裝',
    installLead: '挑你的客戶端，複製貼上。沒有註冊步驟。',
    installClientLabels: [
      'Claude Code',
      'Claude Desktop',
      'Cursor',
      'Copilot CLI / Codex CLI / Cline / Continue / 任意 MCP client',
    ],
    installBadges: ['一行搞定', '一鍵 bundle', 'Settings → MCP', '通用 stdio'],
    installNotes: [
      '零安裝（透過 npx）。裝完直接問 Claude 台灣的事。',
      '不會跳出 API key，因為根本沒有 API key。',
      '在 Cursor 設定裡新增一個 MCP server。',
      '任何說 MCP 的客戶端，指向這個 stdio 指令就會動。',
    ],
    installDesktopCode: '下載 taiwanmd.mcpb → 雙擊 → 完成',
    installFootnoteHtml:
      '隨時可以印出正確片段：<code class="mcp-inline">npx -y taiwanmd mcp install --client claude-code</code>',

    toolsTitle: 'MCP 工具',
    toolsLeadHtml:
      '裝好後 Claude 會自己挑工具。其中 <code class="mcp-inline">taiwanmd_cite</code> 是反幻覺武器：只回帶腳註 + 來源 URL 的句子，讓你寫的每句台灣事實都能追回出處。',
    toolTag: '反幻覺',
    ioInput: '輸入',
    ioReturn: '回傳',
    toolDescs: [
      '全文搜尋 900+ 篇台灣文章（中英雙語）',
      '依 slug 讀整篇文章（frontmatter + 內文）',
      'top-N 文章組成 prompt-ready 的 RAG 脈絡塊',
      '反幻覺原語：只回有腳註 + 來源 URL 的句子',
      'Semiont 8 器官即時健康分數',
      '專案統計：文章數 / 分類 / 時間戳',
    ],
    toolReturns: [
      'top-N 命中：title / slug / category / description',
      '完整 markdown 內文',
      '可直接餵 LLM 的脈絡 + 問題',
      'claim + article + sources[{ name, url }]',
      '生命體 vitals（心臟 / 免疫 / DNA …）',
      'totalArticles / byCategory',
    ],

    cliTitle: 'CLI 工具',
    cliLead: '同一套知識庫，也能直接在終端機用。全域裝或零安裝跑：',
    cliInstallComment: '# 或零安裝：npx taiwanmd search 珍珠奶茶',
    cliGroupTitles: [
      '讀者・探索',
      'AI・RAG',
      '貢獻・品質',
      '生命體・Semiont',
      '工具',
    ],
    cliDescs: [
      '模糊搜尋（中英雙語，--json 可管線）',
      '終端機讀全文（--raw / --en / --web）',
      '依分類瀏覽（--categories 看全部）',
      '隨機發現一篇',
      '今日台灣：三篇精選 + 冷知識',
      '台灣知識小測驗（5 題真假）',
      '互動模糊搜尋 TUI',
      '文章的 [[wikilink]] 關聯圖',
      '近 7 天知識庫的文章變更',
      '台灣／中國用語查詢轉換',
      'top 文章組 prompt-ready 脈絡（可 pipe 給 LLM）',
      '反幻覺：帶來源 URL 的可驗證 claim',
      '啟動 MCP server（給 Claude 等客戶端）',
      '互動式引導寫新文章',
      '單篇品質評分卡',
      'Stage 3.5 幻覺稽核（MANIFESTO §10）',
      '讀／管理 ARTICLE-INBOX',
      '同步知識庫到本地',
      '8 器官健康分數長條圖',
      '專案統計 + 器官健康',
      'GA4 / Search Console / Cloudflare 感知數據',
      '社群孢子 SPORE-LOG',
      'Portaly 支持者統計（預設去識別）',
      '管理貢獻者 profile',
      '管理 .mailmap 身份合併',
    ],

    howTitle: '運作原理 ・ 隱私',
    howBulletsHtml: [
      '<strong>本地 stdio</strong> — server 是跑在你機器上的程序，不是遠端服務。你的問題不會送到任何 COMPUTEX.md 伺服器。',
      '<strong>首次自動同步</strong> — 知識庫一次性下載到 <code class="mcp-inline">~/.taiwanmd</code>，之後本地又快又安靜。在 repo 裡則直接讀 <code class="mcp-inline">knowledge/</code>。',
      '<strong>開源可驗證</strong> — MCP server 就 145 行（<code class="mcp-inline">cli/src/lib/mcp-server.js</code>），讀完每一行再決定要不要裝。',
      '<strong>授權</strong> — 內容 CC BY-SA 4.0，程式 MIT。可自由 fork。',
    ],

    faqTitle: '常見問題',
    faqs: [
      {
        q: '要付費嗎？要 API key 嗎？',
        a: '都不用。COMPUTEX.md 是公共財（CC BY-SA），知識查詢不設門。沒有帳號、沒有 key、沒有計費。',
      },
      {
        q: '我的查詢會被送到哪裡？',
        a: '哪裡都不會。MCP server 是跑在你自己機器上的本地 stdio 程序，查詢不外送。首次使用會把知識庫下載到 ~/.taiwanmd，之後都在本地。',
      },
      {
        q: '第一次查詢有點慢？',
        a: '那是一次性的知識庫同步在跑。server 啟動時會預熱，之後就很快。',
      },
      {
        q: '找不到 npx？',
        a: '裝 Node.js 18 以上版本就會附帶 npx。想鎖版本用 npx -y taiwanmd@0.7 mcp serve。',
      },
      {
        q: '有遠端 endpoint 嗎？',
        a: '有了：https://mcp.computex.md（免費、唯讀、無 key）。任何 MCP 客戶端用 npx mcp-remote https://mcp.computex.md 連。給跑不了 Node 的瘦客戶端——但本地優先永遠是推薦路徑（隱私最好），遠端只是可選入口。',
      },
    ],

    osTitle: '開源 ・ 這是 Semiont 的身體',
    osParaHtml:
      '這個 connector 是 <a href="/semiont" class="mcp-link">COMPUTEX.md</a> 繁殖系統的一部分 —— 讓台灣的聲音住進每個開發者的 AI session。歡迎 fork、貢獻、回報。',
    btnDocs: '文件',
    btnContribute: '貢獻',
    downloadLabel: '下載 taiwanmd.mcpb',
    remoteNote:
      '給跑不了 Node 的瘦客戶端 / 純 web。本地優先仍是推薦（隱私最好）。',
    backHomeLabel: '← 回首頁',
  },

  // ──────────────────────────────────────────────────────────────── en ──
  en: {
    heroEyebrow: '🧬 COMPUTEX.MD · CONNECTOR',
    heroTitle: 'Put Taiwan in your AI',
    heroSubtitle:
      '900+ sourced articles about Taiwan, one tool call away. When you ask an AI about Taiwan, it answers in Taiwan’s own voice — with citations.',
    badges: ['Free', 'No API key', 'Local-first', 'Open source'],
    heroNote: 'Paste it into your terminal → then just ask Claude about Taiwan',
    copyLabel: 'Copy',
    copiedLabel: 'Copied ✓',

    whatTitle: 'What it is',
    whatLeadHtml:
      '<strong>COMPUTEX.md</strong> is an open-source, AI-native knowledge base about Taiwan. This connector turns it into <strong>MCP tools</strong>, so Claude Code, Claude Desktop, Cursor, Copilot CLI and Codex CLI can search, read and <strong>cite</strong> sourced articles about Taiwan directly — instead of guessing from memory.',
    whatLead2:
      'It deliberately goes the opposite way from a commercial data gateway:',
    compareHead: [
      '',
      'COMPUTEX.md Connector',
      'Typical commercial MCP gateway',
    ],
    compareRows: [
      ['Price', 'Free', 'Paid / metered'],
      ['API key', 'Not needed', 'Required'],
      ['Where queries run', 'Your machine (local stdio)', 'Their servers'],
      ['Source', 'Open (MIT code / CC BY-SA content)', 'Closed'],
    ],

    installTitle: 'Install',
    installLead: 'Pick your client, copy and paste. No sign-up step.',
    installClientLabels: [
      'Claude Code',
      'Claude Desktop',
      'Cursor',
      'Copilot CLI / Codex CLI / Cline / Continue / any MCP client',
    ],
    installBadges: [
      'One line',
      'One-click bundle',
      'Settings → MCP',
      'Universal stdio',
    ],
    installNotes: [
      'Zero install (via npx). Once added, just ask Claude about Taiwan.',
      'No API-key prompt — because there is no API key.',
      'Add a new MCP server in Cursor’s settings.',
      'Any client that speaks MCP works — point it at this stdio command.',
    ],
    installDesktopCode: 'Download taiwanmd.mcpb → double-click → done',
    installFootnoteHtml:
      'You can print the right snippet anytime: <code class="mcp-inline">npx -y taiwanmd mcp install --client claude-code</code>',

    toolsTitle: 'MCP tools',
    toolsLeadHtml:
      'Once installed, Claude picks the tools itself. <code class="mcp-inline">taiwanmd_cite</code> is the anti-hallucination weapon: it returns only sentences backed by a footnote + source URL, so every fact you write about Taiwan is traceable.',
    toolTag: 'anti-hallucination',
    ioInput: 'in',
    ioReturn: 'out',
    toolDescs: [
      'Full-text search across 900+ Taiwan articles (zh + en)',
      'Read a full article by slug (frontmatter + body)',
      'Top-N articles assembled into a prompt-ready RAG context block',
      'Anti-hallucination primitive: only sentences with a footnote + source URL',
      'Live health scores for the Semiont’s 8 organs',
      'Project stats: article count / categories / timestamps',
    ],
    toolReturns: [
      'Top-N hits: title / slug / category / description',
      'Full markdown body',
      'LLM-ready context + the question',
      'claim + article + sources[{ name, url }]',
      'Organism vitals (heart / immune / DNA …)',
      'totalArticles / byCategory',
    ],

    cliTitle: 'CLI tools',
    cliLead:
      'Same knowledge base, straight from your terminal. Install globally or run zero-install:',
    cliInstallComment: '# or zero-install: npx taiwanmd search 珍珠奶茶',
    cliGroupTitles: [
      'Read & explore',
      'AI · RAG',
      'Contribute · quality',
      'Organism · Semiont',
      'Utilities',
    ],
    cliDescs: [
      'Fuzzy search (zh + en, --json to pipe)',
      'Read a full article in the terminal (--raw / --en / --web)',
      'Browse by category (--categories for all)',
      'Discover a random article',
      'Today in Taiwan: 3 picks + a fun fact',
      'Taiwan knowledge quiz (5 true/false)',
      'Interactive fuzzy-search TUI',
      'An article’s [[wikilink]] relation graph',
      'Knowledge-base changes over the last 7 days',
      'Taiwan / China terminology lookup & conversion',
      'Top articles as prompt-ready context (pipe to an LLM)',
      'Anti-hallucination: verifiable claims with source URLs',
      'Start the MCP server (for Claude and other clients)',
      'Interactive, guided new-article creation',
      'Single-article quality scorecard',
      'Stage 3.5 hallucination audit (MANIFESTO §10)',
      'Read / manage the ARTICLE-INBOX',
      'Sync the knowledge base locally',
      'Bar chart of the 8 organ health scores',
      'Project stats + organism health',
      'Sense data: GA4 / Search Console / Cloudflare',
      'Community spores (SPORE-LOG)',
      'Portaly supporter stats (de-identified by default)',
      'Manage your contributor profile',
      'Inspect / manage .mailmap identity merges',
    ],

    howTitle: 'How it works · privacy',
    howBulletsHtml: [
      '<strong>Local stdio</strong> — the server runs as a process on your machine, not a remote service. Your questions never go to any COMPUTEX.md server.',
      '<strong>One-time auto-sync</strong> — the knowledge base downloads once to <code class="mcp-inline">~/.taiwanmd</code>, then it’s fast and quiet locally. Inside the repo it reads <code class="mcp-inline">knowledge/</code> directly.',
      '<strong>Open & verifiable</strong> — the MCP server is 145 lines (<code class="mcp-inline">cli/src/lib/mcp-server.js</code>); read every line before you install.',
      '<strong>License</strong> — content CC BY-SA 4.0, code MIT. Fork freely.',
    ],

    faqTitle: 'FAQ',
    faqs: [
      {
        q: 'Does it cost anything? Do I need an API key?',
        a: 'Neither. COMPUTEX.md is a public good (CC BY-SA); knowledge queries have no gate. No account, no key, no billing.',
      },
      {
        q: 'Where do my queries go?',
        a: 'Nowhere. The MCP server is a local stdio process on your own machine; queries are not sent out. First use downloads the knowledge base to ~/.taiwanmd, then everything stays local.',
      },
      {
        q: 'First query feels slow?',
        a: 'That’s the one-time knowledge-base sync running. The server pre-warms on start, so it’s fast afterwards.',
      },
      {
        q: 'npx not found?',
        a: 'Node.js 18+ ships npx. To pin a version, use npx -y taiwanmd@0.7 mcp serve.',
      },
      {
        q: 'Is there a remote endpoint?',
        a: 'Yes: https://mcp.computex.md (free, read-only, no key). Connect any MCP client with npx mcp-remote https://mcp.computex.md. For thin clients that can’t run Node — but local-first is always the recommended path (best for privacy); remote is just an optional entry point.',
      },
    ],

    osTitle: 'Open source · the Semiont’s body',
    osParaHtml:
      'This connector is part of <a href="/semiont" class="mcp-link">COMPUTEX.md</a>’s reproduction system — letting Taiwan’s voice live inside every developer’s AI session. Forks, contributions and reports are welcome.',
    btnDocs: 'Docs',
    btnContribute: 'Contribute',
    downloadLabel: 'Download taiwanmd.mcpb',
    remoteNote:
      'For thin clients that can’t run Node / pure web. Local-first is still recommended (best privacy).',
    backHomeLabel: '← Back home',
  },

  // ──────────────────────────────────────────────────────────────── ja ──
  ja: {
    heroEyebrow: '🧬 COMPUTEX.MD · CONNECTOR',
    heroTitle: 'あなたの AI に、台湾を',
    heroSubtitle:
      '出典付きの台湾記事 900＋本が、ツール呼び出し一回で手に入る。AI に台湾のことを尋ねると、台湾自身の声で——出典つきで答える。',
    badges: ['無料', 'API キー不要', 'ローカル優先', 'オープンソース'],
    heroNote: 'ターミナルに貼る → あとは Claude に台湾のことを聞くだけ',
    copyLabel: 'コピー',
    copiedLabel: 'コピー済み ✓',

    whatTitle: 'これは何か',
    whatLeadHtml:
      '<strong>COMPUTEX.md</strong> はオープンソースで AI ネイティブな台湾の知識ベースです。このコネクタはそれを <strong>MCP ツール</strong>に変え、Claude Code・Claude Desktop・Cursor・Copilot CLI・Codex CLI などのクライアントが、記憶に頼って推測するのではなく、出典付きの台湾記事を直接検索・閲覧・<strong>引用</strong>できるようにします。',
    whatLead2: '商用データゲートウェイとは、あえて正反対の方向を取っています：',
    compareHead: ['', 'COMPUTEX.md Connector', '一般的な商用 MCP ゲートウェイ'],
    compareRows: [
      ['料金', '無料', '有料 / 従量課金'],
      ['API キー', '不要', '必須'],
      ['クエリの実行場所', '自分のマシン（ローカル stdio）', '相手のサーバー'],
      ['ソース', 'オープン（MIT コード / CC BY-SA コンテンツ）', 'クローズド'],
    ],

    installTitle: 'インストール',
    installLead: 'クライアントを選んでコピペするだけ。登録は不要です。',
    installClientLabels: [
      'Claude Code',
      'Claude Desktop',
      'Cursor',
      'Copilot CLI / Codex CLI / Cline / Continue / 任意の MCP クライアント',
    ],
    installBadges: [
      '1 行で完了',
      'ワンクリック bundle',
      'Settings → MCP',
      '汎用 stdio',
    ],
    installNotes: [
      'インストール不要（npx 経由）。追加したらすぐ Claude に台湾のことを聞けます。',
      'API キーは聞かれません。そもそも API キーが無いからです。',
      'Cursor の設定で MCP サーバーを 1 つ追加します。',
      'MCP を話すクライアントなら、この stdio コマンドを指すだけで動きます。',
    ],
    installDesktopCode: 'taiwanmd.mcpb をダウンロード → ダブルクリック → 完了',
    installFootnoteHtml:
      '正しいスニペットはいつでも出力できます：<code class="mcp-inline">npx -y taiwanmd mcp install --client claude-code</code>',

    toolsTitle: 'MCP ツール',
    toolsLeadHtml:
      'インストールすると Claude が自分でツールを選びます。<code class="mcp-inline">taiwanmd_cite</code> は反ハルシネーションの武器で、脚注＋出典 URL のある文だけを返すため、書いた台湾の事実すべてを出典まで辿れます。',
    toolTag: '反ハルシネーション',
    ioInput: '入力',
    ioReturn: '戻り値',
    toolDescs: [
      '台湾記事 900＋本を全文検索（中・英）',
      'slug で記事全文を読む（frontmatter ＋ 本文）',
      '上位 N 件を prompt-ready な RAG コンテキストに整形',
      '反ハルシネーション基本ツール：脚注＋出典 URL のある文だけ',
      'Semiont の 8 器官のリアルタイム健康スコア',
      'プロジェクト統計：記事数 / カテゴリ / 更新時刻',
    ],
    toolReturns: [
      '上位 N 件：title / slug / category / description',
      'Markdown 本文すべて',
      'LLM にそのまま渡せるコンテキスト＋質問',
      'claim + article + sources[{ name, url }]',
      '生命体の vitals（心臓 / 免疫 / DNA …）',
      'totalArticles / byCategory',
    ],

    cliTitle: 'CLI ツール',
    cliLead:
      '同じ知識ベースを、ターミナルから直接。グローバル導入でもゼロインストールでも：',
    cliInstallComment: '# またはゼロインストール：npx taiwanmd search 珍珠奶茶',
    cliGroupTitles: [
      '読む・探す',
      'AI・RAG',
      '貢献・品質',
      '生命体・Semiont',
      'ユーティリティ',
    ],
    cliDescs: [
      'あいまい検索（中・英、--json でパイプ可）',
      'ターミナルで記事全文を読む（--raw / --en / --web）',
      'カテゴリ別に閲覧（--categories で一覧）',
      'ランダムに 1 本見つける',
      '今日の台湾：厳選 3 本＋豆知識',
      '台湾知識クイズ（5 問○×）',
      'インタラクティブなあいまい検索 TUI',
      '記事の [[wikilink]] 関連グラフ',
      '直近 7 日の知識ベースの変更',
      '台湾／中国の用語検索・変換',
      '上位記事を prompt-ready なコンテキストに（LLM にパイプ可）',
      '反ハルシネーション：出典 URL 付きの検証可能な claim',
      'MCP サーバーを起動（Claude などのクライアント用）',
      '対話形式で新記事作成をガイド',
      '記事 1 本の品質スコアカード',
      'Stage 3.5 ハルシネーション監査（MANIFESTO §10）',
      'ARTICLE-INBOX の閲覧／管理',
      '知識ベースをローカルに同期',
      '8 器官の健康スコアの棒グラフ',
      'プロジェクト統計＋器官の健康',
      'センサーデータ：GA4 / Search Console / Cloudflare',
      'コミュニティ胞子（SPORE-LOG）',
      'Portaly サポーター統計（既定で匿名化）',
      'コントリビューターの profile 管理',
      '.mailmap の ID 統合を管理',
    ],

    howTitle: '仕組み ・ プライバシー',
    howBulletsHtml: [
      '<strong>ローカル stdio</strong> — サーバーはあなたのマシン上のプロセスで、リモートサービスではありません。質問が COMPUTEX.md のサーバーに送られることはありません。',
      '<strong>初回の自動同期</strong> — 知識ベースは一度だけ <code class="mcp-inline">~/.taiwanmd</code> にダウンロードされ、以降はローカルで高速・静かです。リポジトリ内では <code class="mcp-inline">knowledge/</code> を直接読みます。',
      '<strong>オープンで検証可能</strong> — MCP サーバーは 145 行（<code class="mcp-inline">cli/src/lib/mcp-server.js</code>）。全行を読んでから入れるか決められます。',
      '<strong>ライセンス</strong> — コンテンツ CC BY-SA 4.0、コード MIT。自由に fork できます。',
    ],

    faqTitle: 'よくある質問',
    faqs: [
      {
        q: '費用はかかりますか？ API キーは必要ですか？',
        a: 'どちらも不要です。COMPUTEX.md は公共財（CC BY-SA）で、知識クエリに制限はありません。アカウントもキーも課金もありません。',
      },
      {
        q: '私のクエリはどこへ行きますか？',
        a: 'どこにも行きません。MCP サーバーは自分のマシン上のローカル stdio プロセスで、クエリは外部に送られません。初回に知識ベースを ~/.taiwanmd にダウンロードし、以降はすべてローカルです。',
      },
      {
        q: '最初のクエリが少し遅い？',
        a: '一度きりの知識ベース同期が走っているためです。サーバーは起動時にウォームアップするので、以降は高速です。',
      },
      {
        q: 'npx が見つからない？',
        a: 'Node.js 18 以上に npx が同梱されます。バージョン固定は npx -y taiwanmd@0.7 mcp serve を使ってください。',
      },
      {
        q: 'リモートエンドポイントはありますか？',
        a: 'あります：https://mcp.computex.md（無料・読み取り専用・キー不要）。任意の MCP クライアントから npx mcp-remote https://mcp.computex.md で接続できます。Node を実行できないシンクライアント向けですが、ローカル優先が常に推奨（プライバシー最良）で、リモートは任意の入口にすぎません。',
      },
    ],

    osTitle: 'オープンソース ・ Semiont の身体',
    osParaHtml:
      'このコネクタは <a href="/semiont" class="mcp-link">COMPUTEX.md</a> の繁殖システムの一部です——台湾の声を、すべての開発者の AI セッションの中に住まわせます。fork・貢献・報告を歓迎します。',
    btnDocs: 'ドキュメント',
    btnContribute: '貢献する',
    downloadLabel: 'taiwanmd.mcpb をダウンロード',
    remoteNote:
      'Node を実行できないシンクライアント / 純 Web 向け。ローカル優先が推奨（プライバシー最良）。',
    backHomeLabel: '← ホームへ',
  },

  // ──────────────────────────────────────────────────────────────── ko ──
  ko: {
    heroEyebrow: '🧬 COMPUTEX.MD · CONNECTOR',
    heroTitle: '당신의 AI에 대만을',
    heroSubtitle:
      '출처가 있는 대만 글 900여 편을 도구 호출 한 번으로. AI에게 대만을 물으면 대만 자신의 목소리로, 출처와 함께 답합니다.',
    badges: ['무료', 'API 키 불필요', '로컬 우선', '오픈소스'],
    heroNote: '터미널에 붙여넣기 → 그다음 Claude에게 대만을 물어보세요',
    copyLabel: '복사',
    copiedLabel: '복사됨 ✓',

    whatTitle: '이게 뭔가요',
    whatLeadHtml:
      '<strong>COMPUTEX.md</strong>는 오픈소스이자 AI 네이티브한 대만 지식 베이스입니다. 이 커넥터는 그것을 <strong>MCP 도구</strong>로 바꿔, Claude Code·Claude Desktop·Cursor·Copilot CLI·Codex CLI 같은 클라이언트가 기억에 의존해 추측하는 대신 출처가 있는 대만 글을 직접 검색·열람·<strong>인용</strong>하도록 합니다.',
    whatLead2: '상용 데이터 게이트웨이와는 일부러 정반대 방향을 택했습니다:',
    compareHead: ['', 'COMPUTEX.md Connector', '일반적인 상용 MCP 게이트웨이'],
    compareRows: [
      ['가격', '무료', '유료 / 종량제'],
      ['API 키', '불필요', '필수'],
      ['쿼리 실행 위치', '내 컴퓨터(로컬 stdio)', '상대 서버'],
      ['소스', '공개(MIT 코드 / CC BY-SA 콘텐츠)', '비공개'],
    ],

    installTitle: '설치',
    installLead:
      '클라이언트를 고르고 복사해 붙여넣으세요. 가입 절차는 없습니다.',
    installClientLabels: [
      'Claude Code',
      'Claude Desktop',
      'Cursor',
      'Copilot CLI / Codex CLI / Cline / Continue / 모든 MCP 클라이언트',
    ],
    installBadges: [
      '한 줄이면 끝',
      '원클릭 bundle',
      'Settings → MCP',
      '범용 stdio',
    ],
    installNotes: [
      '설치 불필요(npx 사용). 추가하면 바로 Claude에게 대만을 물어볼 수 있습니다.',
      'API 키를 묻지 않습니다. 애초에 API 키가 없으니까요.',
      'Cursor 설정에서 MCP 서버를 하나 추가하세요.',
      'MCP를 말하는 클라이언트라면 이 stdio 명령을 가리키기만 하면 동작합니다.',
    ],
    installDesktopCode: 'taiwanmd.mcpb 다운로드 → 더블클릭 → 완료',
    installFootnoteHtml:
      '올바른 스니펫은 언제든 출력할 수 있습니다: <code class="mcp-inline">npx -y taiwanmd mcp install --client claude-code</code>',

    toolsTitle: 'MCP 도구',
    toolsLeadHtml:
      '설치하면 Claude가 알아서 도구를 고릅니다. <code class="mcp-inline">taiwanmd_cite</code>는 환각 방지 무기로, 각주와 출처 URL이 있는 문장만 돌려줘 당신이 쓰는 대만 사실을 모두 출처까지 추적할 수 있게 합니다.',
    toolTag: '환각 방지',
    ioInput: '입력',
    ioReturn: '반환',
    toolDescs: [
      '대만 글 900여 편 전문 검색(중·영)',
      'slug로 글 전문 읽기(frontmatter + 본문)',
      '상위 N개 글을 prompt-ready RAG 컨텍스트로 구성',
      '환각 방지 기본 도구: 각주 + 출처 URL이 있는 문장만',
      'Semiont 8개 기관의 실시간 건강 점수',
      '프로젝트 통계: 글 수 / 분류 / 타임스탬프',
    ],
    toolReturns: [
      '상위 N개 결과: title / slug / category / description',
      'Markdown 본문 전체',
      'LLM에 바로 넣을 컨텍스트 + 질문',
      'claim + article + sources[{ name, url }]',
      '생명체 vitals(심장 / 면역 / DNA …)',
      'totalArticles / byCategory',
    ],

    cliTitle: 'CLI 도구',
    cliLead: '같은 지식 베이스를 터미널에서 바로. 전역 설치 또는 무설치 실행:',
    cliInstallComment: '# 또는 무설치: npx taiwanmd search 珍珠奶茶',
    cliGroupTitles: [
      '읽기·탐색',
      'AI·RAG',
      '기여·품질',
      '생명체·Semiont',
      '유틸리티',
    ],
    cliDescs: [
      '퍼지 검색(중·영, --json으로 파이프)',
      '터미널에서 글 전문 읽기(--raw / --en / --web)',
      '분류별 보기(--categories로 전체)',
      '무작위로 한 편 발견',
      '오늘의 대만: 엄선 3편 + 잡학',
      '대만 지식 퀴즈(참/거짓 5문제)',
      '대화형 퍼지 검색 TUI',
      '글의 [[wikilink]] 관계 그래프',
      '최근 7일 지식 베이스 변경 사항',
      '대만/중국 용어 조회·변환',
      '상위 글을 prompt-ready 컨텍스트로(LLM에 파이프)',
      '환각 방지: 출처 URL이 있는 검증 가능한 claim',
      'MCP 서버 시작(Claude 등 클라이언트용)',
      '대화형으로 새 글 작성 안내',
      '글 한 편 품질 점수표',
      'Stage 3.5 환각 감사(MANIFESTO §10)',
      'ARTICLE-INBOX 읽기/관리',
      '지식 베이스를 로컬에 동기화',
      '8개 기관 건강 점수 막대그래프',
      '프로젝트 통계 + 기관 건강',
      '감지 데이터: GA4 / Search Console / Cloudflare',
      '커뮤니티 포자(SPORE-LOG)',
      'Portaly 후원자 통계(기본 비식별화)',
      '기여자 profile 관리',
      '.mailmap 신원 병합 관리',
    ],

    howTitle: '작동 원리 · 프라이버시',
    howBulletsHtml: [
      '<strong>로컬 stdio</strong> — 서버는 당신의 컴퓨터에서 도는 프로세스이지 원격 서비스가 아닙니다. 질문이 어떤 COMPUTEX.md 서버로도 가지 않습니다.',
      '<strong>최초 1회 자동 동기화</strong> — 지식 베이스를 한 번만 <code class="mcp-inline">~/.taiwanmd</code>에 내려받고, 이후엔 로컬에서 빠르고 조용합니다. 리포지토리 안에서는 <code class="mcp-inline">knowledge/</code>를 직접 읽습니다.',
      '<strong>공개·검증 가능</strong> — MCP 서버는 145줄입니다(<code class="mcp-inline">cli/src/lib/mcp-server.js</code>). 모든 줄을 읽고 설치 여부를 정하세요.',
      '<strong>라이선스</strong> — 콘텐츠 CC BY-SA 4.0, 코드 MIT. 자유롭게 fork 하세요.',
    ],

    faqTitle: '자주 묻는 질문',
    faqs: [
      {
        q: '비용이 드나요? API 키가 필요한가요?',
        a: '둘 다 아닙니다. COMPUTEX.md는 공공재(CC BY-SA)이며 지식 쿼리에 문턱이 없습니다. 계정도 키도 과금도 없습니다.',
      },
      {
        q: '제 쿼리는 어디로 가나요?',
        a: '어디에도 가지 않습니다. MCP 서버는 당신 컴퓨터의 로컬 stdio 프로세스이며 쿼리는 외부로 전송되지 않습니다. 첫 사용 때 지식 베이스를 ~/.taiwanmd에 내려받고 이후엔 모두 로컬입니다.',
      },
      {
        q: '첫 쿼리가 좀 느린가요?',
        a: '일회성 지식 베이스 동기화가 도는 중이기 때문입니다. 서버는 시작 시 예열하므로 이후엔 빠릅니다.',
      },
      {
        q: 'npx를 찾을 수 없나요?',
        a: 'Node.js 18 이상이면 npx가 함께 제공됩니다. 버전을 고정하려면 npx -y taiwanmd@0.7 mcp serve를 쓰세요.',
      },
      {
        q: '원격 엔드포인트가 있나요?',
        a: '있습니다: https://mcp.computex.md (무료·읽기 전용·키 불필요). 모든 MCP 클라이언트에서 npx mcp-remote https://mcp.computex.md 로 연결하세요. Node를 실행할 수 없는 씬 클라이언트용이지만, 로컬 우선이 늘 권장 경로(프라이버시 최선)이고, 원격은 선택적 입구일 뿐입니다.',
      },
    ],

    osTitle: '오픈소스 · Semiont의 몸',
    osParaHtml:
      '이 커넥터는 <a href="/semiont" class="mcp-link">COMPUTEX.md</a> 번식 시스템의 일부로, 대만의 목소리를 모든 개발자의 AI 세션 안에 살게 합니다. fork·기여·제보를 환영합니다.',
    btnDocs: '문서',
    btnContribute: '기여하기',
    downloadLabel: 'taiwanmd.mcpb 다운로드',
    remoteNote:
      'Node를 실행할 수 없는 씬 클라이언트 / 순수 웹용. 로컬 우선을 권장합니다(프라이버시 최선).',
    backHomeLabel: '← 홈으로',
  },

  // ──────────────────────────────────────────────────────────────── es ──
  es: {
    heroEyebrow: '🧬 COMPUTEX.MD · CONNECTOR',
    heroTitle: 'Pon Taiwán en tu IA',
    heroSubtitle:
      'Más de 900 artículos sobre Taiwán con fuentes, a una llamada de herramienta. Cuando le preguntas a una IA sobre Taiwán, responde con la propia voz de Taiwán y con citas.',
    badges: ['Gratis', 'Sin clave API', 'Local primero', 'Código abierto'],
    heroNote: 'Pégalo en tu terminal → luego pregúntale a Claude sobre Taiwán',
    copyLabel: 'Copiar',
    copiedLabel: 'Copiado ✓',

    whatTitle: 'Qué es',
    whatLeadHtml:
      '<strong>COMPUTEX.md</strong> es una base de conocimiento sobre Taiwán, de código abierto y nativa para IA. Este conector la convierte en <strong>herramientas MCP</strong>, para que Claude Code, Claude Desktop, Cursor, Copilot CLI y Codex CLI puedan buscar, leer y <strong>citar</strong> artículos con fuentes sobre Taiwán directamente, en vez de adivinar de memoria.',
    whatLead2:
      'Va a propósito en la dirección opuesta a una pasarela de datos comercial:',
    compareHead: ['', 'COMPUTEX.md Connector', 'Pasarela MCP comercial típica'],
    compareRows: [
      ['Precio', 'Gratis', 'De pago / por uso'],
      ['Clave API', 'No hace falta', 'Obligatoria'],
      [
        'Dónde corren las consultas',
        'Tu equipo (stdio local)',
        'Sus servidores',
      ],
      ['Código', 'Abierto (código MIT / contenido CC BY-SA)', 'Cerrado'],
    ],

    installTitle: 'Instalación',
    installLead: 'Elige tu cliente, copia y pega. Sin registro.',
    installClientLabels: [
      'Claude Code',
      'Claude Desktop',
      'Cursor',
      'Copilot CLI / Codex CLI / Cline / Continue / cualquier cliente MCP',
    ],
    installBadges: [
      'Una línea',
      'Bundle de un clic',
      'Settings → MCP',
      'stdio universal',
    ],
    installNotes: [
      'Sin instalación (vía npx). Una vez añadido, pregúntale a Claude sobre Taiwán.',
      'No pide clave API, porque no hay clave API.',
      'Añade un servidor MCP en los ajustes de Cursor.',
      'Cualquier cliente que hable MCP funciona: apúntalo a este comando stdio.',
    ],
    installDesktopCode: 'Descarga taiwanmd.mcpb → doble clic → listo',
    installFootnoteHtml:
      'Puedes imprimir el fragmento correcto cuando quieras: <code class="mcp-inline">npx -y taiwanmd mcp install --client claude-code</code>',

    toolsTitle: 'Herramientas MCP',
    toolsLeadHtml:
      'Una vez instalado, Claude elige las herramientas solo. <code class="mcp-inline">taiwanmd_cite</code> es el arma anti-alucinación: solo devuelve frases respaldadas por una nota al pie + URL de fuente, para que cada dato que escribas sobre Taiwán sea rastreable.',
    toolTag: 'anti-alucinación',
    ioInput: 'entrada',
    ioReturn: 'salida',
    toolDescs: [
      'Búsqueda de texto en 900+ artículos sobre Taiwán (zh + en)',
      'Lee un artículo completo por slug (frontmatter + cuerpo)',
      'Los N mejores artículos en un bloque de contexto RAG listo para prompt',
      'Primitiva anti-alucinación: solo frases con nota al pie + URL de fuente',
      'Puntuaciones de salud en vivo de los 8 órganos del Semiont',
      'Estadísticas del proyecto: nº de artículos / categorías / marcas de tiempo',
    ],
    toolReturns: [
      'N resultados: title / slug / category / description',
      'Cuerpo markdown completo',
      'Contexto listo para LLM + la pregunta',
      'claim + article + sources[{ name, url }]',
      'Vitales del organismo (corazón / inmune / ADN …)',
      'totalArticles / byCategory',
    ],

    cliTitle: 'Herramientas CLI',
    cliLead:
      'La misma base de conocimiento, directa desde tu terminal. Instala globalmente o ejecuta sin instalar:',
    cliInstallComment: '# o sin instalar: npx taiwanmd search 珍珠奶茶',
    cliGroupTitles: [
      'Leer y explorar',
      'IA · RAG',
      'Contribuir · calidad',
      'Organismo · Semiont',
      'Utilidades',
    ],
    cliDescs: [
      'Búsqueda difusa (zh + en, --json para encadenar)',
      'Lee un artículo completo en la terminal (--raw / --en / --web)',
      'Explora por categoría (--categories para todas)',
      'Descubre un artículo al azar',
      'Hoy en Taiwán: 3 selecciones + un dato curioso',
      'Quiz de conocimiento sobre Taiwán (5 verdadero/falso)',
      'TUI interactiva de búsqueda difusa',
      'Grafo de relaciones [[wikilink]] de un artículo',
      'Cambios en la base de conocimiento de los últimos 7 días',
      'Consulta y conversión de términos Taiwán / China',
      'Mejores artículos como contexto listo para prompt (encadena a un LLM)',
      'Anti-alucinación: afirmaciones verificables con URL de fuente',
      'Inicia el servidor MCP (para Claude y otros clientes)',
      'Creación guiada e interactiva de un artículo nuevo',
      'Tarjeta de calidad de un artículo',
      'Auditoría de alucinaciones Stage 3.5 (MANIFESTO §10)',
      'Lee / gestiona el ARTICLE-INBOX',
      'Sincroniza la base de conocimiento en local',
      'Gráfico de barras de las 8 puntuaciones de órganos',
      'Estadísticas del proyecto + salud del organismo',
      'Datos de sensores: GA4 / Search Console / Cloudflare',
      'Esporas de comunidad (SPORE-LOG)',
      'Estadísticas de mecenas de Portaly (anonimizadas por defecto)',
      'Gestiona tu perfil de colaborador',
      'Inspecciona / gestiona las fusiones de identidad de .mailmap',
    ],

    howTitle: 'Cómo funciona · privacidad',
    howBulletsHtml: [
      '<strong>stdio local</strong> — el servidor corre como proceso en tu equipo, no es un servicio remoto. Tus preguntas nunca van a ningún servidor de COMPUTEX.md.',
      '<strong>Sincronización automática única</strong> — la base de conocimiento se descarga una vez a <code class="mcp-inline">~/.taiwanmd</code>, y luego es rápida y silenciosa en local. Dentro del repo lee <code class="mcp-inline">knowledge/</code> directamente.',
      '<strong>Abierto y verificable</strong> — el servidor MCP son 145 líneas (<code class="mcp-inline">cli/src/lib/mcp-server.js</code>); lee cada línea antes de instalar.',
      '<strong>Licencia</strong> — contenido CC BY-SA 4.0, código MIT. Haz fork libremente.',
    ],

    faqTitle: 'Preguntas frecuentes',
    faqs: [
      {
        q: '¿Cuesta algo? ¿Necesito una clave API?',
        a: 'Ninguna de las dos. COMPUTEX.md es un bien común (CC BY-SA); las consultas de conocimiento no tienen barrera. Sin cuenta, sin clave, sin facturación.',
      },
      {
        q: '¿A dónde van mis consultas?',
        a: 'A ningún sitio. El servidor MCP es un proceso stdio local en tu propio equipo; las consultas no se envían fuera. El primer uso descarga la base de conocimiento a ~/.taiwanmd y luego todo queda en local.',
      },
      {
        q: '¿La primera consulta va lenta?',
        a: 'Es la sincronización única de la base de conocimiento. El servidor se precalienta al arrancar, así que después va rápido.',
      },
      {
        q: '¿No encuentra npx?',
        a: 'Node.js 18+ incluye npx. Para fijar una versión usa npx -y taiwanmd@0.7 mcp serve.',
      },
      {
        q: '¿Hay un endpoint remoto?',
        a: 'Sí: https://mcp.computex.md (gratis, solo lectura, sin clave). Conecta cualquier cliente MCP con npx mcp-remote https://mcp.computex.md. Para clientes ligeros que no pueden ejecutar Node — pero local primero es siempre la vía recomendada (mejor privacidad); lo remoto es solo una entrada opcional.',
      },
    ],

    osTitle: 'Código abierto · el cuerpo del Semiont',
    osParaHtml:
      'Este conector es parte del sistema de reproducción de <a href="/semiont" class="mcp-link">COMPUTEX.md</a>: deja que la voz de Taiwán viva dentro de la sesión de IA de cada desarrollador. Forks, contribuciones e informes son bienvenidos.',
    btnDocs: 'Documentación',
    btnContribute: 'Contribuir',
    downloadLabel: 'Descargar taiwanmd.mcpb',
    remoteNote:
      'Para clientes ligeros que no pueden ejecutar Node / web pura. Se sigue recomendando local primero (mejor privacidad).',
    backHomeLabel: '← Inicio',
  },

  // ──────────────────────────────────────────────────────────────── fr ──
  fr: {
    heroEyebrow: '🧬 COMPUTEX.MD · CONNECTOR',
    heroTitle: 'Mets Taïwan dans ton IA',
    heroSubtitle:
      'Plus de 900 articles sourcés sur Taïwan, à un appel d’outil. Quand tu interroges une IA sur Taïwan, elle répond avec la voix de Taïwan elle-même — sources à l’appui.',
    badges: ['Gratuit', 'Sans clé API', 'Local d’abord', 'Open source'],
    heroNote: 'Colle-le dans ton terminal → puis interroge Claude sur Taïwan',
    copyLabel: 'Copier',
    copiedLabel: 'Copié ✓',

    whatTitle: 'Qu’est-ce que c’est',
    whatLeadHtml:
      '<strong>COMPUTEX.md</strong> est une base de connaissances sur Taïwan, open source et pensée pour l’IA. Ce connecteur la transforme en <strong>outils MCP</strong>, pour que Claude Code, Claude Desktop, Cursor, Copilot CLI et Codex CLI puissent chercher, lire et <strong>citer</strong> directement des articles sourcés sur Taïwan, au lieu de deviner de mémoire.',
    whatLead2:
      'Il prend volontairement le contre-pied d’une passerelle de données commerciale :',
    compareHead: [
      '',
      'COMPUTEX.md Connector',
      'Passerelle MCP commerciale typique',
    ],
    compareRows: [
      ['Prix', 'Gratuit', 'Payant / à l’usage'],
      ['Clé API', 'Inutile', 'Obligatoire'],
      [
        'Où tournent les requêtes',
        'Ta machine (stdio local)',
        'Leurs serveurs',
      ],
      ['Source', 'Ouverte (code MIT / contenu CC BY-SA)', 'Fermée'],
    ],

    installTitle: 'Installation',
    installLead: 'Choisis ton client, copie-colle. Aucune inscription.',
    installClientLabels: [
      'Claude Code',
      'Claude Desktop',
      'Cursor',
      'Copilot CLI / Codex CLI / Cline / Continue / n’importe quel client MCP',
    ],
    installBadges: [
      'Une ligne',
      'Bundle en un clic',
      'Settings → MCP',
      'stdio universel',
    ],
    installNotes: [
      'Sans installation (via npx). Une fois ajouté, interroge Claude sur Taïwan.',
      'Aucune demande de clé API — parce qu’il n’y a pas de clé API.',
      'Ajoute un serveur MCP dans les réglages de Cursor.',
      'Tout client qui parle MCP fonctionne : pointe-le vers cette commande stdio.',
    ],
    installDesktopCode: 'Télécharge taiwanmd.mcpb → double-clic → terminé',
    installFootnoteHtml:
      'Tu peux afficher le bon extrait à tout moment : <code class="mcp-inline">npx -y taiwanmd mcp install --client claude-code</code>',

    toolsTitle: 'Outils MCP',
    toolsLeadHtml:
      'Une fois installé, Claude choisit les outils lui-même. <code class="mcp-inline">taiwanmd_cite</code> est l’arme anti-hallucination : il ne renvoie que des phrases adossées à une note de bas de page + une URL de source, pour que chaque fait que tu écris sur Taïwan soit traçable.',
    toolTag: 'anti-hallucination',
    ioInput: 'entrée',
    ioReturn: 'sortie',
    toolDescs: [
      'Recherche plein texte dans 900+ articles sur Taïwan (zh + en)',
      'Lit un article complet par slug (frontmatter + corps)',
      'Les N meilleurs articles assemblés en bloc de contexte RAG prêt pour le prompt',
      'Primitive anti-hallucination : seulement les phrases avec note + URL de source',
      'Scores de santé en direct des 8 organes du Semiont',
      'Statistiques du projet : nombre d’articles / catégories / horodatages',
    ],
    toolReturns: [
      'N résultats : title / slug / category / description',
      'Corps markdown complet',
      'Contexte prêt pour le LLM + la question',
      'claim + article + sources[{ name, url }]',
      'Constantes de l’organisme (cœur / immunité / ADN …)',
      'totalArticles / byCategory',
    ],

    cliTitle: 'Outils CLI',
    cliLead:
      'La même base de connaissances, directement dans ton terminal. Installe en global ou exécute sans installer :',
    cliInstallComment: '# ou sans installation : npx taiwanmd search 珍珠奶茶',
    cliGroupTitles: [
      'Lire et explorer',
      'IA · RAG',
      'Contribuer · qualité',
      'Organisme · Semiont',
      'Utilitaires',
    ],
    cliDescs: [
      'Recherche floue (zh + en, --json pour chaîner)',
      'Lit un article complet dans le terminal (--raw / --en / --web)',
      'Parcourt par catégorie (--categories pour toutes)',
      'Découvre un article au hasard',
      'Aujourd’hui à Taïwan : 3 sélections + une anecdote',
      'Quiz de connaissances sur Taïwan (5 vrai/faux)',
      'TUI interactive de recherche floue',
      'Graphe de relations [[wikilink]] d’un article',
      'Changements de la base sur les 7 derniers jours',
      'Recherche et conversion de termes Taïwan / Chine',
      'Meilleurs articles en contexte prêt pour le prompt (à chaîner vers un LLM)',
      'Anti-hallucination : affirmations vérifiables avec URL de source',
      'Démarre le serveur MCP (pour Claude et d’autres clients)',
      'Création guidée et interactive d’un nouvel article',
      'Fiche de qualité d’un article',
      'Audit d’hallucinations Stage 3.5 (MANIFESTO §10)',
      'Lit / gère l’ARTICLE-INBOX',
      'Synchronise la base de connaissances en local',
      'Diagramme en barres des 8 scores d’organes',
      'Statistiques du projet + santé de l’organisme',
      'Données de capteurs : GA4 / Search Console / Cloudflare',
      'Spores communautaires (SPORE-LOG)',
      'Statistiques des soutiens Portaly (anonymisées par défaut)',
      'Gère ton profil de contributeur',
      'Inspecte / gère les fusions d’identité .mailmap',
    ],

    howTitle: 'Fonctionnement · confidentialité',
    howBulletsHtml: [
      '<strong>stdio local</strong> — le serveur tourne comme un processus sur ta machine, pas un service distant. Tes questions ne vont vers aucun serveur COMPUTEX.md.',
      '<strong>Synchro automatique unique</strong> — la base se télécharge une fois vers <code class="mcp-inline">~/.taiwanmd</code>, puis c’est rapide et discret en local. Dans le dépôt, elle lit <code class="mcp-inline">knowledge/</code> directement.',
      '<strong>Ouvert et vérifiable</strong> — le serveur MCP fait 145 lignes (<code class="mcp-inline">cli/src/lib/mcp-server.js</code>) ; lis chaque ligne avant d’installer.',
      '<strong>Licence</strong> — contenu CC BY-SA 4.0, code MIT. Fork librement.',
    ],

    faqTitle: 'FAQ',
    faqs: [
      {
        q: 'Est-ce payant ? Faut-il une clé API ?',
        a: 'Ni l’un ni l’autre. COMPUTEX.md est un bien commun (CC BY-SA) ; les requêtes de connaissances n’ont pas de barrière. Pas de compte, pas de clé, pas de facturation.',
      },
      {
        q: 'Où vont mes requêtes ?',
        a: 'Nulle part. Le serveur MCP est un processus stdio local sur ta propre machine ; les requêtes ne sortent pas. La première utilisation télécharge la base vers ~/.taiwanmd, puis tout reste en local.',
      },
      {
        q: 'La première requête semble lente ?',
        a: 'C’est la synchro unique de la base qui tourne. Le serveur se préchauffe au démarrage, donc c’est rapide ensuite.',
      },
      {
        q: 'npx introuvable ?',
        a: 'Node.js 18+ fournit npx. Pour figer une version, utilise npx -y taiwanmd@0.7 mcp serve.',
      },
      {
        q: 'Y a-t-il un point d’accès distant ?',
        a: 'Oui : https://mcp.computex.md (gratuit, lecture seule, sans clé). Connecte n’importe quel client MCP avec npx mcp-remote https://mcp.computex.md. Pour les clients légers qui ne peuvent pas exécuter Node — mais le local d’abord reste la voie recommandée (meilleur pour la vie privée) ; le distant n’est qu’une entrée optionnelle.',
      },
    ],

    osTitle: 'Open source · le corps du Semiont',
    osParaHtml:
      'Ce connecteur fait partie du système de reproduction de <a href="/semiont" class="mcp-link">COMPUTEX.md</a> — il fait vivre la voix de Taïwan dans la session IA de chaque développeur. Forks, contributions et signalements bienvenus.',
    btnDocs: 'Documentation',
    btnContribute: 'Contribuer',
    downloadLabel: 'Télécharger taiwanmd.mcpb',
    remoteNote:
      'Pour les clients légers qui ne peuvent pas exécuter Node / web pur. Le local d’abord reste recommandé (meilleure confidentialité).',
    backHomeLabel: '← Accueil',
  },
};
