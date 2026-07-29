/**
 * home.ts — 首頁字串（zh-TW + en）
 *
 * 2026-07-29 整份改寫。取種帶進來的是母體 12 個語言 × 約 150 個 key 的台灣
 * 敘事字串（「策展島嶼的深度敘事」「400+ 年歷史 / 59,000+ 物種」「如何理解
 * 台灣？」的八段引言時間軸）。這裡刪掉兩類東西：
 *
 *   1. 十個沒有被渲染的語言區塊（ja/ko/vi/id/pt/hi/ar/ru/fr/es）。
 *      `ui.ts` 只有 en 與 zh-TW 兩個 key，其餘 1,500 行從取種那天起就沒有
 *      任何一頁讀得到，只是讓「全站還有幾行提到台灣」這個數字永遠降不下來。
 *   2. 已經沒有元件在讀的 key（cover / lang / newsletter / readingPath /
 *      miniGraph / organism / bridge）。對應的元件在同一個 commit 一起刪掉。
 *
 * 寫作紀律：首頁文案不做沒有出處的絕對宣稱（`marketing-speak` gate 會擋），
 * 數字一律由 `src/lib/archive-stats.ts` 現算，NEVER 寫進字串。
 */
export const homeUI = {
  en: {
    // ── Hero stats（數字由 archive-stats 現算，這裡只有標籤）──
    'hero.stat.vendors.label': 'exhibitors',
    'hero.stat.returning.label': 'returning',
    'hero.stat.editions.label': 'editions covered',
    'hero.stat.earliest.label': 'earliest on record',

    'home.hero.subtitle': 'A living archive of Taiwan AI hardware',
    'home.hero.description':
      'An open archive of COMPUTEX exhibitors, products and editions.',
    'home.hero.highlight':
      'Every fact carries a source link. What the organiser has not published stays blank.',
    'home.hero.cta.explore': 'Browse the archive',
    'home.hero.transparency':
      'This is an independent project, not affiliated with TAITRA or COMPUTEX. Spotted something wrong on your own page?',
    'home.hero.transparency.link': 'Open an issue',

    // ── HowItWorks ──
    'home.how.heading': 'How this archive works',
    'home.how.lead':
      'Three rules decide what gets written here. They are also the reason an AI engine has any reason to quote this site rather than a vendor brochure.',
    'home.how.fact.title': 'Facts are extracted by a program, not a model',
    'home.how.fact.body':
      'Every field on a vendor page comes from the official exhibitor directory, pulled by a script, with no language model rewriting anything in between. Each row carries the source URL and the date it was checked. A vendor can send a pull request to correct their own facts, as long as the correction carries a source too.',
    'home.how.curation.title': 'Curation is a separate layer',
    'home.how.curation.body':
      'Where a company sits in the supply chain, what changed since last year, how one edition compares to the last: that is curation, and only neutral editors write it. Vendors can dispute it in a pull request; they cannot edit it directly. That boundary is the design itself.',
    'home.how.blank.title': 'Blank means blank',
    'home.how.blank.body':
      'When the official directory does not publish a field, the page leaves it empty. Filling it in takes a verifiable source, not a plausible guess. A page that looks complete is worth nothing if a single row of it was invented.',
    'home.how.link': 'Read the editorial charter',

    // ── RandomDiscovery ──
    'home.random.button': 'Open a random page',
    'home.random.subtitle': 'Land somewhere you were not looking for',
    'home.random.description':
      'Not sure where to start? Roll the dice and see what is in the archive.',

    // ── FeatureCards ──
    'home.features.title': 'Why this exists',
    'home.features.curated.title': 'Traceable, row by row',
    'home.features.curated.desc':
      'Every fact carries a source link and the date it was last checked',
    'home.features.ai.title': 'Built to be quoted by machines',
    'home.features.ai.desc':
      'Plain Markdown twins, llms.txt, JSON-LD and an MCP server, all public',
    'home.features.bilingual.title': 'Alive between editions',
    'home.features.bilingual.desc':
      'One file per company, accumulating across years instead of resetting every show',
    'home.features.complete.title': 'Open to correction',
    'home.features.complete.desc':
      'Every page can be claimed and corrected through a pull request',
    'home.features.cta.graph': '🔗 Knowledge graph',
    'home.features.cta.ssot': '📂 Browse the raw Markdown ↗',

    // ── VitalsStrip ──
    'home.vitals.heading': 'What the archive looks like right now',
    'home.vitals.body':
      'Counted from the files themselves at build time. Nothing here is a rounded-up claim.',
    'home.vitals.pages': 'pages',
    'home.vitals.sources': 'fact source',
    'home.vitals.sources.value': 'official',
    'home.vitals.span': 'years on record',
    'home.vitals.booth': 'with a booth number',
    'home.vitals.cta': 'Open the dashboard',

    // ── ArchiveShelf ──
    'home.shelf.heading': 'What is in the archive',
    'home.shelf.lead':
      'Counted from the files, not estimated. Empty means empty.',
    'home.shelf.unit': 'pages',
    'home.shelf.empty':
      'Nothing here yet. This section stays empty until there are facts to put in it.',
    'home.shelf.vendors.longestLabel': 'Longest exhibiting records on file',
    'home.shelf.vendors.blurb':
      'One page per exhibiting company, extracted from the official directory: venue, booth number, official site, product tags, and the full year-by-year exhibiting record.',
    'home.shelf.products.blurb':
      'Products and technologies shown on the floor, kept separate from the companies that make them.',
    'home.shelf.editions.blurb':
      'One page per edition: dates, halls, themes, and what was actually announced.',
    'home.shelf.topics.blurb':
      'The curation layer. Industry reading that connects the facts, written only by neutral editors.',
    'home.shelf.footnote':
      'Page counts are what actually exists on disk, not what the directory contains. Whenever the exhibitor count in the header and the page count here diverge, that gap is how much of the directory has not been turned into pages yet, and it is left visible on purpose.',

    'home.categories.divider': 'Browse by section',

    // ── RecentUpdates ──
    'home.updates.heading': 'Recent changes',
    'home.updates.subtitle': 'Every change to this archive is a public commit',
    'home.updates.viewAll': 'Full changelog →',
    'home.heartbeat.organsLabel': 'Organ scores',
    'home.heartbeat.vitalsLabel': 'Vitals',
    'home.heartbeat.viewMore': 'Open the full dashboard →',

    // ── ContributeSection ──
    'home.contribute.heading': 'Claim your page',
    'home.contribute.description':
      'If your company is in here, the page is yours to correct. Facts change through pull requests, and every correction needs a source. If you would rather the page came down, the same route works.',
    'home.contribute.guide': 'How to contribute',
    'home.contribute.github': 'GitHub repository',

    // ── ReaderDoors ──
    'home.doors.first.title': 'First time here',
    'home.doors.first.sub': 'How this archive works →',
    'home.doors.search.title': 'Looking for a company',
    'home.doors.search.sub': 'Search the archive',
    'home.doors.random.title': 'Show me anything',
    'home.doors.random.sub': 'Roll the dice',
    'home.doors.organism.title': 'Show me the numbers',
    'home.doors.organism.sub': 'Public dashboard',

    'home.meta.title':
      'COMPUTEX.md: a living archive of the Taiwan AI hardware industry',
    'home.meta.description':
      'An open archive of COMPUTEX exhibitors, products and editions. The fact layer is extracted mechanically from the official directory, every item carrying a source link and a checked date; what the organiser has not published is left blank.',
  },

  'zh-TW': {
    // ── Hero stats（數字由 archive-stats 現算，這裡只有標籤）──
    'hero.stat.vendors.label': '家參展廠商',
    'hero.stat.returning.label': '家跨屆參展',
    'hero.stat.editions.label': '屆參展紀錄',
    'hero.stat.earliest.label': '最早紀錄年份',

    'home.hero.subtitle': '台灣 AI 硬體產業活體年鑑',
    'home.hero.description': 'COMPUTEX 參展廠商、產品與歷屆展會的開放檔案庫。',
    'home.hero.highlight': '每一項事實都附出處連結。官方沒公布的，我們就留白。',
    'home.hero.cta.explore': '開始瀏覽',
    'home.hero.transparency':
      '本站是獨立專案，非外貿協會或 COMPUTEX 官方網站。發現自己那頁寫錯了？',
    'home.hero.transparency.link': '開一個 issue',

    // ── HowItWorks ──
    'home.how.heading': '這個檔案庫怎麼運作',
    'home.how.lead':
      '三條規則決定這裡寫得出什麼。它們也是 AI 引擎有理由引用這裡、而不是引用廠商官網文案的全部原因。',
    'home.how.fact.title': '事實層由程式抽取，不經語言模型',
    'home.how.fact.body':
      '廠商頁上的每一個欄位都來自官方名錄，由腳本機械抽取，中間沒有任何語言模型改寫。每一列都帶出處網址與查證日期。廠商可以送 pull request 修正自己那頁的事實，前提是修正本身也附得上出處。',
    'home.how.curation.title': '策展層跟事實層分開',
    'home.how.curation.body':
      '一家公司在供應鏈裡的位置、今年跟去年比變了什麼、這一屆跟上一屆的差別，這些屬於策展層，只有中立編輯能寫。廠商可以在 pull request 裡提異議，不能直接改。這條界線本身就是設計。',
    'home.how.blank.title': '留白就是留白',
    'home.how.blank.body':
      '官方名錄沒公布的欄位，頁面就是空的。要補滿它需要可查證的來源，不是需要一個合理的推測。一頁只要有一列是編的，看起來再完整都不值錢。',
    'home.how.link': '看完整編輯憲章',

    // ── RandomDiscovery ──
    'home.random.button': '隨機打開一頁',
    'home.random.subtitle': '掉到一個你本來沒在找的地方',
    'home.random.description':
      '不知道從哪裡看起？擲個骰子，看看檔案庫裡有什麼。',

    // ── FeatureCards ──
    'home.features.title': '為什麼需要這個檔案庫',
    'home.features.curated.title': '逐列可回溯',
    'home.features.curated.desc': '每一項事實都附出處連結與最後查證日期',
    'home.features.ai.title': '為了被機器引用而建',
    'home.features.ai.desc':
      '每頁都有純文字 Markdown 雙胞胎，llms.txt、JSON-LD 與 MCP server 全部公開',
    'home.features.bilingual.title': '非展期也活著',
    'home.features.bilingual.desc':
      '一家公司一份檔案跨年度累積，不是每屆重開一個新檔',
    'home.features.complete.title': '開放被糾正',
    'home.features.complete.desc': '每一頁都可以認領，用 pull request 修正',
    'home.features.cta.graph': '🔗 知識圖譜',
    'home.features.cta.ssot': '📂 瀏覽原始 Markdown ↗',

    // ── VitalsStrip ──
    'home.vitals.heading': '這個檔案庫現在的樣子',
    'home.vitals.body':
      '這些數字是 build 時從檔案本身數出來的。沒有一個是無條件進位過的宣稱。',
    'home.vitals.pages': '頁',
    'home.vitals.sources': '事實來源',
    'home.vitals.sources.value': '官方名錄',
    'home.vitals.span': '涵蓋年份',
    'home.vitals.booth': '有攤位號',
    'home.vitals.cta': '打開數據儀表板',

    // ── ArchiveShelf ──
    'home.shelf.heading': '這個檔案庫現在有什麼',
    'home.shelf.lead': '數字從檔案數出來，不是估的。空的就是空的。',
    'home.shelf.unit': '頁',
    'home.shelf.empty': '還沒有內容。要有可查證的事實才會生出頁面。',
    'home.shelf.vendors.longestLabel': '官方名錄上參展紀錄最長的幾家',
    'home.shelf.vendors.blurb':
      '一家參展廠商一頁，從官方名錄機械抽取：場館、攤位號、官方網站、產品標籤，以及逐年的完整參展紀錄。',
    'home.shelf.products.blurb': '展出的產品與技術，跟做它的公司分開放。',
    'home.shelf.editions.blurb':
      '一屆一頁：日期、場館、主題，以及那一屆真正公布過的東西。',
    'home.shelf.topics.blurb':
      '策展層。把事實串起來的產業閱讀，只有中立編輯能寫。',
    'home.shelf.footnote':
      '這裡的頁數是硬碟上真的存在的頁面數，不是名錄裡有幾家。上方的參展廠商數跟這裡的頁數哪天對不起來，那個差距就是名錄還沒轉成頁面的部分，刻意讓它看得見。',

    'home.categories.divider': '依區塊瀏覽',

    // ── RecentUpdates ──
    'home.updates.heading': '最近的改動',
    'home.updates.subtitle': '這個檔案庫的每一次改動都是一個公開 commit',
    'home.updates.viewAll': '完整更新紀錄 →',
    'home.heartbeat.organsLabel': '當前器官分數',
    'home.heartbeat.vitalsLabel': '生命徵象',
    'home.heartbeat.viewMore': '進入完整儀表板 →',

    // ── ContributeSection ──
    'home.contribute.heading': '認領你自己那一頁',
    'home.contribute.description':
      '如果貴公司在這裡面，那一頁就是你可以來改的。事實層透過 pull request 修正，每一次修正都要附出處。如果希望把那頁撤下來，走同一個管道。',
    'home.contribute.guide': '貢獻指南',
    'home.contribute.github': 'GitHub 專案',

    // ── ReaderDoors ──
    'home.doors.first.title': '我第一次來',
    'home.doors.first.sub': '這個檔案庫怎麼運作 →',
    'home.doors.search.title': '我要找特定廠商',
    'home.doors.search.sub': '搜尋檔案庫',
    'home.doors.random.title': '隨便給我看點什麼',
    'home.doors.random.sub': '擲骰子',
    'home.doors.organism.title': '我想看數據',
    'home.doors.organism.sub': '公開儀表板',

    'home.meta.title': 'COMPUTEX.md：台灣 AI 硬體產業活體年鑑',
    'home.meta.description':
      'COMPUTEX 參展廠商、產品與歷屆展會的開放檔案庫。事實層機械抽取自官方名錄，逐項附出處連結與查證日期；官方沒公布的一律留白。',
  },
} as const;
