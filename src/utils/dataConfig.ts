import { useTranslations } from '../i18n/utils';

export type Sector =
  | 'semiconductor'
  | 'electronicsManufacturing'
  | 'electronicComponents'
  | 'financial'
  | 'telecommunications'
  | 'foodBeverage'
  | 'shipping'
  | 'computerBrand'
  | 'steel'
  | 'petrochemical'
  | 'cement'
  | 'optics'
  | 'bicycle'
  | 'textileFiber'
  | 'transportation'
  | 'consumerElectronics'
  | 'industrialComputer'
  | 'casing'
  | 'petrochemicalPanel'
  | 'server'
  | 'pcb'
  | 'precisionMachinery'
  | 'networking'
  | 'cooling'
  | 'testing';

export type Company = {
  name: string; // from translation function
  sector: Sector; // camelCase sector type
  marketCap: number; // 億 TWD（TWSE 發行量加權市值，2026/06 snapshot）
  revenue: number; // 億 TWD（2025 全年合併營收）
  employees: number; // 約略員工數（集團/合併基準，見頁面方法說明）
  founded: number;
  ticker: string;
  articleUrl?: string; // optional link to knowledge article
};

// Sector color mapping
export const sectorColors: Record<Sector, string> = {
  semiconductor: '#3b82f6',
  electronicsManufacturing: '#f59e0b',
  financial: '#10b981',
  petrochemical: '#8b5cf6',
  electronicComponents: '#06b6d4',
  telecommunications: '#ec4899',
  foodBeverage: '#f97316',
  shipping: '#0ea5e9',
  computerBrand: '#6366f1',
  steel: '#64748b',
  cement: '#a78bfa',
  optics: '#14b8a6',
  bicycle: '#22c55e',
  textileFiber: '#d946ef',
  transportation: '#0891b2',
  consumerElectronics: '#e11d48',
  industrialComputer: '#2563eb',
  casing: '#7c3aed',
  petrochemicalPanel: '#9333ea',
  server: '#0284c7',
  pcb: '#059669',
  precisionMachinery: '#b45309',
  networking: '#0d9488',
  cooling: '#2dd4bf',
  testing: '#eab308',
};

// 台灣前 50 大上市企業（依 2026/06 TWSE 發行量加權市值排序）
// 市值：佔大盤權重 × 集中市場總市值（以台積電 ≈ NT$59兆／43.79% 錨定，TAIEX ≈ NT$134.7兆）
// 營收：2025 全年合併營收（金控為合併營業收入，含保險）。單位皆為「億 TWD」。
// 資料來源：TWSE、各公司 2025 全年營收公告、年報／ESG 報告、公開資訊觀測站。
// snapshot：2026-06；市值為近似值，僅供結構參考，不構成投資建議。
export const getCompanyConfigs = (
  t: ReturnType<typeof useTranslations>,
): Company[] => [
  {
    name: t('data.company.taiwan-semiconductor'),
    sector: 'semiconductor',
    marketCap: 590000,
    revenue: 38090,
    employees: 90557,
    founded: 1987,
    ticker: '2330',
    articleUrl: '/economy/台灣企業：台積電',
  },
  {
    name: t('data.company.delta-electronics'),
    sector: 'electronicComponents',
    marketCap: 59900,
    revenue: 5549,
    employees: 83000,
    founded: 1971,
    ticker: '2308',
    articleUrl: '/economy/台灣企業：台達電子',
  },
  {
    name: t('data.company.mediatek'),
    sector: 'semiconductor',
    marketCap: 44600,
    revenue: 5960,
    employees: 22546,
    founded: 1997,
    ticker: '2454',
    articleUrl: '/economy/台灣企業：聯發科技',
  },
  {
    name: t('data.company.hon-hai-foxconn'),
    sector: 'electronicsManufacturing',
    marketCap: 32700,
    revenue: 81000,
    employees: 826608,
    founded: 1974,
    ticker: '2317',
    articleUrl: '/economy/台灣企業：鴻海精密',
  },
  {
    name: t('data.company.ase-group'),
    sector: 'semiconductor',
    marketCap: 22700,
    revenue: 6454,
    employees: 84000,
    founded: 1984,
    ticker: '3711',
    articleUrl: '/economy/台灣企業：日月光半導體',
  },
  {
    name: t('data.company.elite-material'),
    sector: 'pcb',
    marketCap: 17400,
    revenue: 943,
    employees: 5310,
    founded: 1992,
    ticker: '2383',
  },
  {
    name: t('data.company.unimicron-technology'),
    sector: 'pcb',
    marketCap: 14800,
    revenue: 1312,
    employees: 14592,
    founded: 1990,
    ticker: '3037',
  },
  {
    name: t('data.company.accton'),
    sector: 'networking',
    marketCap: 13600,
    revenue: 2483,
    employees: 6930,
    founded: 1988,
    ticker: '2345',
  },
  {
    name: t('data.company.fubon-financial'),
    sector: 'financial',
    marketCap: 13400,
    revenue: 3815,
    employees: 43000,
    founded: 2001,
    ticker: '2881',
    articleUrl: '/economy/台灣企業：富邦金控',
  },
  {
    name: t('data.company.quanta-computer'),
    sector: 'electronicsManufacturing',
    marketCap: 12900,
    revenue: 21237,
    employees: 64935,
    founded: 1988,
    ticker: '2382',
    articleUrl: '/economy/台灣企業：廣達電腦',
  },
  {
    name: t('data.company.cathay-financial'),
    sector: 'financial',
    marketCap: 12100,
    revenue: 3492,
    employees: 54009,
    founded: 2001,
    ticker: '2882',
    articleUrl: '/economy/台灣企業：國泰金控',
  },
  {
    name: t('data.company.avc'),
    sector: 'cooling',
    marketCap: 11800,
    revenue: 1396,
    employees: 10732,
    founded: 1991,
    ticker: '3017',
  },
  {
    name: t('data.company.chunghwa-telecom'),
    sector: 'telecommunications',
    marketCap: 11200,
    revenue: 2361,
    employees: 20143,
    founded: 1996,
    ticker: '2412',
    articleUrl: '/economy/台灣企業：中華電信',
  },
  {
    name: t('data.company.ctbc-financial'),
    sector: 'financial',
    marketCap: 11000,
    revenue: 2449,
    employees: 31000,
    founded: 2002,
    ticker: '2891',
  },
  {
    name: t('data.company.umc'),
    sector: 'semiconductor',
    marketCap: 10400,
    revenue: 2376,
    employees: 20000,
    founded: 1980,
    ticker: '2303',
    articleUrl: '/economy/台灣企業：聯華電子',
  },
  {
    name: t('data.company.chroma-ate'),
    sector: 'testing',
    marketCap: 9600,
    revenue: 283,
    employees: 3582,
    founded: 1984,
    ticker: '2360',
  },
  {
    name: t('data.company.hon-precision'),
    sector: 'testing',
    marketCap: 9500,
    revenue: 303,
    employees: 800,
    founded: 2015,
    ticker: '7769',
  },
  {
    name: t('data.company.wiwynn'),
    sector: 'server',
    marketCap: 9300,
    revenue: 9507,
    employees: 7257,
    founded: 2012,
    ticker: '6669',
  },
  {
    name: t('data.company.jentech'),
    sector: 'cooling',
    marketCap: 8400,
    revenue: 203,
    employees: 1839,
    founded: 1987,
    ticker: '3653',
  },
  {
    name: t('data.company.nan-ya-plastics'),
    sector: 'petrochemical',
    marketCap: 7600,
    revenue: 2599,
    employees: 29108,
    founded: 1958,
    ticker: '1303',
  },
  {
    name: t('data.company.gold-circuit'),
    sector: 'pcb',
    marketCap: 7600,
    revenue: 597,
    employees: 8150,
    founded: 1981,
    ticker: '2368',
  },
  {
    name: t('data.company.yuanta-financial'),
    sector: 'financial',
    marketCap: 7400,
    revenue: 1284,
    employees: 15548,
    founded: 2002,
    ticker: '2885',
  },
  {
    name: t('data.company.nanya-technology'),
    sector: 'semiconductor',
    marketCap: 7100,
    revenue: 666,
    employees: 3693,
    founded: 1995,
    ticker: '2408',
  },
  {
    name: t('data.company.yageo'),
    sector: 'electronicComponents',
    marketCap: 7000,
    revenue: 1329,
    employees: 30624,
    founded: 1987,
    ticker: '2327',
  },
  {
    name: t('data.company.nan-ya-pcb'),
    sector: 'pcb',
    marketCap: 6900,
    revenue: 402,
    employees: 5920,
    founded: 1997,
    ticker: '8046',
  },
  {
    name: t('data.company.taishin-shinkong'),
    sector: 'financial',
    marketCap: 6300,
    revenue: 1509,
    employees: 30000,
    founded: 2002,
    ticker: '2887',
  },
  {
    name: t('data.company.mega-financial'),
    sector: 'financial',
    marketCap: 6200,
    revenue: 820,
    employees: 9838,
    founded: 2002,
    ticker: '2886',
  },
  {
    name: t('data.company.global-unichip'),
    sector: 'semiconductor',
    marketCap: 6100,
    revenue: 341,
    employees: 882,
    founded: 1998,
    ticker: '3443',
  },
  {
    name: t('data.company.bizlink'),
    sector: 'electronicComponents',
    marketCap: 5800,
    revenue: 712,
    employees: 20000,
    founded: 2000,
    ticker: '3665',
  },
  {
    name: t('data.company.formosa-petrochemical'),
    sector: 'petrochemical',
    marketCap: 5700,
    revenue: 6261,
    employees: 5110,
    founded: 1992,
    ticker: '6505',
  },
  {
    name: t('data.company.e-sun-financial'),
    sector: 'financial',
    marketCap: 5500,
    revenue: 918,
    employees: 9268,
    founded: 2002,
    ticker: '2884',
  },
  {
    name: t('data.company.zhen-ding'),
    sector: 'pcb',
    marketCap: 4800,
    revenue: 1825,
    employees: 48141,
    founded: 2006,
    ticker: '4958',
  },
  {
    name: t('data.company.sinopac-financial'),
    sector: 'financial',
    marketCap: 4800,
    revenue: 744,
    employees: 15268,
    founded: 2002,
    ticker: '2890',
  },
  {
    name: t('data.company.hua-nan-financial'),
    sector: 'financial',
    marketCap: 4750,
    revenue: 695,
    employees: 11423,
    founded: 2001,
    ticker: '2880',
  },
  {
    name: t('data.company.evergreen-marine'),
    sector: 'shipping',
    marketCap: 4700,
    revenue: 3790,
    employees: 13265,
    founded: 1968,
    ticker: '2603',
  },
  {
    name: t('data.company.wistron'),
    sector: 'electronicsManufacturing',
    marketCap: 4650,
    revenue: 21865,
    employees: 80000,
    founded: 2001,
    ticker: '3231',
  },
  {
    name: t('data.company.asustek'),
    sector: 'computerBrand',
    marketCap: 4600,
    revenue: 7389,
    employees: 17000,
    founded: 1989,
    ticker: '2357',
  },
  {
    name: t('data.company.taiwan-mobile'),
    sector: 'telecommunications',
    marketCap: 4400,
    revenue: 1988,
    employees: 10645,
    founded: 1997,
    ticker: '3045',
  },
  {
    name: t('data.company.first-financial'),
    sector: 'financial',
    marketCap: 4400,
    revenue: 776,
    employees: 8623,
    founded: 2003,
    ticker: '2892',
  },
  {
    name: t('data.company.winbond'),
    sector: 'semiconductor',
    marketCap: 4300,
    revenue: 894,
    employees: 8097,
    founded: 1987,
    ticker: '2344',
  },
  {
    name: t('data.company.uni-president'),
    sector: 'foodBeverage',
    marketCap: 4200,
    revenue: 6729,
    employees: 87572,
    founded: 1967,
    ticker: '1216',
  },
  {
    name: t('data.company.lite-on-technology'),
    sector: 'electronicComponents',
    marketCap: 4100,
    revenue: 1661,
    employees: 33163,
    founded: 1975,
    ticker: '2301',
  },
  {
    name: t('data.company.winway'),
    sector: 'testing',
    marketCap: 4000,
    revenue: 79,
    employees: 1200,
    founded: 2001,
    ticker: '6515',
  },
  {
    name: t('data.company.king-slide'),
    sector: 'precisionMachinery',
    marketCap: 4000,
    revenue: 175,
    employees: 1500,
    founded: 1986,
    ticker: '2059',
  },
  {
    name: t('data.company.kyec'),
    sector: 'testing',
    marketCap: 3900,
    revenue: 349,
    employees: 8600,
    founded: 1987,
    ticker: '2449',
  },
  {
    name: t('data.company.kgi-financial'),
    sector: 'financial',
    marketCap: 3900,
    revenue: 650,
    employees: 25000,
    founded: 2001,
    ticker: '2883',
  },
  {
    name: t('data.company.taiwan-cooperative-bank'),
    sector: 'financial',
    marketCap: 3800,
    revenue: 738,
    employees: 8771,
    founded: 2011,
    ticker: '5880',
  },
  {
    name: t('data.company.largan-precision'),
    sector: 'optics',
    marketCap: 3600,
    revenue: 612,
    employees: 8755,
    founded: 1987,
    ticker: '3008',
  },
  {
    name: t('data.company.fareastone'),
    sector: 'telecommunications',
    marketCap: 3500,
    revenue: 1104,
    employees: 5474,
    founded: 1997,
    ticker: '4904',
  },
  {
    name: t('data.company.formosa-plastics'),
    sector: 'petrochemical',
    marketCap: 3500,
    revenue: 1754,
    employees: 7306,
    founded: 1954,
    ticker: '1301',
  },
];

// 被 AI 供應鏈擠出前 50 大的代表性企業（2026/06）。
// 用於「跌出榜」敘事：傳產與舊消費電子如何被重新定價。
// reason 文案走 i18n（data.fellOff.*）。marketCapNow 為 2026/06 近似值（億 TWD）。
export type FellOffCompany = {
  name: string;
  ticker: string;
  marketCapNow: number;
  reason: string;
};

export const getFellOffCompanies = (
  t: ReturnType<typeof useTranslations>,
): FellOffCompany[] => [
  {
    name: t('data.company.china-steel'),
    ticker: '2002',
    marketCapNow: 3068,
    reason: t('data.fellOff.china-steel'),
  },
  {
    name: t('data.company.htc'),
    ticker: '2498',
    marketCapNow: 421,
    reason: t('data.fellOff.htc'),
  },
  {
    name: t('data.company.taiwan-cement'),
    ticker: '1101',
    marketCapNow: 1832,
    reason: t('data.fellOff.taiwan-cement'),
  },
  {
    name: t('data.company.far-eastern-new-century'),
    ticker: '1402',
    marketCapNow: 1542,
    reason: t('data.fellOff.far-eastern-new-century'),
  },
  {
    name: t('data.company.giant-manufacturing'),
    ticker: '9921',
    marketCapNow: 296,
    reason: t('data.fellOff.giant-manufacturing'),
  },
];

export type CategoryItem = {
  name: string;
  url: string;
  desc: string;
};

export type Category = {
  icon: string;
  title: string;
  description: string;
  items: CategoryItem[];
};

export const getCategories = (
  t: ReturnType<typeof useTranslations>,
): Category[] => [
  {
    icon: '📊',
    title: t('data.category.1.title'),
    description: t('data.category.1.description'),
    items: [
      {
        name: t('data.category.1.item.1.name'),
        url: 'https://data.gov.tw/',
        desc: t('data.category.1.item.1.desc'),
      },
      {
        name: t('data.category.1.item.2.name'),
        url: 'https://statdb.dgbas.gov.tw/',
        desc: t('data.category.1.item.2.desc'),
      },
      {
        name: t('data.category.1.item.3.name'),
        url: 'https://db.cec.gov.tw/',
        desc: t('data.category.1.item.3.desc'),
      },
      {
        name: t('data.category.1.item.4.name'),
        url: 'https://law.moj.gov.tw/',
        desc: t('data.category.1.item.4.desc'),
      },
      {
        name: t('data.category.1.item.5.name'),
        url: 'https://airtw.moenv.gov.tw/',
        desc: t('data.category.1.item.5.desc'),
      },
    ],
  },
  {
    icon: '🗺️',
    title: t('data.category.2.title'),
    description: t('data.category.2.description'),
    items: [
      {
        name: t('data.category.2.item.1.name'),
        url: 'https://smc.peering.tw/',
        desc: t('data.category.2.item.1.desc'),
      },
      {
        name: t('data.category.2.item.2.name'),
        url: 'https://maps.nlsc.gov.tw/',
        desc: t('data.category.2.item.2.desc'),
      },
      {
        name: t('data.category.2.item.3.name'),
        url: 'https://scweb.cwa.gov.tw/',
        desc: t('data.category.2.item.3.desc'),
      },
      {
        name: t('data.category.2.item.4.name'),
        url: 'https://fhy.wra.gov.tw/',
        desc: t('data.category.2.item.4.desc'),
      },
      {
        name: t('data.category.2.item.5.name'),
        url: 'https://env.gov.tw/',
        desc: t('data.category.2.item.5.desc'),
      },
    ],
  },
  {
    icon: '🤖',
    title: t('data.category.3.title'),
    description: t('data.category.3.description'),
    items: [
      {
        name: t('data.category.3.item.1.name'),
        url: 'https://g0v.tw/',
        desc: t('data.category.3.item.1.desc'),
      },
      {
        name: t('data.category.3.item.2.name'),
        url: 'https://g0v-jothon.kktix.cc/',
        desc: t('data.category.3.item.2.desc'),
      },
      {
        name: t('data.category.3.item.3.name'),
        url: 'https://cofacts.tw/',
        desc: t('data.category.3.item.3.desc'),
      },
      {
        name: t('data.category.3.item.4.name'),
        url: 'https://vtaiwan.tw/',
        desc: t('data.category.3.item.4.desc'),
      },
      {
        name: t('data.category.3.item.5.name'),
        url: 'https://join.gov.tw/',
        desc: t('data.category.3.item.5.desc'),
      },
    ],
  },
  {
    icon: '📰',
    title: t('data.category.4.title'),
    description: t('data.category.4.description'),
    items: [
      {
        name: t('data.category.4.item.1.name'),
        url: 'https://www.twreporter.org/',
        desc: t('data.category.4.item.1.desc'),
      },
      {
        name: t('data.category.4.item.2.name'),
        url: 'https://tfc-taiwan.org.tw/',
        desc: t('data.category.4.item.2.desc'),
      },
      {
        name: t('data.category.4.item.3.name'),
        url: 'https://www.readr.tw/',
        desc: t('data.category.4.item.3.desc'),
      },
      {
        name: t('data.category.4.item.4.name'),
        url: 'https://artouch.com/',
        desc: t('data.category.4.item.4.desc'),
      },
    ],
  },
  {
    icon: '🔬',
    title: t('data.category.5.title'),
    description: t('data.category.5.description'),
    items: [
      {
        name: t('data.category.5.item.1.name'),
        url: 'https://openmuseum.tw/',
        desc: t('data.category.5.item.1.desc'),
      },
      {
        name: t('data.category.5.item.2.name'),
        url: 'https://tcmb.culture.tw/',
        desc: t('data.category.5.item.2.desc'),
      },
      {
        name: t('data.category.5.item.3.name'),
        url: 'https://tbn.biodiv.tw/',
        desc: t('data.category.5.item.3.desc'),
      },
      {
        name: t('data.category.5.item.4.name'),
        url: 'https://huggingface.co/TAIDE',
        desc: t('data.category.5.item.4.desc'),
      },
    ],
  },
];
