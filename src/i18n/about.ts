/**
 * about.ts — /about 字串（zh-TW + en）
 *
 * 2026-07-29 整份改寫，跟 `about.template.astro` 一起。原本是 5,567 行、12 個
 * 語言，內容是母體的命名故事、母體的十九則版本日記（每則都是幾百字的第一人稱
 * 敘事）、母體的贊助商故事、母體的媒體報導清單。`ui.ts` 只有 en 與 zh-TW 兩個
 * key，其餘十個語言區塊從取種那天起就沒有任何一頁讀得到。
 *
 * 這一頁的文案紀律比別頁嚴：它是外貿協會提案前會點開的第一頁，所以
 *   - NEVER 出現沒有出處的絕對宣稱（`marketing-speak` gate 會擋）
 *   - NEVER 暗示官方背書。非官方聲明放在頁面最上方，中英各一句
 *   - 數字一律由 `src/lib/archive-stats.ts` 現算，不寫進字串
 */
export const aboutUI = {
  en: {
    'about.meta.title': 'About COMPUTEX.md',
    'about.meta.description':
      'What COMPUTEX.md is, where its facts come from, who is allowed to write what, and how to correct or remove a page. An independent open archive, not affiliated with TAITRA or COMPUTEX.',

    'about.hero.title': 'About COMPUTEX.md',
    'about.hero.subtitle':
      'What this is, where the facts come from, and how to change them',

    'about.disclaimer.zh':
      '本站是獨立專案，非外貿協會（TAITRA）或 COMPUTEX 官方網站，未經其授權或背書。所有資料整理自公開來源。',
    'about.disclaimer.en':
      'This is an independent project. It is not the official website of TAITRA or COMPUTEX, and carries no authorisation or endorsement from either. All data is compiled from publicly available sources.',

    'about.intro.p1':
      'COMPUTEX.md is an open archive of COMPUTEX exhibitors, products and editions. One file per company, in plain Markdown, accumulating year after year instead of resetting when the show closes.',
    'about.intro.p2':
      'The show runs for four days a year. The supply chain behind it does not. A directory that only exists during those four days cannot answer the question people actually ask the rest of the year: who makes this, and how long have they been doing it.',
    'about.intro.p3':
      'So the unit here is the company, not the event. A page opened this year is the same page that gets added to next year, and the year after.',

    'about.md.title': 'Why the .md',
    'about.md.p1':
      'Every page here is a Markdown file in a public Git repository. That is not a technical detail, it is the product. A Markdown file can be diffed, so every change has an author and a date. It can be quoted by a language model without a rendering step. It can be forked by anyone if this project ever stops being maintained.',
    'about.md.p2':
      'Each page also serves a plain-text twin at the same address plus a .md suffix, and the whole archive is indexed in llms.txt. Machines read the same thing you do, not a stripped-down version of it.',
    'about.md.cta': 'Browse the vendor pages',

    'about.charter.title': 'The editorial charter',
    'about.charter.lead':
      'Multiple parties with commercial interests co-edit this archive. That only works if it is clear, in advance, who may write what. These three rules are enforced in review, not by good intentions.',
    'about.layers.whoLabel': 'Who may write it:',
    'about.layers.fact.title': 'The fact layer',
    'about.layers.fact.body':
      'Company name, venue, booth number, official URL, product tags, and the year-by-year exhibiting record. Extracted from the official exhibitor directory by a script, with no language model rewriting anything in between. Every row carries its source URL and the date it was checked.',
    'about.layers.fact.who':
      'Anyone, including the company itself, through a pull request. A change is accepted when it carries a source that a third party can check. A correction without a source is declined, however obviously true it looks.',
    'about.layers.curation.title': 'The curation layer',
    'about.layers.curation.body':
      'Where a company sits in the supply chain, what changed since last year, how one edition compares to the last, which technologies clustered on the floor. This is judgement, not record.',
    'about.layers.curation.who':
      'Neutral editors only. A company can dispute a curation passage in a pull request and the dispute is answered in public, but it cannot edit the passage directly. Without this line an AI engine has no reason to treat this archive as anything other than a brochure.',
    'about.layers.blank.title': 'The blank',
    'about.layers.blank.body':
      'When the official directory does not publish a field, the page leaves it empty and says so.',
    'about.layers.blank.who':
      'Nobody fills a blank from a company website, a press release, last year’s pattern, or a third-party aggregator. Filling it takes a verifiable source. A page that looks complete is worth nothing if a single row of it was inferred.',

    'about.sources.title': 'Where the facts come from',
    'about.sources.where.q': 'What is the source?',
    'about.sources.where.a':
      'The official COMPUTEX exhibitor directory. Each vendor page links to the exact directory entry it was built from, and every row in the fact table repeats that link.',
    'about.sources.how.q': 'How is it extracted?',
    'about.sources.how.a':
      'By a script in this repository, which you can read and run. No language model touches the fact layer, because a model that paraphrases a booth number is indistinguishable from a model that invents one.',
    'about.sources.when.q': 'How current is it?',
    'about.sources.when.a':
      'Every page carries the date it was last checked, in the frontmatter and next to each fact row. When you are reading a page, that date is the honest answer, not the date at the top of this paragraph.',
    'about.sources.wrong.q': 'What if it is wrong?',
    'about.sources.wrong.a':
      'Open an issue or send a pull request. Corrections to the fact layer need a source; that is the only requirement, and it applies equally to us and to you.',

    'about.figures.vendors': 'exhibitors on file',
    'about.figures.returning': 'with 2+ COMPUTEX editions',
    'about.figures.span': 'years covered',
    'about.figures.pages': 'pages published',

    'about.lineage.title': 'Where this came from',
    'about.lineage.p1':
      'COMPUTEX.md is a derivative of Taiwan.md, an open-source knowledge base built by Frank Wu that demonstrated something worth copying: a plain-Markdown archive, structured for machine reading, can become what a language model quotes when someone asks about a subject.',
    'about.lineage.p2':
      'The site scaffolding, the quality-gate architecture and the AI-readable layer come from there. The taxonomy, the editorial charter and every word in knowledge/ are written here. The parent project explicitly invites derivatives and asks only that lineage stay visible, which is what this section is for.',
    'about.lineage.parentLabel': 'Parent project:',
    'about.lineage.contentLicenseLabel': 'Content licence:',
    'about.lineage.codeLicenseLabel': 'Code licence:',
    'about.lineage.repoLabel': 'Repository:',

    'about.faq.title': 'Questions people actually ask',
    'about.faq.official.q': 'Is this the official COMPUTEX website?',
    'about.faq.official.a':
      'No. The official site is computextaipei.com.tw, run by TAITRA. This is an independent archive with no authorisation or endorsement from them. If that ever changes, it will say so here in plain language and the change will be in the Git history.',
    'about.faq.consent.q':
      'My company has a page here and nobody asked us. Why?',
    'about.faq.consent.a':
      'Because the page contains only facts your company already published through the official exhibitor directory: name, booth, venue, official URL and exhibiting history. Nothing on it came from anywhere else. The page names its source on every row so you can check that claim rather than take our word for it.',
    'about.faq.remove.q': 'We want the page changed or taken down.',
    'about.faq.remove.a':
      'Open an issue and say which. Corrections are usually faster and better for you than removal, but removal is a legitimate request and is handled the same way, in public, with the reason recorded.',
    'about.faq.ai.q': 'Is this AI-generated?',
    'about.faq.ai.a':
      'The fact layer is not. It is extracted mechanically and never passes through a language model. The curation layer is written by people, with AI assistance in drafting, and every page records whether a human has reviewed it. Where that flag is false, it is visible rather than hidden.',
    'about.faq.license.q': 'Can I reuse this?',
    'about.faq.license.a':
      'Yes. Content is CC BY 4.0, so commercial reuse is fine as long as you attribute. Code is MIT. Attribution is the only thing asked for, deliberately: the point of this archive is to be quoted.',
    'about.faq.lineage.q': 'Why does it look like Taiwan.md?',
    'about.faq.lineage.a':
      'Because it is a derivative of it, by design and with the parent project’s blessing. See the lineage section above.',

    'about.contact.title': 'Claim, correct, or ask',
    'about.contact.body':
      'Every change to this archive goes through a public pull request, including ours. If your company is in here, that is the same door you use.',
    'about.contact.issue': 'Open an issue',
    'about.contact.contribute': 'How to contribute',
  },

  'zh-TW': {
    'about.meta.title': '關於 COMPUTEX.md',
    'about.meta.description':
      'COMPUTEX.md 是什麼、事實從哪裡來、誰可以寫哪一層、以及怎麼修正或撤下一頁。獨立的開放檔案庫，非外貿協會或 COMPUTEX 官方網站。',

    'about.hero.title': '關於 COMPUTEX.md',
    'about.hero.subtitle': '這是什麼、事實從哪裡來、你可以怎麼改它',

    'about.disclaimer.zh':
      '本站是獨立專案，非外貿協會（TAITRA）或 COMPUTEX 官方網站，未經其授權或背書。所有資料整理自公開來源。',
    'about.disclaimer.en':
      'This is an independent project. It is not the official website of TAITRA or COMPUTEX, and carries no authorisation or endorsement from either. All data is compiled from publicly available sources.',

    'about.intro.p1':
      'COMPUTEX.md 是 COMPUTEX 參展廠商、產品與歷屆展會的開放檔案庫。一家公司一份純文字 Markdown 檔，跨年度累積，不是展期一結束就歸零。',
    'about.intro.p2':
      '展覽一年開四天，它背後的供應鏈不是。一個只在那四天存在的名錄，回答不了其他三百六十一天真正被問到的問題：這東西是誰做的，他做多久了。',
    'about.intro.p3':
      '所以這裡的單位是公司，不是活動。今年開的那一頁，明年、後年都是同一頁往上疊。',

    'about.md.title': '為什麼是 .md',
    'about.md.p1':
      '這裡的每一頁都是公開 Git repo 裡的一個 Markdown 檔。這不是技術細節，這就是產品本身。Markdown 檔可以 diff，所以每一次改動都有作者跟日期；可以直接被語言模型引用，中間不必經過渲染；哪天這個專案不再有人維護，任何人都可以把它整份接走。',
    'about.md.p2':
      '每一頁在同一個網址加上 .md 後綴就有一份純文字雙胞胎，整個檔案庫在 llms.txt 裡列成索引。機器讀到的跟你讀到的是同一份，不是刪減版。',
    'about.md.cta': '去看廠商頁',

    'about.charter.title': '編輯憲章',
    'about.charter.lead':
      '這個檔案庫是多方共編，而且各方都有商業利益。要撐得住，只能事先把「誰可以寫哪一層」講清楚。下面三條是審 PR 時真的照著執行的規則，不是自我期許。',
    'about.layers.whoLabel': '誰可以寫：',
    'about.layers.fact.title': '事實層',
    'about.layers.fact.body':
      '公司名、場館、攤位號、官方網址、產品標籤，以及逐年的參展紀錄。由腳本從官方名錄機械抽取，中間沒有任何語言模型改寫。每一列都帶出處網址與查證日期。',
    'about.layers.fact.who':
      '任何人都可以，包含公司自己，走 pull request。改動要附得上第三方可以查證的出處才會被接受。沒有出處的修正一律退回，不管它看起來多明顯正確。',
    'about.layers.curation.title': '策展層',
    'about.layers.curation.body':
      '一家公司在供應鏈裡的位置、今年跟去年比變了什麼、這一屆跟上一屆的差別、展場上哪些技術聚成一群。這些是判斷，不是紀錄。',
    'about.layers.curation.who':
      '只有中立編輯。廠商可以在 pull request 裡對策展段落提異議，異議會被公開回覆，但不能直接改那段文字。這條線一旦破了，AI 引擎就沒有理由把這裡當成廠商官網以外的東西。',
    'about.layers.blank.title': '留白',
    'about.layers.blank.body':
      '官方名錄沒公布的欄位，頁面就留空，並且寫明留空。',
    'about.layers.blank.who':
      '沒有人可以用公司官網文案、新聞稿、往年慣例或第三方彙整站去補那個空格。要補它需要可查證的來源。一頁只要有一列是推測來的，看起來再完整都不值錢。',

    'about.sources.title': '事實從哪裡來',
    'about.sources.where.q': '來源是什麼？',
    'about.sources.where.a':
      'COMPUTEX 官方參展廠商名錄。每一個廠商頁都連到它實際採用的那一筆名錄條目，事實表的每一列也各自重複那條連結。',
    'about.sources.how.q': '怎麼抽的？',
    'about.sources.how.a':
      '用這個 repo 裡的腳本，你可以讀它也可以自己跑。事實層完全不經過語言模型：一個會改寫攤位號的模型，跟一個會編造攤位號的模型，從輸出上分不出來。',
    'about.sources.when.q': '資料多新？',
    'about.sources.when.a':
      '每一頁都帶最後查證日期，寫在 frontmatter 也寫在每一列事實旁邊。你正在讀那一頁時，那個日期才是誠實的答案，不是這段文字上面的日期。',
    'about.sources.wrong.q': '寫錯了怎麼辦？',
    'about.sources.wrong.a':
      '開 issue 或直接送 pull request。修正事實層需要附出處，就這一個條件，而且這條件對我們跟對你一樣適用。',

    'about.figures.vendors': '家參展廠商在檔',
    'about.figures.returning': '家來過 2 屆以上 COMPUTEX',
    'about.figures.span': '涵蓋年份',
    'about.figures.pages': '頁已發布',

    'about.lineage.title': '這個站怎麼來的',
    'about.lineage.p1':
      'COMPUTEX.md 是 Taiwan.md 的衍生專案。Taiwan.md 是吳哲宇做的開源知識庫，它先證明了一件值得照抄的事：一個純 Markdown、為機器閱讀而結構化的檔案庫，可以變成語言模型回答某個主題時實際引用的來源。',
    'about.lineage.p2':
      '站體骨架、品質守門架構與 AI 可讀層來自那裡；分類方式、編輯憲章，以及 knowledge/ 裡的每一個字都是這裡自己寫的。母專案明文歡迎衍生，唯一的請求是讓譜系看得見，這一段就是為此存在。',
    'about.lineage.parentLabel': '母專案：',
    'about.lineage.contentLicenseLabel': '內容授權：',
    'about.lineage.codeLicenseLabel': '程式授權：',
    'about.lineage.repoLabel': '原始碼：',

    'about.faq.title': '真的被問過的問題',
    'about.faq.official.q': '這是 COMPUTEX 官網嗎？',
    'about.faq.official.a':
      '不是。官網是 computextaipei.com.tw，由外貿協會經營。本站是獨立檔案庫，沒有取得他們的授權或背書。哪天狀況改變，這裡會用白話寫清楚，而且那次改動會留在 Git 紀錄裡。',
    'about.faq.consent.q': '我們公司有一頁在這裡，但沒人問過我們。為什麼？',
    'about.faq.consent.a':
      '因為那一頁上只有貴公司已經透過官方名錄公開過的事實：公司名、攤位、場館、官方網址與參展紀錄，沒有一項來自別的地方。那一頁的每一列都標了出處，所以這句話你可以自己查，不必相信我們。',
    'about.faq.remove.q': '我們要求修改或撤下那一頁。',
    'about.faq.remove.a':
      '開一個 issue 說明要哪一種。修正通常比撤下更快，對貴公司也更有利，但撤下是正當的請求，處理方式一樣：公開進行，理由留紀錄。',
    'about.faq.ai.q': '這些是 AI 寫的嗎？',
    'about.faq.ai.a':
      '事實層不是，它是機械抽取的，完全不經過語言模型。策展層由人撰寫，草稿階段有 AI 協助，而且每一頁都記錄了人工複核狀態。沒被人工複核過的頁面，那個欄位是看得見的 false，不會藏起來。',
    'about.faq.license.q': '我可以轉用這些內容嗎？',
    'about.faq.license.a':
      '可以。內容採 CC BY 4.0，商業轉用也沒問題，標註出處即可；程式採 MIT。刻意只要求標註出處：這個檔案庫的存在目的就是要被引用。',
    'about.faq.lineage.q': '為什麼它看起來很像 Taiwan.md？',
    'about.faq.lineage.a':
      '因為它就是 Taiwan.md 的衍生專案，而且是在母專案歡迎的前提下做的。詳見上面的譜系段落。',

    'about.contact.title': '認領、修正，或提問',
    'about.contact.body':
      '這個檔案庫的每一次改動都走公開的 pull request，包含我們自己的。貴公司如果在這裡面，走的是同一道門。',
    'about.contact.issue': '開一個 issue',
    'about.contact.contribute': '貢獻指南',
  },
} as const;
