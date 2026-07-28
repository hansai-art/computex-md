import type { Lang } from '../types';
import { useTranslations } from '../i18n/utils';
import counties22Zh from '../data/counties-22.json';
import counties22Ko from '../data/counties-22.ko.json';

// 22 縣市系列 route — coords + canonical key（顯示文字來自 counties-22*.json）
const COUNTIES_22_COORDS = [
  { id: 'c22-keelung', canonical: '基隆市', lat: 25.131, lng: 121.741 },
  { id: 'c22-chiayi-city', canonical: '嘉義市', lat: 23.477, lng: 120.452 },
  { id: 'c22-lienchiang', canonical: '連江縣', lat: 26.158, lng: 119.951 },
  { id: 'c22-penghu', canonical: '澎湖縣', lat: 23.566, lng: 119.563 },
  { id: 'c22-yilan', canonical: '宜蘭縣', lat: 24.752, lng: 121.755 },
  { id: 'c22-miaoli', canonical: '苗栗縣', lat: 24.561, lng: 120.821 },
  { id: 'c22-hsinchu-county', canonical: '新竹縣', lat: 24.836, lng: 121.012 },
  { id: 'c22-chiayi-county', canonical: '嘉義縣', lat: 23.452, lng: 120.685 },
  { id: 'c22-pingtung', canonical: '屏東縣', lat: 22.668, lng: 120.488 },
  { id: 'c22-hualien', canonical: '花蓮縣', lat: 23.987, lng: 121.601 },
  { id: 'c22-taitung', canonical: '臺東縣', lat: 22.755, lng: 121.144 },
  { id: 'c22-changhua', canonical: '彰化縣', lat: 24.075, lng: 120.543 },
  { id: 'c22-yunlin', canonical: '雲林縣', lat: 23.706, lng: 120.434 },
  { id: 'c22-kinmen', canonical: '金門縣', lat: 24.448, lng: 118.317 },
  { id: 'c22-nantou', canonical: '南投縣', lat: 23.916, lng: 120.684 },
  { id: 'c22-hsinchu-city', canonical: '新竹市', lat: 24.804, lng: 120.971 },
  { id: 'c22-taoyuan', canonical: '桃園市', lat: 24.994, lng: 121.301 },
  { id: 'c22-tainan', canonical: '臺南市', lat: 22.999, lng: 120.227 },
  { id: 'c22-kaohsiung', canonical: '高雄市', lat: 22.627, lng: 120.301 },
  { id: 'c22-taipei', canonical: '臺北市', lat: 25.033, lng: 121.565 },
  { id: 'c22-taichung', canonical: '臺中市', lat: 24.144, lng: 120.679 },
  { id: 'c22-new-taipei', canonical: '新北市', lat: 25.012, lng: 121.466 },
] as const;

function buildCounties22Route(
  t: ReturnType<typeof useTranslations>,
  lang: Lang,
) {
  const countiesData =
    lang === 'ko'
      ? (counties22Ko as Record<string, County22Entry>)
      : (counties22Zh as Record<string, County22Entry>);

  return {
    id: 'counties22',
    name: t('map.routes.counties22.name'),
    description: t('map.routes.counties22.description'),
    color: '#16a34a',
    stops: COUNTIES_22_COORDS.map((stop) => {
      const county = countiesData[stop.canonical];
      const displayName = county?.displayName || stop.canonical;
      return {
        id: stop.id,
        name: displayName,
        lat: stop.lat,
        lng: stop.lng,
        note: county?.core_contradiction || '',
        link: county?.link || `/geography/${stop.canonical}`,
      };
    }),
  };
}

type County22Entry = {
  displayName?: string;
  core_contradiction?: string;
  link?: string;
};

export function getMapRoutes(
  t: ReturnType<typeof useTranslations>,
  lang: Lang,
) {
  return [
    buildCounties22Route(t, lang),
    {
      id: 'nightMarkets',
      name: t('map.routes.nightMarkets.name'),
      description: t('map.routes.nightMarkets.description'),
      color: '#f39c12',
      stops: [
        {
          id: 'shilinNightMarket',
          name: t('map.stops.shilinNightMarket.name'),
          lat: 25.088,
          lng: 121.524,
          note: t('map.stops.shilinNightMarket.note'),
          link: '/food/夜市文化',
        },
        {
          id: 'raoheNightMarket',
          name: t('map.stops.raoheNightMarket.name'),
          lat: 25.051,
          lng: 121.577,
          note: t('map.stops.raoheNightMarket.note'),
          link: '/food/夜市文化',
        },
        {
          id: 'ningxiaNightMarket',
          name: t('map.stops.ningxiaNightMarket.name'),
          lat: 25.056,
          lng: 121.515,
          note: t('map.stops.ningxiaNightMarket.note'),
          link: '/food/夜市文化',
        },
        {
          id: 'fengjiaNightMarket',
          name: t('map.stops.fengjiaNightMarket.name'),
          lat: 24.179,
          lng: 120.647,
          note: t('map.stops.fengjiaNightMarket.note'),
          link: '/food/夜市文化',
        },
        {
          id: 'huayuanNightMarket',
          name: t('map.stops.huayuanNightMarket.name'),
          lat: 23.004,
          lng: 120.206,
          note: t('map.stops.huayuanNightMarket.note'),
          link: '/food/夜市文化',
        },
        {
          id: 'liuheNightMarket',
          name: t('map.stops.liuheNightMarket.name'),
          lat: 22.632,
          lng: 120.299,
          note: t('map.stops.liuheNightMarket.note'),
          link: '/food/夜市文化',
        },
      ],
    },
    {
      id: 'nationalParks',
      name: t('map.routes.nationalParks.name'),
      description: t('map.routes.nationalParks.description'),
      color: '#27ae60',
      stops: [
        {
          id: 'yangmingshanNationalPark',
          name: t('map.stops.yangmingshanNationalPark.name'),
          lat: 25.158,
          lng: 121.549,
          note: t('map.stops.yangmingshanNationalPark.note'),
          link: '/nature/國家公園',
        },
        {
          id: 'tarokoNationalPark',
          name: t('map.stops.tarokoNationalPark.name'),
          lat: 24.158,
          lng: 121.621,
          note: t('map.stops.tarokoNationalPark.note'),
          link: '/nature/國家公園',
        },
        {
          id: 'yushanNationalPark',
          name: t('map.stops.yushanNationalPark.name'),
          lat: 23.47,
          lng: 120.957,
          note: t('map.stops.yushanNationalPark.note'),
          link: '/nature/國家公園',
        },
        {
          id: 'alishanScenicArea',
          name: t('map.stops.alishanScenicArea.name'),
          lat: 23.51,
          lng: 120.7,
          note: t('map.stops.alishanScenicArea.note'),
          link: '/nature/阿里山',
        },
        {
          id: 'sunMoonLakeScenicArea',
          name: t('map.stops.sunMoonLakeScenicArea.name'),
          lat: 23.863,
          lng: 120.917,
          note: t('map.stops.sunMoonLakeScenicArea.note'),
          link: '/nature/日月潭',
        },
        {
          id: 'kentingNationalPark',
          name: t('map.stops.kentingNationalPark.name'),
          lat: 21.948,
          lng: 120.803,
          note: t('map.stops.kentingNationalPark.note'),
          link: '/nature/國家公園',
        },
      ],
    },
    {
      id: 'historyTrail',
      name: t('map.routes.historyTrail.name'),
      description: t('map.routes.historyTrail.description'),
      color: '#e74c3c',
      stops: [
        {
          id: 'anpingFort',
          name: t('map.stops.anpingFort.name'),
          lat: 22.998,
          lng: 120.161,
          note: t('map.stops.anpingFort.note'),
          link: '/history/荷蘭與西班牙殖民時期',
        },
        {
          id: 'chikanTower',
          name: t('map.stops.chikanTower.name'),
          lat: 22.998,
          lng: 120.203,
          note: t('map.stops.chikanTower.note'),
          link: '/history/鄭氏時期',
        },
        {
          id: 'lukang',
          name: t('map.stops.lukang.name'),
          lat: 24.055,
          lng: 120.437,
          note: t('map.stops.lukang.note'),
          link: '/culture/台灣老街文化與商業街區',
        },
        {
          id: 'presidentialOffice',
          name: t('map.stops.presidentialOffice.name'),
          lat: 25.04,
          lng: 121.512,
          note: t('map.stops.presidentialOffice.note'),
          link: '/history/日本殖民統治',
        },
        {
          id: 'chiangKaiShekMemorialHall',
          name: t('map.stops.chiangKaiShekMemorialHall.name'),
          lat: 25.036,
          lng: 121.522,
          note: t('map.stops.chiangKaiShekMemorialHall.note'),
          link: '/history/戒嚴時期',
        },
        {
          id: 'legislativeYuan',
          name: t('map.stops.legislativeYuan.name'),
          lat: 25.044,
          lng: 121.521,
          note: t('map.stops.legislativeYuan.note'),
          link: '/society/太陽花學運',
        },
      ],
    },
    {
      id: 'oldStreets',
      name: t('map.routes.oldStreets.name'),
      description: t('map.routes.oldStreets.description'),
      color: '#9b59b6',
      stops: [
        {
          id: 'dihuaStreet',
          name: t('map.stops.dihuaStreet.name'),
          lat: 25.057,
          lng: 121.51,
          note: t('map.stops.dihuaStreet.note'),
          link: '/culture/大稻埕',
        },
        {
          id: 'jiufenOldStreet',
          name: t('map.stops.jiufenOldStreet.name'),
          lat: 25.109,
          lng: 121.845,
          note: t('map.stops.jiufenOldStreet.note'),
          link: '/culture/九份',
        },
        {
          id: 'lukangOldStreet',
          name: t('map.stops.lukangOldStreet.name'),
          lat: 24.055,
          lng: 120.437,
          note: t('map.stops.lukangOldStreet.note'),
          link: '/culture/台灣老街文化與商業街區',
        },
        {
          id: 'anpingOldStreet',
          name: t('map.stops.anpingOldStreet.name'),
          lat: 22.998,
          lng: 120.161,
          note: t('map.stops.anpingOldStreet.note'),
          link: '/history/安平',
        },
        {
          id: 'qishanOldStreet',
          name: t('map.stops.qishanOldStreet.name'),
          lat: 22.889,
          lng: 120.483,
          note: t('map.stops.qishanOldStreet.note'),
          link: '/culture/旗山',
        },
        {
          id: 'tamsuiOldStreet',
          name: t('map.stops.tamsuiOldStreet.name'),
          lat: 25.17,
          lng: 121.44,
          note: t('map.stops.tamsuiOldStreet.note'),
          link: '/culture/淡水',
        },
      ],
    },
  ];
}
