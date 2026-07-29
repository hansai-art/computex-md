/**
 * contribute.ts — /contribute 字串（zh-TW + en）
 *
 * 2026-07-29 整份改寫，跟 `contribute.template.astro` 一起。原本是 6,755 行、
 * 12 個語言，而且不只是「內容還沒換」而已，是三件會實際傷到人的事：
 *
 *   1. 表單把訪客的姓名 + email + 內容 POST 到母體的 Google Apps Script
 *      端點，然後顯示「送出成功」。填的人以為投給我們，實際上進了別人的
 *      試算表。這是活的資料外洩，不是外觀殘留。
 *   2. 母體作者的信箱 `taiwanmd@monoame.com` 在 12 個語言區塊裡被當成本站的
 *      聯絡方式公開，共 15 處。
 *   3. 「捐 token 幫忙翻譯成 8 個語言」整段。本站只有 zh-TW + en，而且它給的
 *      兩個連結都指向私有 repo 的檔案，任何人點了都是 404。
 *
 * 新版的紀律：
 *   - 只寫**現在真的可用**的參與方式。私有 repo 期間 NEVER 把「送 PR」寫成
 *     可執行的動作（送不了），也 NEVER 假裝 Booth Score 已經上線（還沒實作）。
 *   - 「本站不做的四件事」是這一頁最重要的段落。廠商共編的專案，可信度全部
 *     押在這四條上，所以它們用否定句寫死，不留模糊空間。
 */
export const contributeUI = {
  en: {
    'contribute.meta.title': 'Contribute — COMPUTEX.md',
    'contribute.meta.description':
      'Who may edit which layer, how to send a correction, how a company claims its own page, and the four things this site does not do.',

    'contribute.hero.title': 'Contribute',
    'contribute.hero.subtitle':
      'What you can change, how to send it, and what happens after you do',

    'contribute.lead':
      'This page answers three things: which layer you are allowed to change, how to send a change, and what happens once you have sent it.',

    'contribute.paths.title': 'Which layer you can change',
    'contribute.paths.lead':
      'Every page is written in three layers, and each layer has a different rule about who may write it.',
    'contribute.paths.whoLabel': 'Who:',
    'contribute.paths.noteLabel': 'Condition:',

    'contribute.paths.fact.title': 'Fact layer — corrections',
    'contribute.paths.fact.who': 'Anyone.',
    'contribute.paths.fact.body':
      'Company name, exhibit zone, hall, booth number, years exhibited, official links. These are extracted mechanically from the public exhibitor directory, so they go wrong in exactly the ways a directory goes wrong: stale entries, renamed companies, moved booths.',
    'contribute.paths.fact.note':
      'Every correction needs a source link: the official directory, the company site, or a public press release. A correction without a source is not applied.',

    'contribute.paths.claim.title': 'Claiming your own page',
    'contribute.paths.claim.who':
      'An employee or authorised representative of the company the page is about.',
    'contribute.paths.claim.body':
      'Fill in fact-layer fields the directory left blank, correct what is wrong, or ask for the whole page to be taken down.',
    'contribute.paths.claim.note':
      'Claiming costs nothing and changes nothing about how the page is ordered or displayed. There is no paid tier.',

    'contribute.paths.curation.title': 'Curation layer — objections',
    'contribute.paths.curation.who':
      'Anyone may object; only neutral editors may write.',
    'contribute.paths.curation.body':
      'Where a company sits in the industry, what changed year over year, how it compares with others in the same zone. These are judgements, not directory fields.',
    'contribute.paths.curation.note':
      'A company can object and ask for the objection to be recorded on the page, but cannot dictate what the curation layer says. That boundary is what the site is worth.',

    'contribute.how.title': 'How to send it',
    'contribute.how.lead':
      'Email is the only route right now. Include these five things so the correction can be checked without a follow-up round trip.',
    'contribute.how.item1': 'The page URL',
    'contribute.how.item2': 'Which field, or which sentence',
    'contribute.how.item3': 'What it should say',
    'contribute.how.item4':
      'A source link: official directory, company site, or press release',
    'contribute.how.item5':
      'Who you are: company representative or reader (optional)',
    'contribute.how.cta': 'Email with the template filled in',
    'contribute.how.ctaNote':
      'Opens your mail client with the five fields pre-written. Type over them.',

    'contribute.pr.title': 'Or send a pull request',
    'contribute.pr.body':
      'The source and the data are public. Every page is one Markdown file under knowledge/, so a correction is a one-line diff. A pull request is the only write path into the repository, and merging stays with a human: that boundary is the design, not a limitation.',
    'contribute.pr.cta': 'Open the repository',

    'contribute.process.title': 'What happens after you send it',
    'contribute.process.step1':
      'The source you sent is checked against what the page currently says.',
    'contribute.process.step2':
      'If it matches, the field is changed and its checked date is set to that day.',
    'contribute.process.step3':
      'If it does not match, or the source is not enough to carry the claim, you get a reply explaining why. Nothing is silently dropped.',
    'contribute.process.step4':
      'A takedown request is honoured. A short note is left at the original URL: the page is not made to look as though it never existed.',

    'contribute.rules.title': 'Four things this site does not do',
    'contribute.rules.lead':
      'A multi-party archive is only worth reading if the rules still hold when someone with a budget asks. So they are written as flat negatives.',
    'contribute.rules.one':
      'No payment changes any ordering, marker, or presentation. There is nothing here to buy.',
    'contribute.rules.two':
      'No marketing copy is written or reprinted here. Material supplied by a company does not go up as-is.',
    'contribute.rules.three':
      'The curation layer takes no dictated content, from anyone.',
    'contribute.rules.four':
      'Numbers the organiser has not published are not inferred, and not reconstructed from elsewhere. Blank stays blank.',

    'contribute.soon.title': 'Not open yet',
    'contribute.soon.lead':
      'One thing is designed but not available. It is listed here so this page does not imply more than exists.',
    'contribute.soon.score.title': 'Booth Score',
    'contribute.soon.score.body':
      'A completeness score computed mechanically from field coverage, source coverage and freshness, where marketing copy earns zero. The rule is settled; the implementation is not written. There is no ranking on the site today.',

    'contribute.contact.title': 'Contact',
    'contribute.contact.body':
      'Corrections, claims, takedowns, or a question about how any of this works.',

    'contribute.mail.subject': 'COMPUTEX.md correction',
    'contribute.mail.body':
      'Page URL:\n\nWhich field or sentence:\n\nWhat it should say:\n\nSource link:\n\nWho I am (company representative / reader, optional):\n',
  },

  'zh-TW': {
    'contribute.meta.title': '參與編輯 — COMPUTEX.md',
    'contribute.meta.description':
      '誰可以改哪一層、怎麼送出勘誤、廠商怎麼認領自己的頁面，以及本站不做的四件事。',

    'contribute.hero.title': '參與編輯',
    'contribute.hero.subtitle': '你能改什麼、怎麼送出、送出之後會發生什麼',

    'contribute.lead':
      '這一頁回答三件事：你被允許改哪一層、怎麼把改動送出來、送出之後會發生什麼。',

    'contribute.paths.title': '你能改哪一層',
    'contribute.paths.lead':
      '每一頁都分三層寫，每一層對「誰可以寫」的規定不一樣。',
    'contribute.paths.whoLabel': '誰可以改：',
    'contribute.paths.noteLabel': '條件：',

    'contribute.paths.fact.title': '事實層勘誤',
    'contribute.paths.fact.who': '任何人。',
    'contribute.paths.fact.body':
      '公司名稱、展區、館別、攤位號、參展年份、官方連結。這些是從公開參展名錄機械抽取的，所以它會錯在名錄會錯的地方：資料沒更新、公司改名、攤位換了位置。',
    'contribute.paths.fact.note':
      '每一筆更正都要附出處連結：官方名錄、公司官網，或公開新聞稿。沒有出處的更正不會採用。',

    'contribute.paths.claim.title': '廠商認領自己的頁面',
    'contribute.paths.claim.who': '該頁主體公司的員工或委任代表。',
    'contribute.paths.claim.body':
      '補上名錄沒給的事實層欄位、更正寫錯的地方，或要求整頁下架。',
    'contribute.paths.claim.note':
      '認領不收費，也不會改變這一頁的排序或呈現方式。這裡沒有付費方案。',

    'contribute.paths.curation.title': '策展層異議',
    'contribute.paths.curation.who':
      '任何人都可以提異議，但只有中立編輯能動筆。',
    'contribute.paths.curation.body':
      '這家公司在產業裡的位置、跟去年比變了什麼、跟同展區其他家怎麼對照。這些是判斷，不是名錄欄位。',
    'contribute.paths.curation.note':
      '廠商可以提出異議，並要求把異議記在該頁上，但不能指定策展層要怎麼寫。這條界線就是這個站的價值本身。',

    'contribute.how.title': '怎麼送出',
    'contribute.how.lead':
      '現在唯一的路是 email。信裡請寫齊這五件事，這樣不用來回問就能查證。',
    'contribute.how.item1': '頁面網址',
    'contribute.how.item2': '哪一個欄位、或哪一句',
    'contribute.how.item3': '正確的內容是什麼',
    'contribute.how.item4': '出處連結：官方名錄、公司官網，或新聞稿',
    'contribute.how.item5': '你的身分：廠商代表或讀者（選填）',
    'contribute.how.cta': '用填好的範本寄信',
    'contribute.how.ctaNote':
      '會開啟你的信箱程式，五個欄位已經先寫好，直接覆蓋填寫就可以。',

    'contribute.pr.title': '或者直接送 PR',
    'contribute.pr.body':
      '原始碼與資料都是公開的。每一頁就是 knowledge/ 底下的一個 Markdown 檔，所以一筆更正往往只是一行 diff。PR 是進到這個資料庫的唯一寫入口，而合併由人決定：這條界線是設計，不是限制。',
    'contribute.pr.cta': '打開資料庫',

    'contribute.process.title': '送出之後會發生什麼',
    'contribute.process.step1': '我們拿你附的出處，對照頁面上現在寫的內容。',
    'contribute.process.step2': '對得上就改，並把該欄位的查證日期更新成當天。',
    'contribute.process.step3':
      '對不上、或出處不足以支撐那句話，我們回信說明理由。不會靜默忽略。',
    'contribute.process.step4':
      '要求整頁下架會照辦，並在原網址留一段說明。不會假裝那一頁沒存在過。',

    'contribute.rules.title': '本站不做的四件事',
    'contribute.rules.lead':
      '多方共編的檔案，只有在「有預算的人來要求時規則照樣成立」的前提下才值得讀。所以這四條用否定句寫死，不留模糊空間。',
    'contribute.rules.one':
      '不接受任何付費調整排序、標記或呈現方式。這裡沒有東西可以買。',
    'contribute.rules.two':
      '不代寫、不轉貼行銷文案。廠商提供的稿件不會原樣上站。',
    'contribute.rules.three': '策展層不接受任何人指定內容。',
    'contribute.rules.four':
      '官方沒公布的數字不推測，也不從別處推算補上。留白就是留白。',

    'contribute.soon.title': '還沒開放的',
    'contribute.soon.lead':
      '有一件事已經設計好但還不能用。列在這裡，是為了不讓這一頁講得比實際多。',
    'contribute.soon.score.title': 'Booth Score 完整度分數',
    'contribute.soon.score.body':
      '由欄位覆蓋率、出處覆蓋率與新鮮度機械計算的分數，行銷文案零加分。規則已經定了，實作還沒寫。站上目前沒有任何排名。',

    'contribute.contact.title': '聯絡',
    'contribute.contact.body':
      '勘誤、認領、下架，或想問清楚上面任何一條怎麼運作。',

    'contribute.mail.subject': 'COMPUTEX.md 勘誤',
    'contribute.mail.body':
      '頁面網址：\n\n哪一個欄位或哪一句：\n\n正確的內容：\n\n出處連結：\n\n我的身分（廠商代表 / 讀者，選填）：\n',
  },
} as const;
