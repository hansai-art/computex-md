/**
 * explore.ts — /explore 字串（zh-TW + en）
 *
 * 2026-07-29 整份改寫，跟 `explore.template.astro` 一起。原本是 782 行、
 * 8 個語言，內容全是母體的：熱門搜尋是「夜市 / 二二八 / 珍珠奶茶」，分類副標
 * 寫「十二個領域，每個都是這座島嶼的一個切面」，meta description 宣稱
 * 「685+ 篇台灣策展文章」。
 *
 * 這一頁的定位沒有跟著換：它是「來找東西的人」的入口（跟首頁那條「來讀故事的
 * 人」分開），這個分工對展會版一樣成立，所以留骨架、換內容與資料來源。
 *
 * 紀律：
 *   - 熱門搜尋不手寫。字串只留標籤，詞條由 template 從實際資料（展區、館別）
 *     現算 —— 手寫的熱門詞很容易變成「搜了 0 筆」的死字。
 *   - 數字一律 `src/lib/archive-stats.ts` 現算，NEVER 寫進字串。
 */
export const exploreUI = {
  en: {
    'explore.meta.title': 'Explore COMPUTEX.md: vendors, products, editions',
    'explore.meta.description':
      'Search the archive, browse by category, and see which exhibitors have the longest run at COMPUTEX. Every fact carries a source link and a checked date.',

    'explore.hero.eyebrow': 'ARCHIVE',
    'explore.hero.title': 'Explore the archive',
    'explore.hero.subtitle':
      'Search it, browse it by category, or take the machine-readable route.',

    'explore.search.heading': 'Search the archive',
    'explore.search.placeholder': 'Company name, booth number, exhibit zone…',
    'explore.search.button': 'Search',
    'explore.search.random': 'Random page',
    'explore.search.randomSubtitle':
      'Land on an exhibitor you were not looking for',
    'explore.hotSearches.label': 'Try',

    'explore.stats.pages': 'pages',
    'explore.stats.vendors': 'exhibitors',
    'explore.stats.editions': 'COMPUTEX editions covered',
    'explore.stats.span': 'earliest record',

    'explore.categories.heading': 'Browse by category',
    'explore.categories.subtitle':
      'Four folders. Two of them are still empty, and the counts say so rather than hiding it.',

    'explore.longest.heading': 'Longest run at COMPUTEX',
    'explore.longest.subtitle':
      'Ranked mechanically by COMPUTEX editions in the official directory, ties broken by who started earlier, then by name. Other TAITRA shows in the same record are not counted. Nothing here is editorial, and nothing can be bought.',
    'explore.longest.editions': 'editions',
    'explore.longest.since': 'since',
    'explore.longest.viewAll': 'All exhibitors',

    'explore.machine.heading': 'The machine-readable route',
    'explore.machine.subtitle':
      'This archive is built to be quoted by language models as much as read by people. These are the doors built for them.',
    'explore.machine.organism.title': 'The Organism',
    'explore.machine.organism.desc':
      'The archive as a living colony: one cell per exhibitor, sitting at its real booth coordinate, lit by how complete its page is.',
    'explore.machine.organism.cta': 'Open the organism',
    'explore.machine.llms.title': 'llms.txt',
    'explore.machine.llms.desc':
      'One plain-text file describing what this archive is, what it does not claim, and how to cite it.',
    'explore.machine.llms.cta': 'Open llms.txt',
    'explore.machine.raw.title': 'Plain Markdown twins',
    'explore.machine.raw.desc':
      'Every page also exists as raw Markdown at the same path under /raw/, served as text/markdown.',
    'explore.machine.raw.cta': 'See an example',

    'explore.cta.heading': 'Something wrong, or missing?',
    'explore.cta.body':
      'Corrections need a source link, not an argument. Companies can also claim their own page, or ask for it to come down.',
    'explore.cta.contribute': 'How to send a correction',
    'explore.cta.github': 'Browse the repository',
  },

  'zh-TW': {
    'explore.meta.title': '探索 COMPUTEX.md：廠商、產品、歷屆展會',
    'explore.meta.description':
      '搜尋檔案庫、依分類瀏覽，看哪些廠商在 COMPUTEX 連續參展最久。每一項事實附出處連結與查證日期。',

    'explore.hero.eyebrow': '檔案庫',
    'explore.hero.title': '探索檔案庫',
    'explore.hero.subtitle': '用搜尋、用分類，或者走機器可讀的那條路。',

    'explore.search.heading': '搜尋檔案庫',
    'explore.search.placeholder': '公司名稱、攤位號、展區⋯⋯',
    'explore.search.button': '搜尋',
    'explore.search.random': '隨機一頁',
    'explore.search.randomSubtitle': '掉到一家你本來沒在找的廠商',
    'explore.hotSearches.label': '試試',

    'explore.stats.pages': '頁',
    'explore.stats.vendors': '家廠商',
    'explore.stats.editions': '屆 COMPUTEX',
    'explore.stats.span': '最早紀錄',

    'explore.categories.heading': '依分類瀏覽',
    'explore.categories.subtitle':
      '四個資料夾。其中兩個目前是空的，數字照實寫出來，不藏。',

    'explore.longest.heading': '在 COMPUTEX 待最久的廠商',
    'explore.longest.subtitle':
      '純機械排序：官方名錄記載的 COMPUTEX 屆數多的在前，同屆數比誰更早開始，再同就按名稱。官方名錄裡的其他外貿協會展會不計入。這裡沒有編輯判斷，也沒有東西可以買。',
    'explore.longest.editions': '屆',
    'explore.longest.since': '自',
    'explore.longest.viewAll': '看全部廠商',

    'explore.machine.heading': '機器可讀的那條路',
    'explore.machine.subtitle':
      '這個檔案庫是為了「被語言模型引用」跟「被人讀」同時設計的。下面這幾道門是給前者開的。',
    'explore.machine.organism.title': '生命體',
    'explore.machine.organism.desc':
      '把整個檔案庫看成一個群落：一顆細胞是一家廠商，待在自己真實的攤位座標上，亮度是這一頁被補到什麼程度。',
    'explore.machine.organism.cta': '打開生命體',
    'explore.machine.llms.title': 'llms.txt',
    'explore.machine.llms.desc':
      '一個純文字檔，說明這個檔案庫是什麼、不主張什麼、該怎麼引用。',
    'explore.machine.llms.cta': '打開 llms.txt',
    'explore.machine.raw.title': '純 Markdown 分身',
    'explore.machine.raw.desc':
      '每一頁在 /raw/ 底下都有同路徑的原始 Markdown，以 text/markdown 供應。',
    'explore.machine.raw.cta': '看一個範例',

    'explore.cta.heading': '有錯，或缺了什麼？',
    'explore.cta.body':
      '更正要附出處連結，不是講道理。廠商也可以認領自己的頁面，或要求下架。',
    'explore.cta.contribute': '怎麼送出勘誤',
    'explore.cta.github': '瀏覽原始碼與資料',
  },
} as const;
