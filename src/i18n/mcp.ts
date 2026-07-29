/**
 * mcp.ts — /mcp 字串（zh-TW + en）
 *
 * 2026-07-29 整份改寫，取代 `src/data/mcp-content.ts`（998 行、六語）。
 *
 * 舊頁不能留的理由跟 /contribute 的表單是同一種：它教訪客執行
 *   `claude mcp add taiwanmd -- npx -y taiwanmd mcp serve`
 * 而 `taiwanmd` 是**母體發佈在 npm 上的套件**。照著做的人裝到的是 Taiwan.md，
 * 拿到的是台灣的資料，但整頁的標題是「把台灣裝進你的 AI」、掛在 COMPUTEX.md 的
 * 網域下。另外 `/downloads/taiwanmd.mcpb` 是母體作者（CheYu Wu，homepage
 * taiwan.md）打包的 connector，我們把它放在自己的 public/ 裡供人下載。
 *
 * 新頁只寫**現在真的存在、而且可以自己驗證**的東西：純 Markdown 分身、llms.txt、
 * 幾支 JSON、sitemap、robots 立場、授權與引用格式。MCP server 與 CLI 的原始碼
 * 確實在 repo 裡，但沒有發佈到 npm、也沒有線上端點，所以那一段就寫「還沒有」，
 * 不給跑不動的安裝指令。
 *
 * 紀律：這一頁列出的每一條路徑都必須在 dist 裡真的存在。寫進來之前先 build 再
 * 確認檔案在，不然這頁本身就變成它要解決的那個問題。
 */
export const mcpUI = {
  en: {
    'mcp.meta.title': 'Machine-readable entry points',
    'mcp.meta.description':
      'Every door into COMPUTEX.md built for machines: plain Markdown twins of every page, llms.txt, JSON endpoints, sitemap, and an open crawler policy. Content is CC BY 4.0.',

    'mcp.hero.title': 'Built to be read by machines',
    'mcp.hero.subtitle':
      'This archive exists to be quoted. Every door below is open, needs no key, and returns the same content a person sees.',

    'mcp.lead':
      'What survives online after a trade show is mostly press releases and each exhibitor’s own marketing pages. A language model asked about the Taiwan AI hardware supply chain has to answer from that. This archive is the alternative: mechanically extracted facts, each carrying a source link and a checked date, served in formats a machine can read without rendering a page.',

    'mcp.doors.title': 'Available now',
    'mcp.doors.lead':
      'Each of these is a real path on this site. Nothing here is behind an API key, a rate limit, or an account.',
    'mcp.doors.pathLabel': 'Path',
    'mcp.doors.whatLabel': 'What it returns',

    'mcp.doors.raw.what':
      'The plain Markdown source of any page, frontmatter included, served as text/markdown with a provenance header. Same content as the rendered page, no HTML to strip.',
    'mcp.doors.llms.what':
      'One plain-text file describing what this archive is, what it deliberately does not claim, and how to cite it. Follows the llms.txt convention.',
    'mcp.doors.articles.what':
      'Metadata for every page: title, description, category, tags, URL, reading time.',
    'mcp.doors.stats.what':
      'Counts by category, generated at build time from the files on disk.',
    'mcp.doors.search.what':
      'A flat search index of every page (title, description, URL, tags) for clients that want to search locally.',
    'mcp.doors.sitemap.what': 'Every URL on the site.',
    'mcp.doors.feed.what': 'RSS feed of the most recently changed pages.',
    'mcp.doors.robots.what':
      'The crawler policy. Every named AI crawler is explicitly allowed and no content path is disallowed.',

    'mcp.cite.title': 'How to cite',
    'mcp.cite.lead':
      'Content is CC BY 4.0. You may copy, redistribute, remix and build on it, including commercially, as long as you give attribution.',
    'mcp.cite.format': 'Attribution format',
    'mcp.cite.note':
      'Two things matter more than the format. First: COMPUTEX.md is an independent open-data project, not the official site of COMPUTEX, TAITRA or the Taipei Computer Association. Do not attribute this content to the organizers. Second: every fact on this site carries the primary source URL it came from. If you are citing a fact rather than our arrangement of it, cite that source, not us.',

    'mcp.mcp.title': 'The MCP server',
    'mcp.mcp.status': 'Status: source in the repository, not published',
    'mcp.mcp.body':
      'An MCP server and a command-line client live in this repository under workers/ and cli/. Neither is published to a package registry, and there is no hosted endpoint. Until that changes, this section is a status note rather than an install guide: an install command that quietly pulls someone else’s package is worse than no install command.',
    'mcp.mcp.meanwhile':
      'In the meantime the doors above are enough to build against. A model that can fetch a URL can read every page of this archive as Markdown, and the JSON endpoints give you the index without crawling.',
    'mcp.mcp.cta': 'Read the source on GitHub',

    'mcp.wont.title': 'What this site will not do to machines',
    'mcp.wont.lead':
      'These are commitments, not current limitations. They are written as negatives because negatives leave no room for interpretation.',
    'mcp.wont.1':
      'Serve different content to crawlers than to people. What a bot reads is what a reader reads.',
    'mcp.wont.2':
      'Put content behind an API key, an account, or a paywall. There is no tier above free.',
    'mcp.wont.3':
      'Block AI crawlers, in robots.txt or at the edge, including the ones that are unpopular this month.',
    'mcp.wont.4':
      'Generate facts with a language model and serve them as extracted ones. The fact layer is mechanical or it is blank.',
  },

  'zh-TW': {
    'mcp.meta.title': '給機器的入口',
    'mcp.meta.description':
      'COMPUTEX.md 為機器開的每一道門：每頁的純 Markdown 分身、llms.txt、JSON 端點、sitemap，以及全面開放的爬蟲政策。內容授權 CC BY 4.0。',

    'mcp.hero.title': '這個檔案庫是為了被機器讀而做的',
    'mcp.hero.subtitle':
      '它存在的理由就是被引用。下面每一道門都開著，不需要金鑰，回傳的內容跟人看到的一模一樣。',

    'mcp.lead':
      '一場展會結束後留在網路上的，多半是新聞稿與各家自己的行銷頁。語言模型被問到台灣 AI 硬體供應鏈時，只能拿那些來回答。這個檔案庫是另一個選項：機械抽取的事實，每一項附出處連結與查證日期，並且用機器不必解析網頁就讀得動的格式供應。',

    'mcp.doors.title': '現在就有的',
    'mcp.doors.lead':
      '下面每一條都是本站真實存在的路徑。沒有任何一條需要 API 金鑰、帳號，或有流量限制。',
    'mcp.doors.pathLabel': '路徑',
    'mcp.doors.whatLabel': '回傳什麼',

    'mcp.doors.raw.what':
      '任何一頁的原始 Markdown，含 frontmatter，以 text/markdown 供應並附一段來源標頭。內容跟渲染後的頁面相同，不用剝 HTML。',
    'mcp.doors.llms.what':
      '一個純文字檔，說明這個檔案庫是什麼、刻意不主張什麼、該怎麼引用。遵循 llms.txt 慣例。',
    'mcp.doors.articles.what':
      '每一頁的 metadata：標題、描述、分類、標籤、網址、閱讀時間。',
    'mcp.doors.stats.what': '各分類的頁數，build 時從磁碟上的檔案現算。',
    'mcp.doors.search.what':
      '全站頁面的扁平搜尋索引（標題、描述、網址、標籤），給想在本地搜尋的客戶端。',
    'mcp.doors.sitemap.what': '站上全部網址。',
    'mcp.doors.feed.what': '最近變動頁面的 RSS。',
    'mcp.doors.robots.what':
      '爬蟲政策。每一個具名的 AI 爬蟲都明確允許，沒有任何內容路徑被擋。',

    'mcp.cite.title': '怎麼引用',
    'mcp.cite.lead':
      '內容授權 CC BY 4.0。你可以複製、散布、改作、再利用，包含商業用途，條件只有一個：標明出處。',
    'mcp.cite.format': '標註格式',
    'mcp.cite.note':
      '有兩件事比格式重要。第一，COMPUTEX.md 是獨立的開放資料專案，不是 COMPUTEX、外貿協會（TAITRA）或台北市電腦公會的官方網站，請不要把本站內容歸給主辦單位。第二，本站每一項事實都帶著它的第一手出處網址；如果你要引用的是那項事實本身，而不是我們的整理方式，請引用那個出處，不是引用我們。',

    'mcp.mcp.title': 'MCP server 呢',
    'mcp.mcp.status': '狀態：原始碼在 repo 裡，尚未發佈',
    'mcp.mcp.body':
      '這個 repo 的 workers/ 與 cli/ 底下確實有一份 MCP server 與命令列客戶端。兩者都還沒發佈到套件庫，也還沒有線上端點。在那之前，這一段是狀態說明而不是安裝指南：一行會默默裝到別人套件的安裝指令，比沒有安裝指令更糟。',
    'mcp.mcp.meanwhile':
      '在那之前，上面那幾道門已經夠用了。會抓網址的模型就能把這個檔案庫的每一頁讀成 Markdown，而 JSON 端點讓你不必爬站就拿得到索引。',
    'mcp.mcp.cta': '到 GitHub 看原始碼',

    'mcp.wont.title': '本站不會對機器做的四件事',
    'mcp.wont.lead':
      '這幾條是承諾，不是現況的限制。它們用否定句寫，因為肯定句留得下解釋空間，否定句留不下。',
    'mcp.wont.1': '對爬蟲供應跟對人不同的內容。機器讀到的就是讀者讀到的。',
    'mcp.wont.2': '把內容放到 API 金鑰、帳號或付費牆後面。免費之上沒有另一層。',
    'mcp.wont.3':
      '封鎖 AI 爬蟲，不管是在 robots.txt 還是在邊緣層，也包含這個月風評不好的那幾家。',
    'mcp.wont.4':
      '用語言模型生成事實再當成抽取來的供應。事實層要嘛是機械的，要嘛是空的。',
  },
} as const;
