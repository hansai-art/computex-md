import { useTranslations } from '../i18n/utils';

/**
 * 分類的顯示設定。分類本身的 SSOT 在 src/config/categories.ts，
 * 這裡只負責「長什麼樣」（名稱走 i18n、顏色、封面）。兩邊的 key 必須一致。
 *
 * 2026-07-29 出生時的取捨：
 * - 不用 emoji 當 icon。母體每個分類配一顆 emoji，那是前幾年的預設美學，
 *   而且 emoji 在不同平台長得不一樣，不受控。改成空字串，Stage 4 視覺階段補正式圖標。
 * - cover 留空。母體用維基共享的台灣照片，那些檔案已隨 knowledge/ 一起清掉。
 *   展會版的封面應該是展場或產品照，且必須是可查證授權的圖，不是隨手抓的。
 * - 顏色刻意壓抑。全站唯一的強調色是 COMPUTEX 洋紅 #E4007E，而且只標記「此刻」
 *   （見 brand-spec.md）。分類色不能跟它搶。
 */
export const getCategoryConfigs = (t: ReturnType<typeof useTranslations>) => ({
  vendors: {
    name: t('categoryConfig.vendors'),
    description: t('categoryConfig.vendors.description'),
    icon: '',
    color: '#334155',
    colorLight: '#33415520',
    gradient: 'linear-gradient(135deg, #334155, #64748b)',
    cover: '',
  },
  products: {
    name: t('categoryConfig.products'),
    description: t('categoryConfig.products.description'),
    icon: '',
    color: '#3f3f46',
    colorLight: '#3f3f4620',
    gradient: 'linear-gradient(135deg, #3f3f46, #71717a)',
    cover: '',
  },
  editions: {
    name: t('categoryConfig.editions'),
    description: t('categoryConfig.editions.description'),
    icon: '',
    color: '#44403c',
    colorLight: '#44403c20',
    gradient: 'linear-gradient(135deg, #44403c, #78716c)',
    cover: '',
  },
  topics: {
    name: t('categoryConfig.topics'),
    description: t('categoryConfig.topics.description'),
    icon: '',
    color: '#292524',
    colorLight: '#29252420',
    gradient: 'linear-gradient(135deg, #292524, #57534e)',
    cover: '',
  },
});

const __plainCategoryConfig = getCategoryConfigs((key) => key as any);

export const categoryList = Object.keys(__plainCategoryConfig) as CategoryKey[];
export type CategoryKey = keyof typeof __plainCategoryConfig;
