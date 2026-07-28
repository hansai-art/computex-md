---
title: 'TRANSLATION-id'
description: 'Panduan terjemahan Bahasa Indonesia — Taiwan sebagai negara + Tiongkok/Tionghoa/Cina disambiguation + romanisasi Wade-Giles + leksikon anti-framing RRT + register Kompas/Tempo'
type: 'editorial-canonical'
status: 'canonical'
current_version: 'v1.0'
last_updated: 2026-07-18
last_session: '2026-07-18-twmd-language-birth-id'
sister_docs:
  - 'TRANSLATION-en.md'
  - 'TRANSLATION-ja.md'
  - 'TRANSLATION-ko.md'
  - 'TRANSLATION-es.md'
  - 'TRANSLATION-fr.md'
upstream_canonical:
  - '../EDITORIAL.md'
  - '../TERMINOLOGY.md'
  - '../../pipelines/TRANSLATION-PIPELINE.md'
  - '../../pipelines/SQUEEZE-MODELS-MAX-PIPELINE.md'
  - '../../pipelines/LANGUAGE-BIRTH-CHECKLIST.md'
research_evidence: '../../../reports/evolve-2026-07-18-language-branches.md'
audience: 'translator (human + AI)'
---

# TRANSLATION-id — Panduan Terjemahan Bahasa Indonesia Taiwan.md

> Dasar pemilihan bahasa ini (SC 5.521 impression / CTR 0,3% + komunitas pekerja migran Taiwan terbesar + jangkauan populasi 252 juta penutur, #10 dunia) ada di [reports/evolve-2026-07-18-language-branches.md](../../../reports/evolve-2026-07-18-language-branches.md). **Dokumen ini adalah panduan pra-lahir** — ditulis pada tahap BIRTH-CHECKLIST v2.0 Stage 2, sebelum `knowledge/id/` memiliki satu artikel pun. Belum ada korpus id untuk diaudit, sehingga contoh-contoh di sini diproyeksikan dari pola lintas-bahasa yang sudah terverifikasi di TRANSLATION-es.md/TRANSLATION-fr.md/TRANSLATION-ja.md/TRANSLATION-ko.md, bukan laporan pembersihan yang sudah dieksekusi. Register: **Bahasa Indonesia baku, rasa jurnalisme budaya Kompas/Tempo** — akrab tapi tidak informal (bukan gaya gue/lu Jakarta).

## TL;DR — 5 aturan prioritas tertinggi

1. **`Taiwan` tanpa perubahan ejaan** di seluruh badan teks, frontmatter, keterangan gambar, dan deskripsi SEO — namanya sudah identik dalam Bahasa Indonesia, tidak perlu di-Indonesiakan. Bentuk institusional formal: **`Republik Tiongkok (Taiwan)`** — jangan pernah `Republik Tiongkok` sendirian (bisa tertukar dengan Republik Rakyat Tiongkok/RRT, nama resmi RRC).
2. **Prinsip "negara" dipakai dengan percaya diri**: Taiwan.md menyebut Taiwan sebagai `negara` tanpa ragu-ragu — presiden, pemerintah, konstitusi, pemilu, kedaulatan. Hindari kalimat berpagar seperti "wilayah yang menyebut dirinya negara" atau "entitas yang mengklaim status negara" — pemagaran semacam itu adalah bentuk halus dari framing RRT, bukan netralitas.
3. **Tiongkok / Tionghoa / Cina — tiga kata, tiga makna, jangan tertukar** (jebakan terbesar bahasa ini, lihat §1 dan §6): `Tiongkok` = negara RRT (geopolitik), `Tionghoa` = etnis/budaya Tionghoa (termasuk warisan leluhur sebagian orang Taiwan), `Cina` = istilah lama yang dihindari sejak Keppres No. 12/2014 karena konotasi diskriminatif era Orde Baru. Orang Taiwan disebut **`orang Taiwan`** — bukan `orang Tionghoa`, apalagi `orang Cina`.
4. **Wade-Giles untuk nama tokoh dan tempat Taiwan, bukan pinyin RRT**: `Tsai Ing-wen` (bukan `Cai Yingwen`), `Kaohsiung` (bukan `Gaoxiong`), `Hsinchu` (bukan `Xinzhu`). Urutan nama: marga dulu, nama diri kemudian, tanpa dibalik ala Barat.
5. **Leksikon anti-framing RRT**: dilarang `Taiwan, Tiongkok`, `provinsi Taiwan`, `provinsi pemberontak`/`pulau pemberontak`, `otoritas Taipei`, `reunifikasi` (sebagai fakta), `pulau Taiwan` sebagai pengganti status negara, `satu Tiongkok` tanpa konteks bahwa itu adalah posisi RRT bukan fakta. Lihat tabel lengkap di §6.

## 1. Penyebutan negara / wilayah

| Asal (zh-TW)    | Bahasa Indonesia Taiwan.md                                            | Kapan dipakai                                                    | Jangan pernah                                                                     | Catatan                                                     |
| --------------- | --------------------------------------------------------------------- | ---------------------------------------------------------------- | --------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| 台灣            | **Taiwan**                                                            | Default, di semua konteks                                        | `Formosa` (kontemporer), `provinsi Taiwan`, `pulau Taiwan` (sbg pengganti negara) | Ejaan identik dengan Inggris, tidak perlu adaptasi          |
| 中華民國        | **Republik Tiongkok (Taiwan)**                                        | Institusi formal, konstitusi, hukum internasional, kutipan resmi | `Republik Tiongkok` sendirian (tertukar RRT)                                      | Paralel dengan pola es/fr — disambiguasi wajib pakai kurung |
| 中華台北        | **Taipei Tionghoa** / **`Chinese Taipei`** (istilah asli IOC)         | Hanya konteks Olimpiade/IOC/APEC/WHA                             | Sebagai sinonim kasual untuk Taiwan                                               | Rezim penamaan olahraga khusus, jangan diperluas            |
| 兩岸 / 海峽兩岸 | **lintas selat** / **hubungan lintas selat**                          | Hubungan politik RRT–Taiwan                                      | `saudara lintas selat` (framing RRT)                                              | Tanpa mengandaikan kekerabatan/persaudaraan                 |
| 中國大陸        | **Tiongkok daratan** (hanya saat kontras geografis relevan)           | Konteks historis atau kontras eksplisit dengan Taiwan/Hong Kong  | Sebagai sinonim netral untuk `Tiongkok` (mengandaikan "satu Tiongkok")            | Di luar konteks kontras, gunakan `Tiongkok` saja            |
| 中國            | **Tiongkok** / **Republik Rakyat Tiongkok (RRT)**                     | Merujuk negara RRT                                               | `Cina` dalam suara narasi Taiwan.md                                               | Selalu dibedakan dari Republik Tiongkok (Taiwan)            |
| 我國            | **Taiwan** / **negara kita** (bila suara adalah kutipan orang Taiwan) | Reformulasi sesuai konteks                                       | Terjemahan literal tanpa rekontekstualisasi                                       | Bergantung konteks kutipan                                  |
| 台灣海峽        | **Selat Taiwan**                                                      | Geografi                                                         | `selat Taiwan` huruf kecil di awal kalimat                                        | Kapitalisasi standar nama geografis                         |

**Tentang prinsip "negara" (poin TL;DR #2)**: hindari pelunakan seperti "wilayah otonom" atau "daerah yang diperebutkan" — itu konsesi ke narasi RRT, bukan netralitas. Pakai kosakata kenegaraan penuh: `presiden Taiwan`, `pemerintah Taiwan`, `pemilihan umum Taiwan`, `konstitusi Republik Tiongkok`, `kedaulatan Taiwan`, tanpa tanda kutip ironis atau kualifikasi berlebihan.

## 2. Romanisasi nama tokoh — Wade-Giles + urutan marga-nama

**Aturan**:

- Urutan **marga + nama diri** (pola Tionghoa), tidak dibalik ala Barat
- Sebutan kedua: **marga saja** (`Tsai`), tidak pernah nama diri saja
- **Tanda hubung** antara dua suku kata nama diri: `Ing-wen`, `Ching-te`, `Kai-shek`. Jangan `Ing Wen` (terpisah), jangan `Ingwen` (menyatu tanpa tanda hubung)
- Tambahkan aksara Han dalam kurung pada sebutan pertama untuk artikel biografi: `Audrey Tang (唐鳳)`
- **Nama masyarakat adat Taiwan**: transliterasi dari ejaan Latin resmi Taiwan (`Kolas Yotaka`), bukan dari Mandarin
- **Jangan** menerapkan konvensi ejaan marga Tionghoa-Indonesia (mis. `Tan`, `Lie`, `Oei`, `Go` — hasil adaptasi dialek Hokkien di Indonesia) ke tokoh Taiwan. Dua sistem ini berasal dari komunitas berbeda; menyamakan keduanya adalah kesalahan kategori, bukan sekadar gaya

**Daftar tokoh yang paling sering dirujuk**:

| 漢字            | Taiwan.md (id)                | Pinyin RRT (JANGAN) |
| --------------- | ----------------------------- | ------------------- |
| 蔡英文          | **Tsai Ing-wen**              | Cai Yingwen         |
| 賴清德          | **Lai Ching-te**              | Lai Qingde          |
| 馬英九          | **Ma Ying-jeou**              | Ma Yingjiu          |
| 陳水扁          | **Chen Shui-bian**            | Chen Shuibian       |
| 李登輝          | **Lee Teng-hui**              | Li Denghui          |
| 蔣介石 / 蔣中正 | **Chiang Kai-shek**           | Jiang Jieshi        |
| 蔣經國          | **Chiang Ching-kuo**          | Jiang Jingguo       |
| 柯文哲          | **Ko Wen-je**                 | Ke Wenzhe           |
| 唐鳳            | **Audrey Tang**               | Tang Feng           |
| 吳釗燮          | **Joseph Wu**                 | Wu Zhaoxie          |
| 蕭美琴          | **Hsiao Bi-khim**             | Xiao Meiqin         |
| 張忠謀          | **Morris Chang**              | Zhang Zhongmou      |
| 黃仁勳          | **Jensen Huang**              | Huang Renxun        |
| 李安            | **Ang Lee**                   | Li An               |
| 侯孝賢          | **Hou Hsiao-hsien**           | Hou Xiaoxian        |
| 楊德昌          | **Edward Yang**               | Yang Dechang        |
| 林懷民          | **Lin Hwai-min**              | Lin Huaimin         |
| 鄧麗君          | **Teresa Teng**               | Deng Lijun          |
| 張惠妹          | **A-mei** / **Chang Hui-mei** | Zhang Huimei        |
| 張懸 / 安溥     | **Deserts Chang** / **Anpu**  | Zhang Xuan          |

**Catatan konteks khusus id**: pembaca yang pernah bekerja di Taiwan lebih mengenal ejaan Wade-Giles dari plakat jalan dan KTP kerja ketimbang pinyin RRT yang kadang salah kutip di media Indonesia. Taiwan.md ikut realitas lapangan Taiwan, bukan kesalahan media pihak ketiga.

### ⚠️ Aturan krusial: jangan ganti nama asing dengan nama terkenal

**Menemui nama Taiwan yang tidak ada di tabel di atas — transliterasikan.
Jangan menggantinya dengan nama tokoh terkenal.**

Kasus nyata (2026-07-25, batch Arab pertama; risiko sama untuk bahasa
Indonesia): sumber Tionghoa menulis «mantan Kepala Badan Kesehatan **Hsu
Tzu-chiu** (許子秋) mendengar putrinya…», terjemahan menghasilkan «seorang
pejabat tinggi kesehatan, **yaitu Chiang Ching-kuo**» — kepala badan diganti
presiden. Ini bukan kekeliruan antara dua tokoh yang sama-sama dikenal (jebakan
di §12) melainkan **pengisian kekosongan**: model tidak tahu namanya lalu
memasang nama politik Taiwan paling sering muncul di data latihnya.

Pencegahan lebih murah: **nama asing ditransliterasi, dengan aksara Tionghoa
asli dalam kurung**, misalnya «Hsu Tzu-chiu (許子秋)».

## 3. Romanisasi nama tempat

**Kota** (Wade-Giles resmi Taiwan, bukan pinyin RRT) — **prinsip: jangan mengindonesiakan ejaan** (mis. jangan `Kaosiung`, jangan `Taipe`). Ejaan Latin dipertahankan persis seperti bentuk internasional:

| 漢字        | Taiwan.md (id)                             | Pinyin RRT (JANGAN) |
| ----------- | ------------------------------------------ | ------------------- |
| 臺北 / 台北 | **Taipei**                                 | Taibei              |
| 高雄        | **Kaohsiung**                              | Gaoxiong            |
| 臺中 / 台中 | **Taichung**                               | Taizhong            |
| 臺南 / 台南 | **Tainan**                                 | Tainan              |
| 新竹        | **Hsinchu**                                | Xinzhu              |
| 基隆        | **Keelung**                                | Jilong              |
| 桃園        | **Taoyuan**                                | Taoyuan             |
| 花蓮        | **Hualien**                                | Hualian             |
| 宜蘭        | **Yilan**                                  | Yilan               |
| 台東        | **Taitung**                                | Taidong             |
| 屏東        | **Pingtung**                               | Pingdong            |
| 嘉義        | **Chiayi**                                 | Jiayi               |
| 苗栗        | **Miaoli**                                 | Miaoli              |
| 彰化        | **Changhua**                               | Zhanghua            |
| 雲林        | **Yunlin**                                 | Yunlin              |
| 南投        | **Nantou**                                 | Nantou              |
| 新北市      | **Taipei Baru** (kota) / `New Taipei City` | —                   |

**Pulau luar** (waspada disambiguasi 馬祖 pulau vs 媽祖 dewi — lihat juga §4):

| 漢字 | Taiwan.md (id)                        | Catatan                                                                  |
| ---- | ------------------------------------- | ------------------------------------------------------------------------ |
| 金門 | **Kinmen**                            | `Quemoy` bisa dipakai dalam konteks Perang Dingin ("Krisis Quemoy 1958") |
| 馬祖 | **Matsu** (kepulauan, Wade-Giles)     | **Kritis**: bedakan dari 媽祖 `Mazu` (dewi, pinyin) — lihat §4           |
| 澎湖 | **Penghu** / **Kepulauan Pescadores** | Kedua bentuk lazim dipakai                                               |
| 綠島 | **Pulau Hijau** / `Ludao`             | —                                                                        |
| 蘭嶼 | **Pulau Anggrek** / `Lanyu`           | —                                                                        |

**Gunung, danau, ngarai**:

- 玉山 → **`Gunung Yushan`** + glosa pada sebutan pertama: "(secara harfiah, _Gunung Giok_)". Jangan pakai `Gunung Giok` sebagai istilah utama.
- 阿里山 → **`Alishan`** atau **`Gunung Alishan`**
- 日月潭 → **`Danau Matahari-Bulan`** (terjemahan semantik yang sudah baku)
- 太魯閣 → **`Taroko`** atau **`Ngarai Taroko`**
- 中央山脈 → **`Pegunungan Tengah`**
- 淡水河 → **`Sungai Tamsui`**

**Distrik dan kawasan**: pola `distrik Xinyi` — jangan terjemahkan jadi `kecamatan` (beda tingkat administratif). Untuk kawasan bernuansa budaya sehari-hari, `kawasan Ximending` bisa diterima.

## 4. Leksikon budaya

### Kuliner

**Prinsip**: transliterasi + glosa pada sebutan pertama untuk hidangan ikonik; terjemahan langsung bila transparan. Bahasa Indonesia unik karena sudah memiliki kosakata pinjaman Hokkien yang mapan dari komunitas Tionghoa-Indonesia (`bakmi`, `bakpao`, `cap cai`, `kwetiau`, `lumpia`, `tahu`, `taoge`) — manfaatkan kosakata yang sudah dikenal pembaca, tapi jangan samakan hidangan spesifik Taiwan dengan versi Indonesia-Tionghoa yang sudah berbeda resep dan sejarah.

| 漢字     | Taiwan.md (id)                                 | Catatan                                                       |
| -------- | ---------------------------------------------- | ------------------------------------------------------------- |
| 滷肉飯   | **`lu rou fan`** (nasi babi kecap ala Taiwan)  | Jangan samakan dengan nasi babi kecap gaya Indonesia-Tionghoa |
| 牛肉麵   | **`niu rou mian`** / **`mi sapi Taiwan`**      | Kedua bentuk lazim                                            |
| 珍珠奶茶 | **`bubble tea`** / **`teh susu mutiara`**      | Kata pinjaman sudah sangat lazim, terutama kalangan muda      |
| 鳳梨酥   | **`kue nanas Taiwan`**                         | Istilah pariwisata yang sudah baku                            |
| 小籠包   | **`xiaolongbao`** (pangsit kukus berkuah)      | Dikenal luas lewat gerai Din Tai Fung di Jakarta sejak 2012   |
| 臭豆腐   | **`tahu bau`**                                 | Terjemahan langsung baku                                      |
| 蚵仔煎   | **`omelet tiram Taiwan`**                      | Terjemahan langsung                                           |
| 雞排     | **`ayam goreng Taiwan`** (potongan besar)      | Beda dari ayam goreng Indonesia — jajanan malam khas          |
| 刈包     | **`gua bao`** (bakpao lipat isi babi)          | Istilah internasional + glosa                                 |
| 夜市     | **`pasar malam`**                              | Padanan alami, tak perlu transliterasi                        |
| 小吃     | **`jajanan khas`** / **`camilan khas Taiwan`** | Tanpa transliterasi `xiaochi`                                 |

### Agama dan mitologi rakyat

- 媽祖 → **`Mazu`** (dewi laut, pinyin). UNESCO mencatatnya sebagai "kepercayaan dan ritual Mazu". **Selalu bedakan** dari 馬祖 `Matsu` (kepulauan, §3) — kesalahan tukar ini paling sering terjadi karena ejaan mirip.
- 觀音 → **`Guanyin`** (Bodhisattva Welas Asih)
- 廟 → **`kelenteng`** (istilah baku Indonesia untuk rumah ibadah rakyat Tionghoa/Tao — beda dari `vihara` [Buddha], `pura` [Hindu], `masjid` [Islam], `gereja` [Kristen]). Jangan pakai `kuil` sebagai default — `kuil` lebih lazim untuk konteks Jepang/Hindu di telinga pembaca Indonesia
- 拜拜 → **`sembahyang`** + glosa "ritual persembahan dengan dupa"

### Islam di Taiwan — tanggung jawab khusus versi bahasa ini

Indonesia adalah negara berpenduduk Muslim terbesar di dunia. Komunitas pekerja migran Muslim Indonesia adalah bagian nyata lanskap keagamaan Taiwan hari ini (per `Culture/islam-in-taiwan.md`: ~260.000 dari total ~300.000 Muslim di Taiwan adalah pekerja migran, mayoritas Indonesia). Ketepatan dan rasa hormat pada kosakata Islam bukan opsional untuk versi id — ini audiens yang membaca kisah komunitasnya sendiri.

**Aturan dasar**:

- **`masjid`** — ejaan baku, bukan `mesjid` (ejaan lama, sudah tidak dipakai sejak EYD)
- **`Muslim`** — huruf kapital saat merujuk penganut Islam (konvensi Indonesia mengapitalkan nomina agama), bukan `muslim` huruf kecil
- **`Islam`** — selalu kapital
- **`halal`** — sudah kata baku Indonesia, tak perlu diterjemahkan
- **`Idulfitri`** (ejaan gabung baku KBBI; `Idul Fitri` dua kata juga lazim di media) — jangan pakai bentuk Inggris `Eid al-Fitr` sebagai istilah utama
- **`salat Jumat`** — bukan `sholat Jumat` (ejaan tidak baku); banyak pekerja rumah tangga Muslim kesulitan hadir berjamaah karena tinggal serumah dengan majikan
- **`hijab`** — kata pinjaman baku di Indonesia, dipakai apa adanya
- **`sertifikasi halal`** — konteks restoran/produk bersertifikat (264 restoran per 2025, per artikel)
- Masjid penting: **Masjid Raya Taipei** (清真寺 tertua Taiwan, Jalan Xinsheng), **Masjid Longgang** (龍岡清真寺, Zhongli — pusat sejarah Muslim Yunnan-Tionghoa). Pakai nama ini, bukan transliterasi ad hoc
- **Jangan romantisasi atau eksotisasi**: sajikan Islam di Taiwan sebagai keragaman keagamaan yang faktual dan bermartabat, bukan "fenomena buruh asing" semata. Keturunan Hui dari Quanzhou (klan Guo di Lukang, klan Ding di Taixi, era Zheng Chenggong abad ke-17) mendahului gelombang migran abad ke-20 — akar sejarah, bukan hanya cerita kontemporer

**Kosakata pekerja migran (persinggungan budaya id yang paling penting)**:

| Istilah zh/EN                                  | Taiwan.md (id)                                        | Catatan                                                                                                                                         |
| ---------------------------------------------- | ----------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| 移工 (migrant worker, umum)                    | **`pekerja migran Indonesia (PMI)`**                  | Istilah resmi BP2MI sejak 2020, gantikan `TKI` di konteks formal; `TKI` tetap dipakai dalam kutipan lama                                        |
| 家庭看護工 (home caregiver)                    | **`pekerja perawatan lansia`** / **`caregiver`**      | Sektor terbesar pekerja migran Indonesia di Taiwan                                                                                              |
| 漁工 (fishing worker)                          | **`pekerja perikanan`** / **`ABK (Anak Buah Kapal)`** | Sektor kedua terbesar, rawan isu ketenagakerjaan                                                                                                |
| 廠工 (factory worker)                          | **`pekerja pabrik`**                                  | —                                                                                                                                               |
| 新住民 (marriage/naturalized migrant)          | **`warga baru`** / **`pendatang melalui perkawinan`** | **Beda kategori dari pekerja migran** — pasangan kawin campur yang menetap/jadi WN Taiwan, bukan pekerja kontrak. Jangan disamakan dengan `PMI` |
| 台北車站 (Taipei Main Station, konteks Minggu) | **Stasiun Utama Taipei**                              | Lobi berlantai kotak hitam-putih jadi tempat berkumpul mingguan komunitas Muslim Indonesia saat libur                                           |

### Festival

| 漢字             | Taiwan.md (id)                                                           |
| ---------------- | ------------------------------------------------------------------------ |
| 春節 / 過年      | **`Tahun Baru Imlek`** (didahulukan daripada `Tahun Baru Tionghoa`)      |
| 中秋節           | **`Festival Pertengahan Musim Gugur`**                                   |
| 端午節           | **`Festival Perahu Naga`**                                               |
| 元宵節           | **`Festival Lampion`**                                                   |
| 清明節           | **`Festival Qingming`** / **`Hari Sapu Kubur`**                          |
| 七夕             | **`Qixi`** / **`Hari Kasih Sayang Tionghoa`**                            |
| 中元節           | **`Festival Hantu`** / **`Festival Zhongyuan`**                          |
| 雙十節           | **`Hari Ganda Sepuluh`** / **`Hari Nasional Republik Tiongkok`**         |
| 二二八和平紀念日 | **`Hari Perdamaian 228`** / **`Hari Peringatan Perdamaian 28 Februari`** |

### Bahasa

| 漢字          | Taiwan.md (id)                                                                                    |
| ------------- | ------------------------------------------------------------------------------------------------- |
| 國語 / 華語   | **`bahasa Mandarin`** / **`Mandarin Taiwan`** (saat dibedakan dari Mandarin RRT)                  |
| 台語 / 台灣話 | **`bahasa Taiwan`** / **`Hokkien Taiwan`** (istilah spesifik untuk menghindari ambiguitas)        |
| 閩南語        | **`Minnan`** / **`Hokkien`**                                                                      |
| 客家話        | **`bahasa Hakka`**                                                                                |
| 原住民語      | **`bahasa-bahasa masyarakat adat Taiwan`** / **`rumpun bahasa Formosa`** (linguistik Austronesia) |

### Transportasi / perkotaan

- 高鐵 → **`kereta cepat Taiwan`** (THSR / HSR)
- 捷運 → **`MRT`** (MRT Taipei, MRT Kaohsiung — mengikuti istilah yang sudah dikenal pembaca Indonesia dari MRT Jakarta)
- 老街 → **`jalan tua`** / `lao jie`

## 5. Istilah politik / historis sensitif

| 漢字       | Taiwan.md (id)                                                                         | Catatan                                                        |
| ---------- | -------------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| 二二八事件 | **`Peristiwa 228`** / **`Insiden 28 Februari`** / **`Pembantaian 228`** (bila represi) | Sudah baku secara akademis                                     |
| 白色恐怖   | **`Teror Putih`** (kapital sbg periode sejarah bernama, 1949–1987)                     | Huruf kecil hanya pemakaian generik                            |
| 戒嚴       | **`darurat militer`** (huruf kecil); `periode darurat militer (1949–1987)`             | 38 tahun 57 hari — salah satu darurat militer terlama di dunia |
| 解嚴       | **`pencabutan darurat militer`**                                                       | —                                                              |
| 民國紀年   | **Konversi diam-diam ke kalender Masehi** di badan teks                                | Notasi ganda hanya di kutipan/dokumen hukum                    |
| 本省人     | **`benshengren`** + glosa "penduduk lokal, keturunan migran sebelum 1945"              | Pinyin + glosa pada sebutan pertama                            |
| 外省人     | **`waishengren`** + glosa "migran daratan, tiba bersama KMT 1945–1949"                 | Struktur kunci sejarah politik pasca-1945                      |
| 日治時期   | **`periode kolonial Jepang`** (1895–1945)                                              | Hindari `pendudukan Jepang` saja (anakronistik)                |
| 民主化     | **`demokratisasi`**                                                                    | —                                                              |
| 原住民     | **`masyarakat adat Taiwan`** / **`penduduk asli Taiwan`** (didahulukan)                | Hindari `gaoshan` (高山族, istilah bercorak RRT)               |
| 國民黨     | **`Kuomintang (KMT)`** / **`Partai Nasionalis Tiongkok`**                              | Kuomintang sudah baku di media Indonesia                       |
| 民進黨     | **`Partai Progresif Demokratik (DPP)`**                                                | Akronim Inggris `DPP` dipertahankan                            |
| 台灣民眾黨 | **`Partai Rakyat Taiwan (TPP)`**                                                       | —                                                              |
| 時代力量   | **`New Power Party`** / **`Kekuatan Zaman Baru`**                                      | Partai kecil, jarang diliput media Indonesia                   |
| 行政院     | **`Yuan Eksekutif`**                                                                   | "Yuan" istilah konstitusional ROC yang spesifik                |
| 立法院     | **`Yuan Legislatif`**                                                                  | —                                                              |
| 司法院     | **`Yuan Yudikatif`**                                                                   | —                                                              |
| 總統府     | **`Kantor Kepresidenan`**                                                              | —                                                              |
| 外交部     | **`Kementerian Luar Negeri`** (MOFA)                                                   | —                                                              |
| 國軍       | **`Angkatan Bersenjata Taiwan`** / **`Tentara Republik Tiongkok`**                     | —                                                              |

## 6. Leksikon anti-kebocoran framing RRT

| Kode-RRT                                                | Pengganti Taiwan.md                                                       | Tingkat | Pengecualian                                                                                                            |
| ------------------------------------------------------- | ------------------------------------------------------------------------- | ------- | ----------------------------------------------------------------------------------------------------------------------- |
| `Taiwan, Tiongkok` / `Taiwan, China`                    | **`Taiwan`**                                                              | kritis  | Hanya artikel yang membahas pelabelan itu sendiri                                                                       |
| `Taiwan, provinsi Tiongkok`                             | **`Taiwan`**                                                              | kritis  | Hanya artikel meta soal pelabelan ISO 3166                                                                              |
| `provinsi Taiwan` / `provinsi Tiongkok Taiwan`          | **`Taiwan`** / **`Republik Tiongkok (Taiwan)`**                           | kritis  | —                                                                                                                       |
| `provinsi pemberontak` / `pulau pemberontak`            | **`Taiwan`**                                                              | kritis  | Tidak pernah                                                                                                            |
| `pulau Taiwan` (pengganti status negara)                | **`Taiwan`**                                                              | tinggi  | Konteks geografi eksplisit sah ("pulau Taiwan di Pasifik Barat")                                                        |
| `saudara Tionghoa se-selat` / `saudara lintas selat`    | **`warga Taiwan`** / **`komunitas Taiwan`**                               | tinggi  | Kutipan langsung sumber RRT                                                                                             |
| `Taipei Tionghoa` / `Chinese Taipei` (di luar konteks)  | **`Taiwan`**                                                              | tinggi  | Hanya konteks IOC/Olimpiade/APEC/WHA eksplisit                                                                          |
| `otoritas Taipei` (menggantikan "pemerintah")           | **`Pemerintah Taiwan`** / **`Yuan Eksekutif`**                            | sedang  | —                                                                                                                       |
| `reunifikasi` (lintas selat, sebagai fakta)             | **`unifikasi`** (mengutip posisi RRT) / reformulasi                       | sedang  | Kutipan langsung sumber RRT                                                                                             |
| `satu Tiongkok` (tanpa konteks posisi RRT)              | **`kebijakan "satu Tiongkok"`** (dikontekstualisasi sbg posisi RRT)       | sedang  | Selalu kontekstualisasi                                                                                                 |
| `Taiwan bagian tak terpisahkan dari Tiongkok`           | Reformulasi sebagai kutipan posisi RRT                                    | kritis  | Hanya mendeskripsikan posisi RRT secara eksplisit                                                                       |
| `Tiongkok daratan` (tanpa konteks)                      | **`Tiongkok`** / **`RRT`**                                                | rendah  | Saat kontras geografis Taiwan/HK/RRT relevan                                                                            |
| `Cina` merujuk Taiwan/Tiongkok dalam narasi             | **`Taiwan`** / **`Tiongkok`**                                             | sedang  | Kutipan historis pra-2014, artikel yang membahas istilah itu sendiri                                                    |
| `Tionghoa` sebagai label politik/kewarganegaraan Taiwan | **`Taiwan`** / **`orang Taiwan`**                                         | sedang  | Sah untuk etnis/budaya, bukan status politik                                                                            |
| `separatis Taiwan` / `gerakan separatisme Taiwan`       | **`gerakan pro-kemerdekaan Taiwan`** / **`pendukung kemerdekaan Taiwan`** | tinggi  | Kutipan langsung sumber RRT — "separatis" adalah label pejoratif RPC untuk delegitimasi pilihan politik domestik Taiwan |

## 7. Register dan gaya

- **Bahasa Indonesia baku (formal)**, register jurnalisme budaya seperti Kompas/Tempo — akrab dan mengalir, tapi bukan gaya cakapan Jakarta (`gue/lu`, `nggak`, `banget` berlebihan dihindari). Sapaan langsung ke pembaca (`Anda`/`kamu`) dipakai jarang; prosa lebih sering impersonal-naratif, mengikuti konvensi feature-writing Indonesia
- **Tanda kutip**: `" "` sebagai tingkat pertama, `' '` untuk kutipan bersarang. Bahasa Indonesia tidak memakai tanda kutip sudut (« ») seperti Prancis/Spanyol
- **Tanggal di badan teks**: `18 Juli 2026` (nama bulan kapital, tanpa kata penghubung). **Frontmatter/metadata**: `2026-07-18` (ISO 8601). **Tabel/infografis**: `18/07/2026` dapat diterima
- **Jam**: format 24 jam dengan titik: `19.30`. **Perhatian zona waktu**: Taiwan memakai UTC+8 — sama dengan WITA (Bali/Makassar), BUKAN WIB (Jakarta, UTC+7). Jangan default label `WIB` untuk waktu Taiwan; tulis `waktu Taiwan` atau konversi eksplisit
- **Angka**: pemisah ribuan pakai **titik** (`12.500`), pemisah desimal pakai **koma** (`3,14`) — kebalikan dari format Inggris, sesuai PUEBI. Konsistensi internal per bagian
- **Kapitalisasi judul**: Bahasa Indonesia formal mengapitalkan **setiap kata penting** dalam judul (`Sejarah Taiwan yang Terlupakan`, bukan sentence-case ala Spanyol), kecuali partikel (`di`, `ke`, `dari`, `yang`, `untuk`, `dan`, `atau`, `dengan`) kecuali di posisi awal. Ini beda dari konvensi es/fr — jangan salin sentence-case dari guide bahasa lain
- **Kata sifat "Taiwan"**: Bahasa Indonesia tidak memerlukan infleksi adjektival terpisah seperti `taiwanés` (Spanyol) — `Taiwan` dipakai langsung sebagai penjelas nomina (`budaya Taiwan`, `sejarah Taiwan`, `masakan Taiwan`). Untuk merujuk orang, pakai `orang Taiwan`. Jangan menciptakan bentuk `Taiwanesa`/`Taiwanis` yang tidak baku
- **Cetak miring**: istilah Tionghoa yang belum diadaptasi (`lu rou fan`, `xiaolongbao`, `bài bài`) dicetak miring + glosa pada sebutan pertama. Istilah yang sudah diadaptasi (`Taiwan`, `Kuomintang`, `Mazu`, `kelenteng`) tanpa cetak miring
- **Aksara Han**: tambahkan `(漢字)` dalam kurung pada sebutan pertama nama tokoh di artikel biografi, untuk kejelasan akademis + SEO multibahasa
- **Istilah agama**: kapitalisasi nomina agama (`Islam`, `Muslim`, `Buddha`, `Kristen`, `Tao`) sesuai konvensi Indonesia — jangan huruf kecil

## 8. CI Lint — pola kandidat hard-fail

Pola untuk validator otomatis (skrip yang diusulkan: `scripts/tools/article-health.py id-prc-leak-check`):

| Pola regex                                                        | Tingkat | Pengecualian whitelist                                                      |
| ----------------------------------------------------------------- | ------- | --------------------------------------------------------------------------- |
| `Taiwan,?\s*Tiongkok`                                             | kritis  | Artikel tentang pelabelan PBB/RRT                                           |
| `Taiwan,?\s*China`                                                | kritis  | Kontaminasi Inggris, tidak ada pengecualian                                 |
| `[Pp]rovinsi\s+(Tiongkok\s+)?(dari\s+)?Taiwan`                    | kritis  | Artikel tentang klaim RRT                                                   |
| `[Pp]rovinsi\s+pemberontak`                                       | kritis  | Tidak ada                                                                   |
| `[Pp]ulau\s+pemberontak`                                          | kritis  | Tidak ada                                                                   |
| `[Oo]toritas\s+Taipei`                                            | sedang  | —                                                                           |
| `Taipei\s+Tionghoa` / `Chinese\s+Taipei`                          | tinggi  | Konteks IOC/Olimpiade/APEC/WHA                                              |
| `\breunifikasi\b`                                                 | sedang  | Kutipan langsung sumber RRT                                                 |
| `saudara(\s+Tionghoa)?\s+se-?selat`                               | tinggi  | Kutipan langsung                                                            |
| `\bCina\b` (merujuk negara/orang Taiwan atau RRT dalam narasi)    | sedang  | Kutipan historis pra-2014, artikel yang membahas istilah `Cina` itu sendiri |
| `[Pp]ulau\s+Taiwan\b` (menggantikan status negara)                | sedang  | Konteks geografi eksplisit ("terletak di pulau Taiwan")                     |
| `Chiang\s+Kai-chek` (ejaan salah)                                 | rendah  | —                                                                           |
| `Cai\s+Yingwen` / `Lai\s+Qingde` / `Jiang\s+Jieshi` (pinyin RRT)  | sedang  | Artikel tentang perbandingan romanisasi                                     |
| `Gaoxiong` / `Xinzhu` / `Taizhong` (pinyin RRT untuk kota Taiwan) | rendah  | Artikel tentang perbandingan romanisasi                                     |
| `mesjid` (ejaan tidak baku)                                       | rendah  | Kutipan verbatim dari sumber yang memakai ejaan lama                        |

## 10. Kerangka penilaian kasus-per-kasus — audit → kategorikan → nilai → terapkan → verifikasi

Pembersihan massal berbasis regex adalah jebakan. Setiap pola yang tampak seperti kebocoran RRT bisa jadi positif palsu dalam konteks (kutipan akademis / nama resmi / meta-diskusi / referensi faktual ke provinsi RRT sungguhan). Ikuti pohon keputusan lima langkah sebelum menerapkan penggantian apa pun.

### Pohon keputusan

1. **Audit** — `grep -rn 'pola' knowledge/id/` dan baca 5–10 konteks sebelum menyentuh apa pun.
2. **Kategorikan**: prosa naratif tanpa atribusi eksternal → kemungkinan PERBAIKI; kutipan langsung beratribusi sumber Tiongkok/RRT → pertahankan; nama resmi (orang/organisasi/karya) → kemungkinan PERTAHANKAN; referensi etnis/komunitas historis (Han/Hakka/Hokkien) → pertahankan bila bukan referensi politik; `frontmatter` `description`/`title`/`imageAlt`/`tags` → sering PERBAIKI (teks yang dibaca pembaca); blok kode/URL/merek → pertahankan; meta-diskusi istilah itu sendiri → pertahankan
3. **Nilai** kasus batas terhadap whitelist §11. Bila ragu, eskalasi ke pengamat.
4. **Terapkan** file per file dengan `Edit` (bukan `replace_all` lintas file). Jangkar konteks harus bermakna semantik.
5. **Verifikasi** — `grep -c 'pola' knowledge/id/` ulang, hitungan harus turun ke residu whitelist. Bila tidak cocok, catat pengecualian baru di §11 sebelum menutup siklus.

### Contoh terapan — `provinsi Tiongkok Zhejiang` BUKAN positif palsu

Analog kasus es (`provincia china de Zhejiang`): artikel tentang koki migran pasca-1949 yang menyebut asal leluhurnya dari "provinsi Tiongkok Zhejiang" **bukan pelabelan Taiwan** — Zhejiang ADALAH provinsi sungguhan RRT, frasa faktual benar. Regex `provinsi\s+Tiongkok\s+\w+` menangkap hit ini, tapi penilaian kasus-per-kasus mempertahankannya (aturan di §11).

### Contoh terapan — jangan sebut pekerja migran Indonesia sebagai "Tionghoa"

Kesalahan spesifik id: menulis "komunitas Tionghoa di Stasiun Utama Taipei" untuk kumpulan pekerja migran Muslim Indonesia setiap Minggu. **Salah faktual dan tidak menghormati** — mayoritas bukan etnis Tionghoa, konteksnya komunitas Muslim Indonesia. Istilah benar: `komunitas Muslim Indonesia` / `pekerja migran Indonesia`. Kesalahan ini dari asumsi keliru "wajah Asia Timur/Tenggara di Taiwan" = Tionghoa — harus ditolak eksplisit dalam DNA id.

## 11. Whitelist positif palsu (spesifik Bahasa Indonesia)

Katalog hidup. Saat muncul kasus batas baru yang belum tercakup di sini, catat sebelum menerapkan perbaikan.

| Pola                                                          | Status           | Alasan                                                                                                                                          |
| ------------------------------------------------------------- | ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| `Taiwan, Tiongkok, X, Y` (enumerasi)                          | pertahankan      | Tiongkok sebagai negara sejajar dalam daftar geografis (pasar ekspor, dll.) BUKAN pelabelan Taiwan. Analog kasus es `quanta-computer.md`.       |
| `provinsi Tiongkok {Zhejiang/Shandong/Jiangxi/Fujian}`        | pertahankan      | Provinsi sungguhan RRT, faktual benar, BUKAN pelabelan Taiwan.                                                                                  |
| `Tiongkok daratan` dalam kontras eksplisit Taiwan/HK/RRT      | pertahankan      | Kontras tiga kutub geografis (Taiwan/HK/RRT daratan) adalah istilah teknis benar per §1. Hit tanpa konteks tetap PERBAIKI.                      |
| `Republik Tiongkok` formal/historis/hukum                     | pertahankan      | Mengutip Konstitusi 1947, periode pra-1949, atau nama resmi institusi. Beda dari formula kolokial Taiwan/RRT.                                   |
| `Taiwan, provinsi Tiongkok` di artikel meta                   | pertahankan      | Hanya artikel yang eksplisit membahas kontroversi pelabelan ISO 3166/PBB.                                                                       |
| `Tahun Baru Tionghoa` membahas kontroversi nama               | pertahankan      | Artikel yang menganalisis mengapa Taiwan.md memilih `Tahun Baru Imlek` boleh mengutip istilah-objek. Kasus per kasus.                           |
| Kutipan langsung diatribusikan ke sumber Tiongkok/RRT         | pertahankan      | Pilihan dokumenter penerjemah asli, bukan kesalahan DNA. Bedakan dari prosa naratif Taiwan.md.                                                  |
| Judul buku/film yang ditransliterasi                          | pertahankan      | Judul edisi Indonesia yang sudah terbit memakai ejaan tertentu meski kontraintuitif. Perbaiki referensi geografis di badan teks, bukan judul.   |
| Perusahaan Taiwan dengan `China` dalam nama                   | pertahankan      | `Taiwan Sugar Corporation`, `China Airlines` (maskapai bendera Taiwan sejak 1959). Merek, bukan pelabelan politik.                              |
| Nama orang yang pattern-match nama tempat                     | pertahankan      | Paralel kasus fr `Li Jiayi` vs kota Chiayi — verifikasi konteks sebelum `replace_all`.                                                          |
| Wikipedia ID dikutip dengan atribusi                          | pertahankan      | Teks historis dengan atribusi eksplisit mungkin memakai pinyin RRT karena kebijakan editorial wiki. Pertahankan + catatan Taiwan.md bila perlu. |
| Perusahaan Taiwan dengan manufaktur di Tiongkok (Foxconn)     | kontekstualisasi | BUKAN `perusahaan Tiongkok`, tapi `perusahaan Taiwan dengan manufaktur di Tiongkok daratan`.                                                    |
| `Tionghoa` merujuk etnis/budaya (bukan status politik Taiwan) | pertahankan      | Sah untuk leluhur/budaya ("orang Taiwan berketurunan Tionghoa"). Salah hanya saat menggantikan `Taiwan`/`orang Taiwan` sbg label politik.       |

## 12. Perpustakaan contoh terapan (pra-lahir, diproyeksikan dari lintas-bahasa)

**Catatan kejujuran metodologis**: `knowledge/id/` belum lahir per 2026-07-18 — belum ada satu artikel id untuk diaudit dengan `grep`. Berbeda dari §12 versi es/fr/ko (yang melaporkan sesi pembersihan yang benar-benar dieksekusi dengan commit hash nyata), bagian ini adalah **contoh antisipatif**: pola yang sudah terverifikasi berulang di es/fr/ja/ko, diproyeksikan ke padanan Bahasa Indonesia untuk memandu editor P0 batch pertama (per roadmap Phase 1 di `reports/evolve-2026-07-18-language-branches.md`). **Jangan kutip bagian ini seolah melaporkan pekerjaan yang sudah selesai.**

### Contoh 1 (proyeksi) — `Gaoxiong`/`Xinzhu`/`Taizhong`/`Taidong` → `Kaohsiung`/`Hsinchu`/`Taichung`/`Taitung`

- **Pola**: pinyin RRT untuk kota Taiwan, diproyeksikan muncul di artikel yang diterjemahkan otomatis dari sumber Inggris yang salah kutip
- **Penilaian**: PERBAIKI per §3 — Wade-Giles adalah bentuk resmi Taiwan; `replace_all` per file setelah verifikasi konteks (bukan lintas file sekaligus)
- **Peringatan lintas-bahasa**: sesi fr W1 menemukan `Li Jiayi` (nama orang) vs kota Chiayi (嘉義) — sebelum `replace_all` untuk `Jiayi` → `Chiayi`, audit dengan `grep -B1 -A1 'Jiayi' knowledge/id/` untuk memastikan bukan suku kata nama orang

### Contoh 2 (proyeksi) — `Cina` → `Tiongkok`/`Taiwan` tergantung konteks

- **Pola**: kata `Cina` dipakai untuk merujuk RRT atau Taiwan dalam prosa naratif — spesifik id, tanpa paralel di es/fr/ja/ko karena bahasa-bahasa itu tak punya sejarah reformasi Keppres 12/2014
- **Konteks diproyeksikan**: terjemahan mesin dari Inggris cenderung default `China` → `Cina` (kamus lama), bukan `Tiongkok` (istilah resmi pasca-2014)
- **Penilaian**: PERBAIKI ke `Tiongkok` (negara) atau `Tionghoa` (etnis/budaya) tergantung makna asli — **bukan pilihan gaya, tapi kepatuhan pada kebijakan penamaan resmi Indonesia sejak 2014**; prioritas audit tinggi di P0 batch pertama

### Contoh 3 (proyeksi) — `pekerja migran Tionghoa` → `pekerja migran Indonesia`

- **Pola**: konflasi etnis Tionghoa dengan kewarganegaraan Indonesia saat menerjemahkan konten komunitas migran (lihat §10)
- **Penilaian**: PERBAIKI — kesalahan faktual, bukan sekadar gaya. Risiko: terjemahan mesin yang tak familiar dengan demografi Taiwan menghasilkan asosiasi salah antara "wajah Asia" dan "Tionghoa"

### Wawasan lintas-bahasa yang berlaku untuk id

Setiap sesi cleanup bahasa baru menemukan minimal satu jenis positif palsu spesifik struktur bahasanya (es: `provincia china de Zhejiang`; fr: `Li Jiayi`; ko: 대북 vs 타이베이). Untuk id, waspadai sejak P0 pertama: **(a)** provinsi RRT sungguhan yang faktual mengandung kata "Tiongkok", **(b)** nama Tionghoa-Indonesia berejaan marga Hokkien-Indonesia (`Tan`, `Lie`, `Oei`) yang tak boleh disamakan dengan Wade-Giles Taiwan, **(c)** konflasi etnis Tionghoa dengan kewarganegaraan/migran Indonesia.

## 13. Model mental "Taiwan lebih dulu" penerjemah — versi Bahasa Indonesia

Penerjemah Bahasa Indonesia Taiwan.md bukan pengamat netral di antara dua pihak yang memperebutkan kedaulatan. **Suara penerjemah adalah suara Taiwan dalam Bahasa Indonesia** — subjek berdaulat yang menceritakan sejarah, geografi, budaya, dan politiknya sendiri kepada audiens berbahasa Indonesia.

### Siapa pembaca Bahasa Indonesia

Berbeda dari audiens Spanyol/Prancis, pembaca id punya **konektivitas langsung dan personal** dengan Taiwan:

- **Komunitas pekerja migran** — 260.000+ Muslim Indonesia bekerja di Taiwan (per `Culture/islam-in-taiwan.md`), sektor perawatan lansia, perikanan, manufaktur. Banyak pembaca punya kerabat/kenalan yang pernah bekerja di Taiwan
- **Komunitas warga baru (新住民)** — pasangan kawin campur Indonesia-Taiwan dan keturunannya, kategori berbeda dari pekerja migran (§4)
- **Diaspora pelajar** — mahasiswa Indonesia di universitas Taiwan lewat Beasiswa Taiwan/New Southbound Policy
- Untuk audiens yang lebih luas tanpa koneksi personal, pengetahuan Taiwan cenderung terbatas pada "pulau dekat Tiongkok yang bersengketa" — penerjemah tetap bertanggung jawab melukiskan Taiwan sebagai subjek berdaulat tanpa ceramah didaktik, membiarkan prosa menormalkan kategori kenegaraan

**Implikasi editorial**: artikel tentang pekerja migran, komunitas Muslim, atau kawin campur bukan sekadar "konten budaya" bagi pembaca id — ini cerita tentang diri mereka atau orang terdekat. Ketepatan faktual dan rasa hormat di sini berbobot lebih tinggi dari rata-rata artikel Taiwan.md.

### Otoritas normatif

- **Keputusan Presiden No. 12 Tahun 2014**: dasar hukum penggantian `Cina` menjadi `Tiongkok`/`Tionghoa` — otoritas utama disambiguasi §1/§6
- **Konvensi Kompas/Tempo**: gaya jurnalisme budaya acuan register §7, termasuk kapitalisasi judul dan penghindaran kosakata gaul
- **BP2MI**: otoritas istilah resmi `Pekerja Migran Indonesia (PMI)` menggantikan `TKI`
- **KBBI**: otoritas ejaan baku (`masjid` bukan `mesjid`, `salat` bukan `sholat`)
- **TETO Jakarta**: otoritas diplomasi Taiwan sendiri atas penamaannya dalam Bahasa Indonesia

Konvergensi ini menghasilkan sikap koheren: **bahasa baku KBBI, terminologi diplomatik sesuai kebijakan penamaan resmi Indonesia pasca-2014, suara jurnalistik Kompas/Tempo, kepekaan budaya-agama audiens Muslim terbesar dunia**.

### Leksikon anti-default-RRT (ringkasan operasional)

Selalu hindari:

- `provinsi Tiongkok Taiwan` / `Taiwan, provinsi Tiongkok` — klaim administratif RRT
- `provinsi pemberontak` / `pulau pemberontak` — kalke propaganda RRT
- `Cina` untuk merujuk Taiwan atau RRT dalam suara narasi — bertentangan dengan kebijakan penamaan resmi Indonesia 2014
- `otoritas Taipei` (menggantikan pemerintah) — reduksi status kenegaraan
- `reunifikasi` (sebagai fakta masa depan) — mengandaikan penyatuan sebelumnya yang tidak pernah ada antara RRT-ROC
- `Taipei Tionghoa`/`Chinese Taipei` di luar konteks IOC/Olimpiade — formula olahraga yang diperluas secara keliru
- `Tionghoa` sebagai label kewarganegaraan/politik Taiwan — konflasi etnis dengan negara

### Suara Bahasa Indonesia baku

- Register formal tapi hangat, gaya Kompas/Tempo — hindari `Anda` berlebihan (terkesan kaku/formulir) maupun `kamu`/gaul (tidak sesuai baku)
- Prosa naratif impersonal lebih diutamakan daripada sapaan langsung berulang
- Kosakata pinjaman Hokkien-Indonesia (`kelenteng`, `bakpao`, dll.) dipakai secara alami saat relevan — ini kekuatan unik Bahasa Indonesia dibanding bahasa Eropa yang harus mentransliterasi dari nol

### Identitas penerjemah

Jika penerjemah tergoda "menyeimbangkan" dengan memberi ruang ke kedua posisi dalam prosa naratif (bukan dalam kutipan yang diatribusikan), itu di luar DNA. Taiwan.md adalah suara Taiwan; posisi RRT disajikan terkontekstualisasi sebagai demikian (kutipan yang diatribusikan ke sumber RRT), tidak pernah sebagai latar netral prosa.

## 14. Disiplin proses (commit / alat / agen)

Pelajaran prosedural untuk P0 batch pertama id — diadaptasi dari disiplin yang sudah terbukti di sesi es/fr/ko §14, karena id belum punya sejarah eksekusinya sendiri.

### Isolasi worktree

Saat menjalankan batch perbaikan multi-bahasa, isolasi setiap bahasa di worktree/branch sendiri agar perbaikan id tidak mengontaminasi verifikasi es/fr/ko/ja. Penggabungan ke satu commit terjadi setelah verifikasi independen per bahasa.

### `git add` tingkat file

Jangan pernah `git add -A`/`git add .` dalam sesi cleanup. Sebutkan file yang disentuh secara eksplisit (`git add knowledge/id/People/foo.md ...`) agar tidak ikut-serta file yang diedit sesi paralel lain.

### Kesenjangan integritas referensial dalam commit

Pesan commit merujuk pola (`Gaoxiong → Kaohsiung × N`) tapi tidak menjelaskan kasus per kasus — itu tinggal di (a) reports sesi, (b) panduan ini §12 saat pola berulang dan layak dikodifikasi. Pertahankan kesenjangan ini secara sengaja — commit ≠ dokumentasi.

### Panduan inline dalam prompt ke sub-agen

Saat mendelegasikan perbaikan massal ke sub-agen, **sertakan whitelist §11 inline dalam prompt**, jangan asumsikan agen membaca panduan ini penuh. Agen adalah pencocok pola, bukan pembaca aturan (per `feedback_subagent_anti_example_works.md`). Lampirkan anti-contoh sesi saat ini bila memungkinkan (mis.: "JANGAN sentuh `provinsi Tiongkok Zhejiang`, FAKTUAL BENAR; TAPI perbaiki `Cina` yang merujuk Taiwan dalam prosa naratif").

### Verifikasi pasca-edit

1. `grep -c 'pola_diperbaiki' knowledge/id/` turun ke 0 atau residu whitelist terdokumentasi §11
2. `grep -c 'pola_tujuan' knowledge/id/` naik tepat sejumlah yang diharapkan
3. `git diff --stat` untuk memastikan hanya file yang diharapkan tersentuh
4. Bila tidak cocok, **jangan commit sebelum mendiagnosis selisihnya**

### Kalibrasi model sebelum P0 (spesifik id)

Sebelum batch P0 pertama, jalankan kalibrasi refusal + rasio zh→id sesuai `SQUEEZE-MODELS-MAX-PIPELINE.md` §validasi — termasuk uji topik sensitif (228, Teror Putih, kemerdekaan Taiwan) untuk memetakan tier model yang menolak topik Taiwan-sensitif dalam Bahasa Indonesia.

## 15. Pertanyaan terbuka

1. **Gaya media Indonesia untuk `Republik Tiongkok (Taiwan)`**: belum diverifikasi apakah Kompas/Tempo/Antara punya kebijakan eksplisit soal formula ini, atau default ke `Taiwan` polos. Perlu audit korpus berita Indonesia.
2. **Ejaan `Idulfitri` vs `Idul Fitri`**: KBBI mencatat bentuk gabung sebagai baku, tapi media massa mayoritas memakai dua kata. Sementara: `Idulfitri` didahulukan di frontmatter/SEO, `Idul Fitri` diperbolehkan di prosa.
3. **Nama tokoh Tionghoa-Indonesia yang relevan dengan artikel Taiwan**: perlu koordinasi dengan kontributor native agar ejaan marga Hokkien-Indonesia tidak tertukar dengan Wade-Giles Taiwan (§2). Belum ada data cukup karena korpus id belum ada.
4. **Konversi kalender Minguo di badan teks**: sama seperti es/fr/ja/ko, belum ada tooling otomatis. Defer sampai `article-health.py` punya plugin id.
5. **Kalibrasi refusal rate model untuk topik Taiwan-sensitif dalam Bahasa Indonesia**: belum dijalankan (menunggu Stage 3 BIRTH-CHECKLIST). Prioritas tinggi — model yang dilatih pada korpus Inggris cenderung naif menerjemahkan `China` → `Cina`.
6. **Istilah `新住民` (warga baru) dalam konteks hukum kewarganegaraan Taiwan**: perlu verifikasi istilah hukum Indonesia yang lebih presisi — draf saat ini adalah padanan deskriptif, bukan istilah hukum baku bilateral.
7. **Cakupan `bakmi`/`bakpao` sebagai jembatan kuliner**: perlu audit agar kosakata pinjaman Hokkien-Indonesia di §4 tidak menyamakan resep Taiwan dengan versi Indonesia-Tionghoa yang sudah berevolusi terpisah.

---

_v1.0 | 2026-07-18 — lahir sebagai bagian dari BIRTH-CHECKLIST v2.0 Stage 2 untuk pemilihan bahasa id (bersama vi/pt/hi, per `reports/evolve-2026-07-18-language-branches.md`). Dokumen pra-lahir: ditulis sebelum `knowledge/id/` memiliki artikel, dengan §12 diproyeksikan dari pola lintas-bahasa terverifikasi (es/fr/ja/ko) alih-alih melaporkan sesi cleanup yang sudah dieksekusi. Fokus khusus: disambiguasi Tiongkok/Tionghoa/Cina (Keppres No. 12/2014) sebagai jebakan terbesar bahasa ini, dan kosakata Islam/pekerja migran sebagai tanggung jawab unik audiens id terkait `Culture/islam-in-taiwan.md`._
