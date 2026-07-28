---
title: 'TRANSLATION-pt'
description: 'Normas de tradução para português (pt-BR de base) — Taiwan/Taipé + Wade-Giles + léxico anti-RPC + registro'
type: 'editorial-canonical'
status: 'canonical'
current_version: 'v1.0'
last_updated: 2026-07-18
last_session: '2026-07-18-pt-language-birth-prep'
sister_docs:
  - 'TRANSLATION-en.md'
  - 'TRANSLATION-es.md'
  - 'TRANSLATION-ja.md'
  - 'TRANSLATION-ko.md'
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

# TRANSLATION-pt — Normas de tradução para português de Taiwan.md

> Este documento nasce em pré-lançamento: `knowledge/pt/` ainda não existe (ver [reports/evolve-2026-07-18-language-branches.md](../../../reports/evolve-2026-07-18-language-branches.md) — pt foi selecionado como único candidato "três fontes confirmadas": SC 6.659 impressões / CTR 0,1% no mercado brasileiro, CF entre os 6 maiores pedidos de borda sem nenhum conteúdo pt existente, GA 88 usuários orgânicos). É o guia canônico acionável a carregar antes de cada tradução zh → pt, escrito **antes** do primeiro artigo real ser traduzido — por isso §11-§12 são antecipatórias, calibradas com pesquisa de mercado pt real (imprensa brasileira, imprensa portuguesa, mídia estatal chinesa em português), não com corpus pt já existente. **Este guia herda a estrutura e boa parte do conteúdo do [guia espanhol (TRANSLATION-es.md)](TRANSLATION-es.md)** — línguas-irmãs latinas, mesma romanização Wade-Giles, problema de soberania estruturalmente idêntico. Onde o conteúdo é herdado sem alteração, isso está marcado explicitamente; onde português e espanhol divergem (grafia, gramática, falsos amigos, perfil do leitor), a diferença está destacada em caixas de atenção. **Registro: português brasileiro (pt-BR) como base**, evitando coloquialismo regional excessivo para manter legibilidade em todo o mundo lusófono.

## TL;DR — 5 regras de prioridade máxima

1. **`Taiwan` sem acento** (⚠️ diferente do espanhol `Taiwán` — falso amigo nº 1 entre as duas línguas) e **`Taipé` com acento, sem "i" final** (⚠️ diferente do espanhol `Taipéi`) no corpo do texto, frontmatter, legendas e descrições SEO. `Taipé` é a forma consolidada da Wikipédia em português e do próprio escritório oficial brasileiro de Taiwan. A grafia sem acento `Taipei` só é aceita dentro de nomes próprios institucionais (`Taipei 101`, `Taipei Economic and Cultural Office`, `Taipei Times`) e em URLs/slugs ASCII.
2. **Wade-Giles para topônimos e antropônimos taiwaneses, nunca pinyin da RPC.** `Kaohsiung` (não `Gaoxiong`), `Hsinchu` (não `Xinzhu`), `Tsai Ing-wen` (não `Cai Yingwen`), `Chiang Kai-shek` (não `Jiang Jieshi`). Manter o hífen entre as duas sílabas do nome próprio (`Ing-wen`, `Ching-te`).
3. **Ordem chinesa sobrenome + nome**: `Tsai Ing-wen`, nunca `Ing-wen Tsai`. Segunda menção: **sobrenome só** (`Tsai`), nunca o nome próprio sozinho. Para pessoas com nome ocidental (`Audrey Tang`, `Joseph Wu`, `Morris Chang`, `Jensen Huang`), usar a forma com que se apresentam publicamente.
4. **`você` como tratamento padrão pt-BR** (⚠️ diferente do espanhol, onde `tú` é o tuteo panhispânico neutro — em português brasileiro `tu` é regional/marcado, não neutro). Nunca `vós` arcaico; `o(a) senhor(a)` reservado a citações e protocolo. A voz de Taiwan.md é divulgativa e próxima: «você sabia que em Taiwan…?».
5. **Léxico anti-RPC**: usar `Taiwan` como entidade política singular. Proibido `Taiwan, China`, `província chinesa de Taiwan`, `ilha rebelde` / `província rebelde`, `compatriotas taiwaneses`, `reunificação` (quando descreve integração futura como fato consumado). Forma institucional longa: **`República da China (Taiwan)`** — nunca `República da China` sozinha (confunde com RPC).

## 1. Designação de país / região

| Origem (zh-TW)  | Português recomendado                                                                       | Quando usar                                                                  | Nunca usar                                                                                 | Notas                                                                                   |
| --------------- | ------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------- |
| 台灣            | **Taiwan** (sem acento)                                                                     | Por padrão, em todo contexto                                                 | `Taiwán` (grafia espanhola, falso amigo), `Formosa` (contemporâneo), `província de Taiwan` | Wikipédia pt confirma título sem acento                                                 |
| 中華民國        | **República da China (Taiwan)**                                                             | Instituições formais, Constituição, direito internacional, citações oficiais | `República da China` sozinha (confunde com RPC)                                            | Herdado do guia espanhol (mesma lógica, sem equivalente diplomático lusófono — ver §13) |
| 中華台北        | **Taipé Chinesa**                                                                           | Só contexto COI/Jogos Olímpicos/APEC/OMS                                     | Como sinônimo casual de Taiwan                                                             | Verbete próprio na Wikipédia pt (`Taipé Chinesa`); regime esportivo específico          |
| 兩岸 / 海峽兩岸 | **os dois lados do estreito** / **relações entre os dois lados do estreito**                | Relações políticas RPC-ROC                                                   | `compatriotas dos dois lados do estreito` (RPC)                                            | Sem pressupor fraternidade                                                              |
| 中國大陸        | **China continental** (só quando há contraste geográfico relevante) / **China** / **a RPC** | Contexto histórico ou contraste geográfico explícito                         | Como sinônimo neutro de `China` (assume o enquadramento "uma só China")                    | Descontextualizado, evitar                                                              |
| 中國            | **China** / **a República Popular da China (RPC)**                                          | Referência ao Estado RPC                                                     | —                                                                                          | Diferenciar da ROC sempre                                                               |
| 我國            | **Taiwan** / **nosso país** (se a voz é de um taiwanês citado)                              | Reformular conforme o contexto                                               | Tradução literal sem recontextualizar                                                      | Dependente de contexto                                                                  |
| 台灣海峽        | **estreito de Taiwan** (minúscula em _estreito_)                                            | Geografia                                                                    | `Estreito de Taiwan` (maiúscula incorreta)                                                 | Norma jornalística padrão                                                               |

**Princípio "país"**: usar `país` sem hesitação ao descrever Taiwan — nunca `território`, `entidade` ou `ilha` como substituto evasivo da categoria estatal. Isso não é ativismo lexical; é o mesmo princípio que rege o autocuramento de Taiwan.md em chinês (MANIFESTO §自稱: 「大方自稱『台灣』『這個國家』，不用『這座島』當迴避稱呼」— "escrever 'Taiwan', 'este país' sem rodeios, não usar 'esta ilha' como forma evasiva"). O critério é uma pergunta só: **isto é evasão de escrever Taiwan, ou a ilha em si carrega sentido aqui?** Evasão troca-se; sentido genuíno permanece — por isso o uso literário de `ilha` (paisagem, geografia, metáfora) continua livre.

**Proibições explícitas**: `Taiwan, China`; `ilha chinesa de Taiwan`; `Taipé Chinesa` fora do contexto olímpico; `província rebelde`.

**Nota sobre `Formosa`**: diferente do espanhol, `Formosa` não é um empréstimo distante para o português — é uma palavra **de origem portuguesa**. Em 1544, uma frota portuguesa cruzou o estreito de Taiwan a caminho do Japão e batizou a ilha de `Ilha Formosa` ("ilha bela"); o nome permaneceu em uso corrente na literatura europeia até o século XX. Uso literário/histórico glosado é bem-vindo e tem uma ressonância especial em português que nenhuma outra língua-alvo de Taiwan.md compartilha. **Mas não é substituto político**: usar `Formosa` para evitar dizer `Taiwan` num contexto de status político é a mesma evasão vetada acima, só que com verniz poético.

## 2. Antropônimos — Wade-Giles + ordem sobrenome-nome

**Regras** (herdadas do guia espanhol sem alteração de conteúdo — Wade-Giles é romanização internacional, não varia por língua-alvo):

- Ordem **sobrenome + nome** (chinês), sem inverter ao estilo ocidental
- Segunda menção: **sobrenome só** (`Tsai`), nunca o nome próprio sozinho
- **Hífen** entre as duas sílabas do nome próprio: `Ing-wen`, `Ching-te`, `Kai-shek`. Nunca `Ing Wen` (separado), nunca `Ingwen` (junto sem hífen)
- **Sem acentos** ortográficos em nomes romanizados (`Tsai Ing-wen` ✓, não `Tsái Íng-wén`)
- Em artigos biográficos, acrescentar caracteres entre parênteses na primeira menção: `Audrey Tang (唐鳳)`
- **Nomes indígenas**: transliterar a partir da grafia latina oficial taiwanesa (`Kolas Yotaka`), não a partir do mandarim

**Lista canônica das figuras mais referenciadas**:

| 漢字            | Taiwan.md (pt)                | Pinyin RPC (NÃO) |
| --------------- | ----------------------------- | ---------------- |
| 蔡英文          | **Tsai Ing-wen**              | Cai Yingwen      |
| 賴清德          | **Lai Ching-te**              | Lai Qingde       |
| 馬英九          | **Ma Ying-jeou**              | Ma Yingjiu       |
| 陳水扁          | **Chen Shui-bian**            | Chen Shuibian    |
| 李登輝          | **Lee Teng-hui**              | Li Denghui       |
| 蔣介石 / 蔣中正 | **Chiang Kai-shek**           | Jiang Jieshi     |
| 蔣經國          | **Chiang Ching-kuo**          | Jiang Jingguo    |
| 唐鳳            | **Audrey Tang**               | Tang Feng        |
| 吳釗燮          | **Joseph Wu**                 | Wu Zhaoxie       |
| 蕭美琴          | **Hsiao Bi-khim**             | Xiao Meiqin      |
| 張忠謀          | **Morris Chang**              | Zhang Zhongmou   |
| 黃仁勳          | **Jensen Huang**              | Huang Renxun     |
| 李安            | **Ang Lee**                   | Li An            |
| 侯孝賢          | **Hou Hsiao-hsien**           | Hou Xiaoxian     |
| 楊德昌          | **Edward Yang**               | Yang Dechang     |
| 林懷民          | **Lin Hwai-min**              | Lin Huaimin      |
| 鄧麗君          | **Teresa Teng**               | Deng Lijun       |
| 張惠妹          | **A-mei** / **Chang Hui-mei** | Zhang Huimei     |
| 阿信 (五月天)   | **Ashin (Mayday)**            | A Xin            |
| 張懸 / 安溥     | **Deserts Chang** / **Anpu**  | Zhang Xuan       |

> ⚠️ **Atenção falso amigo**: em textos de imprensa em português já é possível encontrar `Lai Ching-te` e `Tsai Ing-wen` escritos exatamente como acima (CNN Brasil, PÚBLICO) — a forma internacional já circula no ecossistema pt. O risco de vazamento pinyin é menor aqui do que a tentação de "aportuguesar" incorretamente sílabas do nome (ex.: escrever `Ingüen` ou separar o hífen).

### ⚠️ Regra crítica: não substitua um nome desconhecido por um famoso

**Ao encontrar um nome taiwanês que não está na tabela acima — translitere-o.
Não coloque no lugar o nome de uma figura conhecida.**

Caso real (2026-07-25, primeiro lote em árabe; o risco é idêntico em português):
a fonte em chinês diz «o ex-diretor da Agência de Saúde **Hsu Tzu-chiu** (許子秋)
ouviu a filha…», e a tradução saiu «um alto funcionário da saúde, **era Chiang
Ching-kuo**» — o diretor de uma agência virou presidente da República. Não é
confusão entre duas figuras conhecidas (a armadilha documentada em §12), é
**preenchimento de lacuna**: o modelo não conhece o nome e coloca o nome político
taiwanês mais frequente nos seus dados de treino.

Prevenir sai mais barato: **nome desconhecido translitera-se, com o original em
caracteres chineses entre parênteses**, por exemplo «Hsu Tzu-chiu (許子秋)».

## 3. Topônimos

### Regra Taipé vs Taipei (decisão explícita)

| Contexto                                                         | Forma                          | Exemplo                                                                                       |
| ---------------------------------------------------------------- | ------------------------------ | --------------------------------------------------------------------------------------------- |
| Prosa corrida, título, legenda, `description`/SEO no frontmatter | **Taipé**                      | «Taipé é a capital de Taiwan.»                                                                |
| Nome próprio institucional (a instituição se autodenomina assim) | **Taipei**                     | `Taipei 101`, `Taipei Economic and Cultural Office`, `Taipei Times`, `Taipei American School` |
| Contexto olímpico/COI/APEC/OMS                                   | **Taipé Chinesa**              | «competiu sob a bandeira de Taipé Chinesa nos Jogos de 2024»                                  |
| URLs, slugs, tags técnicas                                       | **Taipei** (ASCII, sem acento) | `/pt/geography/taipei-districts`                                                              |

`Taipé` é a forma consolidada: é o título do verbete da Wikipédia em português (`pt.wikipedia.org/wiki/Taipé`) e a grafia usada pelo próprio `Escritório Econômico e Cultural de Taipei no Brasil` — que, por sua vez, mantém `Taipei` sem acento **no seu próprio nome institucional**, confirmando o padrão da tabela acima na fonte mais autorizada disponível (a representação diplomática de facto de Taiwan no Brasil).

### Cidades (Wade-Giles oficial taiwanês, nunca pinyin da RPC)

| 漢字        | Taiwan.md (pt)                               | Pinyin (NÃO)    |
| ----------- | -------------------------------------------- | --------------- |
| 臺北 / 台北 | **Taipé** (texto) / `Taipei` (institucional) | Taibei          |
| 高雄        | **Kaohsiung**                                | Gaoxiong        |
| 臺中 / 台中 | **Taichung**                                 | Taizhong        |
| 臺南 / 台南 | **Tainan**                                   | Tainan          |
| 新竹        | **Hsinchu**                                  | Xinzhu          |
| 基隆        | **Keelung**                                  | Jilong          |
| 桃園        | **Taoyuan**                                  | Taoyuan         |
| 花蓮        | **Hualien**                                  | Hualian         |
| 宜蘭        | **Yilan**                                    | Yilan           |
| 台東        | **Taitung**                                  | Taidong         |
| 屏東        | **Pingtung**                                 | Pingdong        |
| 嘉義        | **Chiayi**                                   | Jiayi           |
| 苗栗        | **Miaoli**                                   | Miaoli          |
| 彰化        | **Changhua**                                 | Zhanghua        |
| 雲林        | **Yunlin**                                   | Yunlin          |
| 南投        | **Nantou**                                   | Nantou          |
| 新北市      | **Novo Taipé** (cidade de)                   | New Taipei City |

**Distritos e bairros**: construção `distrito de Xinyi` (com `de`), seguindo o padrão português `bairro de Ipanema` / `distrito da Sé`. Para bairros de sabor cotidiano-cultural, admissível `bairro de Ximending`.

### Ilhas externas (atenção à desambiguação 馬祖 ilhas vs 媽祖 deusa)

| 漢字 | Taiwan.md (pt)                    | Notas                                                                    |
| ---- | --------------------------------- | ------------------------------------------------------------------------ |
| 金門 | **Kinmen**                        | `Quemoy` admissível em contexto de Guerra Fria («crise de Quemoy, 1958») |
| 馬祖 | **Matsu** (ilhas, Wade-Giles)     | **Crítico**: distinguir de 媽祖 `Mazu` (deusa, pinyin)                   |
| 澎湖 | **Penghu** / **ilhas Pescadores** | Ambas as formas viáveis                                                  |
| 綠島 | **Ilha Verde** / `Lüdao`          |                                                                          |
| 蘭嶼 | **Ilha das Orquídeas** / `Lanyu`  |                                                                          |

### Montanhas e rios

- 玉山 → **`monte Yushan`** + glosa na primeira menção: «(literalmente, _Monte de Jade_)». Não usar `Monte Jade` como termo primário.
- 阿里山 → **`Alishan`** ou **`monte Alishan`**
- 日月潭 → **`lago do Sol e da Lua`** (tradução semântica consolidada)
- 太魯閣 → **`Taroko`** ou **`garganta de Taroko`**
- 中央山脈 → **`cordilheira Central`**
- 淡水河 → **`rio Tamsui`**

## 4. Léxico cultural

### Gastronomia (política: transliteração + glosa na primeira menção para pratos icônicos; calco direto quando é transparente)

| 漢字     | Taiwan.md (pt)                                                                   | Notas                                                                                                                                                                                                                                                                                        |
| -------- | -------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 滷肉飯   | **`lurou fan`** (arroz com carne de porco refogada)                              | Manter transliteração                                                                                                                                                                                                                                                                        |
| 牛肉麵   | **`niurou mian`** (macarrão com carne bovina) / **`sopa de macarrão com carne`** | Ambas viáveis                                                                                                                                                                                                                                                                                |
| 珍珠奶茶 | **`bubble tea`**                                                                 | Anglicismo consolidado no mercado brasileiro (redes de bubble tea usam o nome inglês); `chá de bolhas` como glosa descritiva                                                                                                                                                                 |
| 鳳梨酥   | **`bolo de abacaxi`** (taiwanês)                                                 | pt-PT: `bolo de ananás`                                                                                                                                                                                                                                                                      |
| 小籠包   | **`xiaolongbao`** (bolinho no vapor recheado com caldo)                          | Pinyin internacional, mantido em todas as línguas-alvo                                                                                                                                                                                                                                       |
| 臭豆腐   | **`tofu fedorento`**                                                             | Calco literal consolidado                                                                                                                                                                                                                                                                    |
| 蚵仔煎   | **`omelete de ostras`**                                                          | Calco direto                                                                                                                                                                                                                                                                                 |
| 雞排     | **`escalope de frango frito`**                                                   | ⚠️ Baixa confiança — evitar `milanesa` (Cone Sul hispânico); ver §15                                                                                                                                                                                                                         |
| 刈包     | **`gua bao`** / **`sanduíche taiwanês`**                                         | Anglicismo internacional                                                                                                                                                                                                                                                                     |
| 夜市     | **`mercado noturno`**                                                            | **Decisão firmada**: `mercado noturno` é o termo primário (paralelo direto ao `mercado nocturno` espanhol e ao uso da Administração de Turismo de Taiwan em outras línguas). `feira noturna` é variante aceitável, mais frequente em registro coloquial de Portugal — não usar como primário |
| 小吃     | **`xiaochi`** (petiscos / lanches típicos)                                       | Glosa na primeira menção                                                                                                                                                                                                                                                                     |

### Religião e mitologia

- 媽祖 → **`Mazu`** (deusa, pinyin). A UNESCO a registra como `o culto a Mazu e seus rituais`. Distinguir sempre de 馬祖 `Matsu` (ilhas).
- 觀音 → **`Guanyin`** (bodhisattva da compaixão)
- 廟 → **`templo`** (genérico); `templo taoista` / `templo budista` conforme o caso
- 拜拜 → **`bài bài`** + glosa «rito de veneração popular»

### Festividades

| 漢字             | Taiwan.md (pt)                                                      |
| ---------------- | ------------------------------------------------------------------- |
| 春節 / 過年      | **`Ano Novo Lunar`** (preferido a `Ano Novo Chinês`)                |
| 中秋節           | **`Festival do Meio do Outono`**                                    |
| 端午節           | **`Festival do Barco-Dragão`**                                      |
| 元宵節           | **`Festival das Lanternas`**                                        |
| 清明節           | **`Festival de Qingming`** / **`Dia da Limpeza dos Túmulos`**       |
| 七夕             | **`Qixi`** / **`Dia dos Namorados chinês`**                         |
| 中元節           | **`Festival dos Fantasmas`** / **`Festival Zhongyuan`**             |
| 雙十節           | **`Dia Dez de Outubro`** / **`Dia Nacional da República da China`** |
| 二二八和平紀念日 | **`Dia Memorial da Paz de 28 de Fevereiro`** / **`Dia da Paz 228`** |

### Línguas (cuidado homonímico: `taiwanês` é ao mesmo tempo gentílico e nome de língua)

| 漢字          | Taiwan.md (pt)                                                                                      |
| ------------- | --------------------------------------------------------------------------------------------------- |
| 國語 / 華語   | **`mandarim`** / **`mandarim taiwanês`** (quando se distingue do da RPC)                            |
| 台語 / 台灣話 | **`taiwanês`** (língua) / **`hokkien taiwanês`** (especializado, evita ambiguidade com o gentílico) |
| 閩南語        | **`min nan`** / **`min do sul`**                                                                    |
| 客家話        | **`hakka`**                                                                                         |
| 原住民語      | **`línguas indígenas`** / **`línguas formosanas`** / **`línguas austronésias de Taiwan`**           |

### Transporte / urbano

- 高鐵 → **`trem de alta velocidade de Taiwan`** (THSR / HSR)
- 捷運 → **`metrô`** (de Taipé, de Kaohsiung) — ⚠️ falso amigo: pt-BR `metrô` (circunflexo) vs pt-PT `metro` (sem acento, igual ao es). Baseline pt-BR → `metrô`
- 老街 → **`rua velha`** / `lao jie`

## 5. Termos políticos / históricos sensíveis

| 漢字       | Taiwan.md (pt)                                                                                      | Notas                                                                                                                                        |
| ---------- | --------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| 二二八事件 | **`Incidente de 28 de Fevereiro`** / **`Incidente 228`** / **`Massacre 228`** (ênfase na repressão) | Consolidado — título do verbete pt.wikipedia é `Incidente de 28 de fevereiro`; `Massacre 228` usado por imprensa brasileira (Gazeta do Povo) |
| 白色恐怖   | **`Terror Branco`** (maiúsculas, como período histórico nomeado 1949-1987)                          | Confirmado: título do verbete `Terror Branco (Taiwan)` na Wikipédia pt                                                                       |
| 戒嚴       | **`lei marcial`** (minúsculas); `período de lei marcial (1949-1987)`                                | 38 anos e 57 dias                                                                                                                            |
| 解嚴       | **`fim da lei marcial`** / **`levantamento da lei marcial`**                                        |                                                                                                                                              |
| 民國紀年   | **Converter silenciosamente para o calendário gregoriano** no corpo                                 | Manter dupla notação só em citações, direito, artigos sobre o calendário                                                                     |
| 本省人     | **`benshengren`** + glosa «locais, descendentes de migrantes anteriores a 1945»                     | Pinyin com glosa na primeira menção                                                                                                          |
| 外省人     | **`waishengren`** + glosa «continentais, migrantes chegados com o KMT entre 1945 e 1949»            | Estrutura-chave da história política pós-1945                                                                                                |
| 日治時期   | **`período colonial japonês`** / **`período de dominação japonesa`** (1895-1945)                    | Evitar `ocupação japonesa` (anacrônico)                                                                                                      |
| 民主化     | **`democratização`**                                                                                |                                                                                                                                              |
| 原住民     | **`povos indígenas`** / **`indígenas taiwaneses`** (preferido); `aborígenes taiwaneses` aceitável   | Evitar `gaoshan` (高山族, codificado pela RPC)                                                                                               |
| 國民黨     | **`Kuomintang`** / **`KMT`** / **`Partido Nacionalista Chinês`**                                    | Wade-Giles consolidado na imprensa lusófona                                                                                                  |
| 民進黨     | **`Partido Democrático Progressista`** / **`PDP`**                                                  | ⚠️ falso amigo: `progressista` (dois esses, pt) vs `progresista` (um só, es)                                                                 |
| 台灣民眾黨 | **`Partido Popular de Taiwan`** / **`PPT`**                                                         | Melhor que o anglicismo `TPP`                                                                                                                |
| 時代力量   | **`Força do Novo Tempo`** / **`New Power Party`**                                                   | ⚠️ Baixa confiança — ver §15                                                                                                                 |
| 行政院     | **`Yuan Executivo`** / **`Executivo Yuan`**                                                         |                                                                                                                                              |
| 立法院     | **`Yuan Legislativo`** / **`Legislativo Yuan`**                                                     |                                                                                                                                              |
| 司法院     | **`Yuan Judicial`**                                                                                 |                                                                                                                                              |
| 總統府     | **`Palácio Presidencial`** / **`Presidência`**                                                      |                                                                                                                                              |
| 外交部     | **`Ministério das Relações Exteriores`** (MOFA)                                                     | pt-PT: `Ministério dos Negócios Estrangeiros`. Não confundir com o nome coloquial do Itamaraty, que é exclusivo do Brasil                    |
| 國軍       | **`Forças Armadas de Taiwan`** / **`Exército da ROC`**                                              |                                                                                                                                              |

## 6. Léxico contra vazamento RPC-codificado

| RPC-codificado                                                                      | Substituição Taiwan.md                                                                                                                           | Gravidade | Exceção                                                                                                                   |
| ----------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ | --------- | ------------------------------------------------------------------------------------------------------------------------- |
| `Taiwan, China`                                                                     | **`Taiwan`**                                                                                                                                     | crítica   | Só artigo sobre a rotulagem em si                                                                                         |
| `Taiwan, província da China`                                                        | **`Taiwan`**                                                                                                                                     | crítica   | Só artigo sobre a rotulagem                                                                                               |
| `província chinesa de Taiwan` / `província de Taiwan`                               | **`Taiwan`** / **`República da China (Taiwan)`**                                                                                                 | crítica   | —                                                                                                                         |
| `a ilha rebelde` / `província rebelde`                                              | **`Taiwan`**                                                                                                                                     | crítica   | Nunca — confirmado ainda circulando em imprensa brasileira mainstream (`considera uma província rebelde`, em.com.br 2026) |
| `ilha reivindicada pela China` / `país reclamado pela China` como frase de abertura | Apresentar Taiwan primeiro pelo que é (país autogovernado, democracia, semicondutores); só depois mencionar a reivindicação de Pequim, atribuída | alta      | Nunca como definição neutra de abertura                                                                                   |
| `compatriotas taiwaneses` / `compatriotas de Taiwan` (台胞)                         | **`cidadãos taiwaneses`** / **`os taiwaneses`**                                                                                                  | alta      | Citação textual — CGTN Português usa ativamente esta expressão                                                            |
| `Taipé Chinesa` / `Taipé chinesa` fora do contexto olímpico                         | **`Taiwan`**                                                                                                                                     | alta      | Só contexto COI/Olimpíadas/APEC/OMS explícito                                                                             |
| `autoridades de Taipei` (em vez de governo)                                         | **`Governo de Taiwan`** / **`Yuan Executivo`** / **`presidência taiwanesa`**                                                                     | média     | —                                                                                                                         |
| `reunificação` (cross-strait, como fato)                                            | **`unificação`** (se citando postura da RPC) / reformular                                                                                        | média     | Citação textual de fonte RPC — CGTN/CRI em português usam ativamente; até imprensa mainstream reproduz sem marcação       |
| `retorno de Taiwan à China` / `regresso à pátria`                                   | Reformular como enquadramento de Pequim, sempre atribuído                                                                                        | média     | Citação — confirmado em manchete de imprensa portuguesa relatando fala de Xi sem contraponto                              |
| `compatriotas dos dois lados do estreito`                                           | **`dos dois lados do estreito`**                                                                                                                 | alta      | Citação                                                                                                                   |
| `a ilha` (pejorativo, substituindo Taiwan como Estado)                              | **`Taiwan`**                                                                                                                                     | média     | Contexto geográfico explícito                                                                                             |
| `Taiwan é parte da China` / `parte inseparável da China`                            | Reformular como postura da RPC contextualizada                                                                                                   | crítica   | Só descrevendo a postura da RPC                                                                                           |
| `política de uma só China` (como fato, sem marcação)                                | **`política de uma só China`** (sempre apresentada como postura da RPC, nunca como fato)                                                         | média     | Contextualizar sempre — confirmado usado como manchete de abertura sem atribuição em imprensa brasileira                  |
| `questão de Taiwan` (台灣問題, enquadramento de "problema interno chinês")          | **`situação de Taiwan`** / **`relação entre Taiwan e a China`**                                                                                  | média     | Citação de fonte RPC (CGTN usa `Taiwan question`)                                                                         |
| `China continental` (sem contexto)                                                  | **`China`** / **`a RPC`**                                                                                                                        | baixa     | Quando o contraste geográfico é relevante                                                                                 |

## 7. Registro e estilo

- **`você` como tratamento padrão pt-BR.** ⚠️ Diferença estrutural do espanhol: lá `tú` é o tuteo panhispânico neutro (`vosotros` descartado por excluir a América Latina, voseo rioplatense descartado por quebrar a neutralidade). Em português brasileiro **não existe esse mesmo eixo** — `tu` é regional (comum no Sul do Brasil e em Portugal, mas soa marcado/deslocado fora desses contextos quando conjugado à moda europeia), e `você` já é a forma neutra e universal no pt-BR contemporâneo, conjugada com verbo de 3ª pessoa. `o(a) senhor(a)` reservado a citações e protocolo, equivalente ao `usted` espanhol
- **Aspas duplas `" "`** como padrão de primeiro nível na imprensa brasileira (Folha, Estadão) — diferente do espanhol, que prioriza `« »`. Aspas angulares `« »` aparecem mais em tipografia formal portuguesa (Portugal) mas são raras mesmo lá na imprensa online contemporânea. Segundo nível: `' '`
- **Datas no corpo**: `24 de maio de 2026` (mês em minúscula). **Metadata/frontmatter**: `2026-05-24` (ISO 8601). **Tabelas/infográficos**: `24/05/2026` aceitável
- **Horas**: formato pt-BR `19h30` (h minúsculo embutido, sem dois-pontos) — ⚠️ diferente do espanhol `19:30 h`. Narrativa: `às sete e meia da noite`. Evitar `7:30 PM`
- **Números**: separador de milhar ponto (`12.500`); separador decimal vírgula (`3,14`) — igual ao espanhol nesse ponto
- **Maiúsculas em títulos**: só a primeira palavra e nomes próprios (`História de Taiwan`, não `História De Taiwan`). Aplica-se também a `## seções`
- **Itálico**: termos chineses não adaptados (`lurou fan`, `xiaochi`, `bài bài`) em itálico + glosa na primeira menção. Termos adaptados (`Taiwan`, `Taipé`, `Kuomintang`, `Mazu`) sem itálico
- **Caracteres chineses**: acrescentar `(漢字)` entre parênteses na primeira menção de nomes próprios biográficos, para clareza acadêmica + SEO multilíngue
- **Adjetivo**: `taiwanês` / `taiwanesa` (plural `taiwaneses` / `taiwanesas`) preferido a `de Taiwan` (perífrase). Evitar `formosano` (anacrônico) e `chinês de Taiwan` (codificado pela RPC)
- **Variante pt-BR vs pt-PT**: quando existir bifurcação lexical relevante (`ônibus`/`autocarro`, `trem`/`comboio`, `celular`/`telemóvel`, `metrô`/`metro`, `abacaxi`/`ananás`), priorizar a forma brasileira — baseline desta guia é pt-BR por decisão de sitiamento (§evidências acima) — com nota pt-PT quando o termo for central ao artigo (transporte, tecnologia)

### Tom: aproximação ao caderno de cultura brasileiro

O registro-alvo é o do caderno de cultura da grande imprensa brasileira (Ilustríssima/Folha, Aliás/Estadão): **divulgativo mas culto**, frases curtas, sem jargão acadêmico, sem sensacionalismo, cita fontes primárias, deixa a informação falar por si em vez de adjetivar em excesso. Evitar o cacoete de manchete ("bombástico", "chocante", "verdadeiro"); evitar também o tom professoral que trata o leitor como aluno. Para o leitor de Portugal (Público, Expresso), o mesmo registro funciona sem adaptação — a diferença está no léxico técnico (§ variantes acima), não no tom.

### Falsos amigos es↔pt de maior risco (resumo operativo)

| Espanhol            | Português         | Risco                                                                 |
| ------------------- | ----------------- | --------------------------------------------------------------------- |
| `Taiwán`            | `Taiwan`          | Acento sobra em português — maior risco de vazamento cross-lang       |
| `Taipéi`            | `Taipé`           | Português não leva o `i` final                                        |
| `tú` (tuteo neutro) | `você` (não `tu`) | Eixo de formalidade estruturalmente diferente, não é 1:1              |
| `progresista`       | `progressista`    | Duplo `ss` em português                                               |
| `metro`             | `metrô` (pt-BR)   | Circunflexo no Brasil; `metro` só em Portugal                         |
| `« »` como padrão   | `" "` como padrão | Tipografia jornalística diverge                                       |
| `mercado nocturno`  | `mercado noturno` | Sem `c` mudo — português já reformou essa grafia (Acordo Ortográfico) |

## 8. CI Lint — frases candidatas a hard-fail

Padrões para validador automático (script proposto: `scripts/tools/article-health.py pt-prc-leak-check`):

| Padrão regex                                                                     | Gravidade | Exceção na lista branca                                                |
| -------------------------------------------------------------------------------- | --------- | ---------------------------------------------------------------------- |
| `Taiwan,?\s*China`                                                               | crítica   | Artigo sobre a rotulagem ONU/RPC                                       |
| `provínc[ia]+\s+(chinesa\s+)?de\s+Taiwan`                                        | crítica   | Artigo sobre a reivindicação da RPC                                    |
| `provínc[ia]+\s+rebelde`                                                         | crítica   | Nenhuma                                                                |
| `(a\s+)?ilha\s+rebelde`                                                          | crítica   | Nenhuma                                                                |
| `compatriotas\s+taiwaneses`                                                      | alta      | Citação textual                                                        |
| `Taip[eé]\s+[Cc]hinesa`                                                          | alta      | Contexto COI/Olimpíadas/APEC/OMS                                       |
| `autoridades\s+de\s+Taipei`                                                      | média     | —                                                                      |
| `\breunificação\b`                                                               | média     | Citação textual de fonte RPC                                           |
| `Chiang\s+Kai-check` (grafia errônea)                                            | baixa     | —                                                                      |
| `Cai\s+Yingwen` / `Lai\s+Qingde` / `Jiang\s+Jieshi` (pinyin RPC para taiwaneses) | média     | Artigo sobre romanizações                                              |
| `Taiwán\b` (grafia espanhola vazando para pt)                                    | alta      | Nenhuma — vazamento cross-lang, não vazamento RPC, mas hard-fail igual |
| `Taipéi\b` (grafia espanhola vazando para pt)                                    | alta      | Nenhuma                                                                |
| `Gaoxiong` / `Xinzhu` / `Taizhong` (pinyin RPC para cidades taiwanesas)          | baixa     | Artigo sobre romanizações                                              |

## 10. Marco de julgamento caso a caso — auditar → categorizar → julgar → aplicar → verificar

O cleanup em massa por regex é armadilha. Cada padrão aparente de vazamento RPC pode ser falso positivo em contexto (citação acadêmica / nome próprio / meta-discussão / referência factual a uma província real da RPC). O tradutor deve seguir uma árvore de decisão de cinco passos antes de aplicar qualquer substituição — herdada sem alteração do guia espanhol, porque o problema estrutural (regex é cego a contexto) não muda entre línguas latinas.

### Árvore de decisão

1. **Auditar** — `grep -rn 'padrão' knowledge/pt/` e ler 5-10 contextos amostrais antes de tocar em qualquer coisa. Ancorar a unicidade do resultado com contexto suficiente para que `Edit` não falhe por duplicidade.
2. **Categorizar** cada acerto:
   - Prosa narrativa, fora de aspas, sem atribuição externa? → provavelmente CORRIGIR
   - Dentro de `" "` / `« »` como citação direta com atribuição a fonte chinesa ou RPC? → preservar (a responsabilidade é da fonte citada; o tradutor não edita citações)
   - Nome próprio (pessoa, organização, título de obra, festival com nome oficial RPC)? → provavelmente PRESERVAR
   - Referência a grupo étnico / comunidade histórica (han, hakka, hoklo)? → preservar quando distinto de referência política
   - Em `frontmatter` `description` / `title` / `imageAlt` / `tags`? → revisar visibilidade para o leitor final, frequentemente CORRIGIR (é texto que o leitor vê mesmo fora do corpo Markdown)
   - Bloco de código, URL, nome de marca, identificador técnico? → preservar
   - Meta-discussão do próprio termo (artigo que analisa a rotulagem ISO 3166 / a fórmula "Chinese Taipei" / como a RPC nomeia Taiwan)? → preservar
3. **Julgar** os casos-limite contra a lista branca codificada em §11. Se a dúvida persistir, escalar ao observador antes de aplicar.
4. **Aplicar** arquivo por arquivo com `Edit` (não `replace_all` global entre múltiplos arquivos). O contexto que ancora a unicidade deve ser semanticamente significativo, não apenas sintaticamente único.
5. **Verificar** — reexecutar `grep -c 'padrão' knowledge/pt/` e confirmar que a contagem baixou ao resíduo esperado (soma dos acertos na lista branca). Se a contagem residual não bater, alguma exceção não estava documentada — registrar em §11 antes de fechar.

### Nota de honestidade

Como `knowledge/pt/` ainda não existe, os exemplos abaixo (§11-§12) **não são casos reais de limpeza de corpus** — são padrões antecipados a partir de pesquisa de mercado pt real (Wikipédia em português, imprensa brasileira e portuguesa, mídia estatal chinesa em português) e de lições cross-lang das sessões es/fr já concluídas. Servem para pré-calibrar o julgamento do primeiro tradutor pt; devem ser substituídos por exemplos reais assim que o primeiro lote de artigos pt for traduzido (ver §15).

---

## 11. Lista branca de falsos positivos (específica do português)

Catálogo vivo, pré-populado por pesquisa (não por corpus real — ver nota acima). Quando aparecer um novo caso-limite não contemplado aqui, registrar antes de aplicar a correção.

| Padrão                                                                      | Status    | Razão                                                                                                                                                                                                              |
| --------------------------------------------------------------------------- | --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `Taiwan, China, X, Y` (enumeração)                                          | preservar | Quando China figura como país par numa enumeração geográfica (lista de mercados de exportação, países onde uma empresa opera etc.), NÃO é rotulagem de Taiwan. Herdado do padrão es §11 `taiwan-foreign-trade.md`. |
| `província chinesa de {Shandong/Zhejiang/Jiangxi/Fujian}`                   | preservar | Províncias reais da RPC, sintagma factualmente correto. NÃO é rotulagem de Taiwan. Mesmo raciocínio do guia espanhol §11 (`braised-pork-rice.md`, `puli-shaoxing-wine.md`).                                        |
| `China continental` em contraste explícito Taiwan/Hong Kong/RPC             | preservar | Quando o texto contrasta Taiwan e Hong Kong com a RPC continental como três polos geográficos distintos, `China continental` é o termo técnico correto (per §1).                                                   |
| `China continental` contrastando P&D vs manufatura                          | preservar | Em artigos sobre cadeias de fornecimento (Wistron/Pegatron/Foxconn), `P&D em Taiwan + manufatura na China continental` é contraste industrial técnico, não rotulagem.                                              |
| `República da China` formal/histórica/legal                                 | preservar | Quando se cita a Constituição de 1947, o período pré-1949, ou instituições cujo nome oficial usa a forma curta. Distinto da fórmula coloquial Taiwan/RPC.                                                          |
| `Taiwan, província da China` em artigos meta                                | preservar | Só em artigos que discutem explicitamente a controvérsia ISO 3166 / rotulagem da ONU. Marcar com citação ou contexto explícito.                                                                                    |
| `Ano Novo Chinês` discutindo a controvérsia do nome                         | preservar | Quando o artigo analisa por que Taiwan.md prefere `Ano Novo Lunar`, citar `Ano Novo Chinês` como termo-objeto.                                                                                                     |
| `中国台湾网` (taiwan.cn) como citação de fonte RPC                          | preservar | Se o nome do site RPC aparecer em nota de rodapé citando a fonte, preservar verbatim com atribuição — é referência bibliográfica, não endosso.                                                                     |
| Citações diretas atribuídas a fonte chinesa (CGTN, CRI, Xinhua Português)   | preservar | Se a fonte primária usa `reunificação`, `compatriotas de Taiwan` etc. dentro de uma citação atribuída, preservar — é escolha documental do original, não erro de DNA do tradutor.                                  |
| Empresas taiwanesas com `China` no nome                                     | preservar | `China Airlines` (bandeira taiwanesa desde 1959), `Taiwan Cement Corporation`. Preservar marca; não é rotulagem política.                                                                                          |
| Nomes próprios chineses que colidem com topônimo                            | preservar | Ex.: nome de pessoa cuja romanização coincida com `Jiayi` (嘉義, cidade) sem ser a cidade. Lição cross-lang: fr W1 teve este falso positivo com `Li Jiayi`; auditar com `grep -B1 -A1` antes de `replace_all`.     |
| Texto citado de mídia estatal chinesa em português com atribuição explícita | preservar | CGTN/CRI/Xinhua Português usam `reunificação`, `compatriotas de Taiwan`, `regresso à pátria` como vocabulário editorial próprio — preservar como citação de fonte, nunca como voz narrativa de Taiwan.md           |
| `Taipé Chinesa` em artigo sobre a própria fórmula olímpica                  | preservar | Meta-discussão do rótulo esportivo — mesmo padrão de `Taipéi chino` no guia espanhol.                                                                                                                              |

---

## 12. Biblioteca de exemplos antecipados (pré-lançamento, calibrados por pesquisa real pt)

Diferente das irmãs es/fr — que documentam sessões de limpeza reais sobre corpus já traduzido —, esta seção documenta **padrões observados em pesquisa de mercado pt** que muito provavelmente aparecerão assim que o primeiro lote `knowledge/pt/` for traduzido pela cascata babel. Cada exemplo cita a fonte real da pesquisa.

### Exemplo 1 — `ilha reclamada/reivindicada pela China` como frase de abertura

- **Padrão observado**: reportagem brasileira mainstream (não mídia estatal chinesa) abre a definição de Taiwan assim: «Taiwan, também conhecido por Formosa ou República da China, é um país independente do Extremo Oriente e reclamado pela China como parte integrante de seu território» — e segue: «considera uma província rebelde e defende sua reunificação» (Estado de Minas, trends, 2026).
- **Julgamento**: se a mesma estrutura aparecer num rascunho de tradução babel (o modelo tradutor pode reproduzir o enquadramento de uma fonte usada como referência), é FIX obrigatório — a definição de abertura de Taiwan.md nunca começa pela reivindicação de Pequim. Reformular para: Taiwan primeiro como o que é, RPC depois como postura atribuída.
- **Ação esperada**: reordenar a frase; `província rebelde` e `reunificação` sem atribuição saem sempre.

### Exemplo 2 — `reunificação` na voz narrativa vs `reunificação` em citação

- **Padrão observado**: CGTN Português e CRI Português (mídia estatal chinesa) usam `reunificação` como vocabulário editorial ativo e recorrente («O futuro de Taiwan reside na reunificação completa da pátria»).
- **Julgamento**: se um artigo Taiwan.md citar uma declaração oficial de Pequim como fonte primária (ex.: discurso de porta-voz do Gabinete de Assuntos de Taiwan), `reunificação` dentro da citação atribuída PRESERVA-SE — é a escolha lexical da fonte, e camuflá-la reduz a precisão histórica. Fora de citação, na voz narrativa de Taiwan.md, sempre FIX.
- **Ação esperada**: verificar sempre se o termo está dentro de aspas com atribuição explícita antes de decidir.

### Exemplo 3 — `regresso/retorno de Taiwan à China`

- **Padrão observado**: um veículo português mainstream noticiou, sem contraponto textual imediato, «regresso de Taiwan à China é motivo de conversa entre Xi e Trump» — reproduzindo o enquadramento de Pequim no próprio título da notícia.
- **Julgamento**: risco alto de vazamento silencioso quando um artigo Taiwan.md narra eventos diplomáticos recentes usando fontes noticiosas de terceiros como referência de tradução. FIX sempre que a formulação aparecer fora de citação atribuída a Pequim.
- **Ação esperada**: reformular como «a alegação de Pequim de que Taiwan deve integrar a China» ou equivalente, sempre atribuída.

### Exemplo 4 — `Taipé` vs `Taipei` em texto histórico Qing/japonês

- **Padrão (lição cross-lang, es §12 exemplo 8)**: es teve arquivos com `Taibei` (pinyin) sobrevivendo em referências históricas Qing e modernas. Mesmo risco em pt — `Taipei` sem acento pode vazar de fontes em inglês, mesmo em contexto histórico (`Taipei Prefecture` da era Qing).
- **Ação esperada**: aplicar a regra da tabela §3 uniformemente, independente do período histórico do parágrafo — `Taipei` só dentro de nome institucional, `Taipé` em toda prosa.

### Exemplo 5 — `mercado noturno` vs `bubble tea`: dois pesos conscientes

- **Padrão**: pesquisa confirma `mercado noturno` como termo institucional consolidado nas línguas latinas irmãs; já `珍珠奶茶` tende a manter o anglicismo `bubble tea` no mercado brasileiro por força comercial (redes usam o nome inglês em cardápio).
- **Julgamento**: nem todo termo cultural taiwanês segue "traduzir sempre que possível" — quando o mercado de chegada já consolidou um anglicismo por uso comercial extensivo, forçar a tradução soa artificial. Decisão caso a caso, não regra geral.

### Insight cross-lang aplicável ao pt

Antes de qualquer `replace_all` entre arquivos para `Gaoxiong` → `Kaohsiung`, `Xinzhu` → `Hsinchu` etc. (o mesmo cleanup que es e fr já fizeram), replicar o protocolo de auditoria de es §12 exemplo 6: `grep` primeiro, verificar se a ocorrência não é parte de um nome próprio de pessoa cuja romanização colide com o topônimo (lição do falso positivo `Li Jiayi` em fr W1).

---

## 13. Modelo mental «Taiwan primeiro» do tradutor — versão portuguesa

O tradutor de português de Taiwan.md não é um observador neutro entre duas partes que disputam soberania. **A voz do tradutor é a voz de Taiwan em português** — um sujeito soberano descrevendo sua própria história, geografia, cultura, política, a uma audiência lusófona.

### Quem é o leitor lusófono

Aqui o perfil diverge do espanhol de um jeito estrutural, não apenas de detalhe: **nenhum país lusófono atual mantém relações diplomáticas formais com a ROC.** São Tomé e Príncipe manteve laços com Taiwan entre 1997 e 2016, sendo o precedente lusófono mais próximo — mas rompeu e reconheceu a RPC em dezembro de 2016. Angola, Moçambique, Cabo Verde, Guiné-Bissau, Timor-Leste e Guiné Equatorial reconhecem todos a RPC; Portugal reconhece a RPC desde 1979 e mantém a fórmula "uma só China" na sua política externa. Isso significa:

- **Não existe, no mundo lusófono, o equivalente ao Paraguai/Guatemala do guia espanhol** — não há embaixada da ROC ativa em nenhum país de língua portuguesa para ancorar a fórmula institucional `República da China (Taiwan)` em uso diplomático oficial local. A autoridade normativa mais próxima é o próprio `Escritório Econômico e Cultural de Taipei no Brasil` — a representação de facto de Taiwan em território lusófono.
- **Em compensação, existe uma ligação histórica que nenhuma outra língua-alvo de Taiwan.md tem**: `Formosa` é uma palavra portuguesa, cunhada por navegadores portugueses em 1544 (ver §1). O leitor lusófono não herda o nome de uma fonte estrangeira — herda-o da própria história marítima da sua língua.
- Para o restante do mundo lusófono (Brasil, Portugal, PALOP), o leitor médio sabe que Taiwan é «uma ilha perto da China com disputa territorial» — ponto, semelhante ao perfil do leitor hispânico do guia espanhol. O tradutor tem a responsabilidade de **pintar Taiwan como sujeito soberano** sem lições didáticas desnecessárias, deixando que a própria prosa normalize a categoria estatal.

### Autoridades normativas

- **Wikipédia em português**: autoridade de fato para grafia consolidada (`Taipé`, `Terror Branco (Taiwan)`, `Incidente de 28 de fevereiro`) — usada aqui como proxy de uso lexical real por falta de um equivalente lusófono à RAE/FundéuRAE especificamente dedicado a Taiwan.
- **`Escritório Econômico e Cultural de Taipei no Brasil`**: autoridade da própria diplomacia taiwanesa sobre sua autodenominação em português — inclusive sobre a convivência `Taipé` (prosa) / `Taipei` (nome institucional) documentada em §3.
- **Imprensa brasileira e portuguesa mainstream** (Folha, Estadão, CNN Brasil, Público, DN): autoridade de registro e de romanização de nomes próprios em uso corrente.
- **Mídia estatal chinesa em português** (CGTN Português, CRI Português): não é autoridade normativa — é a fonte primária do vocabulário a evitar em §6, útil precisamente para identificar o vazamento antes que ele aconteça.

A convergência produz uma postura coerente: **grafia consolidada via Wikipédia pt, terminologia institucional via a própria representação taiwanesa, registro via imprensa lusófona mainstream, vigilância lexical via a fonte do problema (mídia estatal chinesa em português)**.

### Léxico anti-RPC-padrão (resumo operativo)

Evitar sempre:

- `província chinesa de Taiwan` / `Taiwan, província da China` — reivindicação administrativa da RPC
- `ilha rebelde` / `província rebelde` — calco de propaganda da RPC, ainda circulando até em imprensa brasileira mainstream sem marcação de atribuição
- `compatriotas taiwaneses` / `compatriotas de Taiwan` (台胞) — apelação familiar da RPC, vocabulário ativo do CGTN Português
- `autoridades de Taipei` (em vez de governo) — redução da categoria estatal
- `reunificação` (como fato futuro) — pressupõe uma união anterior que nunca existiu entre RPC e ROC
- `regresso/retorno à pátria` — a mesma pressuposição, em roupagem mais poética, ativa em CRI Português
- `Taipé Chinesa` fora do contexto COI/Olimpíadas — fórmula esportiva extrapolada indevidamente

### Identidade do tradutor

Se o tradutor sentir a tentação de «equilibrar» dando voz às duas posições na prosa narrativa (fora de citações atribuídas), está fora do DNA. Taiwan.md é a voz de Taiwan; as posições da RPC apresentam-se contextualizadas como tais (citação atribuída a fonte RPC), nunca como pano de fundo neutro da prosa.

## 14. Disciplina de processo (commit / ferramentas / agentes)

Lições procedimentais herdadas sem alteração do guia espanhol — a disciplina de execução não muda entre línguas, só o conteúdo linguístico muda.

### Isolamento de worktree

Num lote de correções multi-idioma (W1 a W4 cross-language numa mesma corrida babel), isolar cada língua na sua própria worktree/branch evita que uma correção em pt contamine a verificação de es/fr/ko/ja. O agrupamento final num commit conjunto ocorre só depois da verificação independente de cada língua.

### `git add` no nível de arquivo

Nunca `git add -A` nem `git add .` em sessões de limpeza. Listar explicitamente os arquivos tocados (`git add knowledge/pt/People/foo.md knowledge/pt/Geography/bar.md ...`) para evitar incluir arquivos editados por engano ou por outra sessão paralela.

### Gap de integridade referencial no conteúdo do commit

A mensagem de commit referencia padrões (`Gaoxiong → Kaohsiung × 2` etc.) mas não explica caso a caso — essa explicação vive nos relatórios da sessão sob `reports/` e neste guia §12 quando o padrão é recorrente. Gap intencional — commit ≠ documentação.

### Orientação inline em prompts para sub-agentes

Ao delegar uma correção em massa a um sub-agente, **incluir inline a lista branca de §11 no prompt**, não assumir que o agente vai ler este guia inteiro. Agentes são reconhecedores de padrões, não leitores de regras (per `feedback_subagent_anti_example_works.md`). Quando possível, anexar um contraexemplo da sessão atual (ex.: «NÃO toque em `província chinesa de Zhejiang`, factualmente correto; TOQUE em `compatriotas taiwaneses` em prosa narrativa»).

### Verificação pós-edição

Ao fechar o ciclo:

1. `grep -c 'padrão_corrigido' knowledge/pt/` deveria baixar a 0 ou ao resíduo documentado na lista branca de §11
2. `grep -c 'padrão_destino' knowledge/pt/` deveria subir na quantidade exatamente esperada
3. Visualizar o diff (`git diff --stat`) para confirmar que só os arquivos esperados foram tocados
4. Se a verificação não bater, **não fazer commit até diagnosticar a diferença** — falsos positivos não documentados são sinal de que a lista branca precisa de ampliação

---

## 15. Questões em aberto

1. **`knowledge/pt/` ainda não existe**: este guia foi calibrado por pesquisa de mercado (Wikipédia pt, imprensa brasileira/portuguesa, mídia estatal chinesa em português), não por corpus real. §11-§12 devem ser revisados com casos reais assim que o primeiro lote babel pt for traduzido — provavelmente revelará falsos positivos não previstos, como aconteceu com `Li Jiayi` em fr W1.
2. **`雞排` (`escalope de frango frito`)**: baixa confiança em §4. Não há termo consolidado em português para este prato de rua; `milanesa` foi descartado por soar mais argentino/uruguaio do que brasileiro. Confirmar quando o primeiro artigo de gastronomia pt for traduzido.
3. **`時代力量` (`Força do Novo Tempo`)**: tradução literal de baixa confiança. Não há uso consolidado em imprensa lusófona — a maioria mantém `New Power Party` em inglês. Decidir forma primária quando o primeiro artigo sobre partidos taiwaneses for traduzido.
4. **Estilo de agência de notícias lusófona** (Agência Brasil / Agência Lusa): não confirmado se há política editorial explícita sobre `República da China (Taiwan)` — equivalente ao capítulo Ásia Oriental da EFE citado no guia espanhol. Consulta manual recomendada.
5. **`Chinese Taipei` em contexto esportivo do COI**: política ainda não fixada, mesma questão aberta no guia espanhol §15. Literal `Taipé Chinesa`, glosar como «equipe olímpica de Taiwan», ou `Taiwan` com nota de rodapé?
6. **Conversão automatizada do calendário ROC**: ainda não há script; regra atual é conversão silenciosa para o gregoriano — problema idêntico ao do guia espanhol §15, sem solução ali também.
7. **Nomes próprios austronésios indígenas em português**: literatura lusófona especializada praticamente inexistente. Por ora, transliterar da grafia latina oficial taiwanesa, não do mandarim — mesma política do guia espanhol.
8. **Calibração pt-BR vs pt-PT após os primeiros dados de tráfego**: esta guia assume pt-BR pela evidência de sitiamento (Brasil é a origem do sinal de demanda). Se o tráfego revelar fatia relevante de Portugal/PALOP, os itens «⚠️ diferença pt-BR/pt-PT» (`metrô`/`metro`, `ônibus`/`autocarro`, tratamento formal) merecem reavaliação como segunda camada de localização.
9. **Aspas `« »` vs `" "`**: fixado como `" "` primário por observação da imprensa brasileira online, sem fonte normativa equivalente ao Acordo Ortográfico para tipografia de aspas.

---

_v1.0 | 2026-07-18 — nascimento do guia pt. Herdado da estrutura e de boa parte do conteúdo de [TRANSLATION-es.md](TRANSLATION-es.md) v2.0 (línguas-irmãs latinas, mesma romanização Wade-Giles, mesmo problema estrutural de soberania), com diferenças destacadas explicitamente em cada seção (grafia `Taiwan`/`Taipé` sem acento espanhol, eixo `você`/`tu` diferente do tuteo panhispânico, ausência de aliado diplomático lusófono equivalente a Paraguai/Guatemala, ligação histórica única com a origem portuguesa do nome `Formosa`). Motivo de nascimento: pré-requisito para o nascimento da língua pt (BIRTH-CHECKLIST v2.0 Stage 2), selecionada em [reports/evolve-2026-07-18-language-branches.md](../../../reports/evolve-2026-07-18-language-branches.md) como único candidato "três fontes confirmadas" entre vi/id/pt/hi (SC 6.659 impressões / CTR 0,1% + CF pedidos de borda #6 + GA 88 usuários). `knowledge/pt/` ainda não existe nesta data — §10-§12 são antecipatórios._
