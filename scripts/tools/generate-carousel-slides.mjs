#!/usr/bin/env node
/**
 * generate-carousel-slides.mjs — COMPUTEX.md IG carousel slide 生成器
 *
 * 把一份 slide script (JSON) 渲染成 N 張 1080×1350 (4:5) PNG。
 * 模 scripts/core/generate-og-images.mjs v4：inline HTML template + Playwright
 * single-page setContent → per-slide page.evaluate(__renderSlide) → screenshot。
 * 無需 dev server。Google Fonts Noto Serif/Sans TC CDN。
 *
 * 品牌識別（v0.4，2026-06-03 哲宇 directive「主題色效果不好，先不要用」）：
 * COMPUTEX.md 主色 #1a3c34 + 單一 accent #00d4aa（識別色）。
 * 不再用分類色當次要 accent — 統一識別色，profile feed 一致度更高。
 *
 * Usage:
 *   node scripts/tools/generate-carousel-slides.mjs --script docs/factory/CAROUSEL-BLUEPRINTS/颱風.json
 *   node scripts/tools/generate-carousel-slides.mjs --script <path> --out public/carousel-images
 *
 * Script JSON schema:
 *   {
 *     "slug": "颱風",
 *     "category": "nature",
 *     // accent2 已 deprecated（v0.4）— 全 accent 統一用 #00d4aa 識別色
 *     "url": "computex.md/nature/颱風",
 *     "heroImage": "public/article-images/nature/morakot-modis-satellite-2009.jpg",
 *     "slides": [
 *       { "type": "cover",  "kicker": "氣候與災害", "title": "能預測風雨，\n預測不了命運", "subtitle": "台灣與颱風的四百年", "hero": true },
 *       { "type": "stat",   "value": "172→57", "unit": "公里", "label": "25 年來，颱風 24 小時路徑預報誤差壓掉三分之二" },
 *       { "type": "chart-stat", "title": "一週的代謝", "stats": [{ "value": "310", "label": "次 commit" }, { "value": "28", "label": "個 PR" }] },
 *       { "type": "chart-bars", "title": "誰在讀台灣的故事？", "bars": [{ "label": "西方 AI", "value": 83, "display": "83%" }, { "label": "對岸", "value": 16, "display": "16%", "note": "成功回應率較低" }], "source_note": "Cloudflare 7d" },
 *       // v0.6 圖表母片（← graph.md tw-* port，spec 見 SPORE-IG-PIPELINE §3.9-3.10）：
 *       { "type": "versus", "title": "台灣 vs 香港", "left": "台灣國宅", "right": "香港居屋", "rows": [{ "l": "住滿即可全價轉售", "r": "轉售須補地價" }] },
 *       { "type": "chart-timeline", "title": "政策軸", "nodes": [{ "year": "1975", "label": "國宅條例上路", "desc": "設買家資格閉環" }] },
 *       { "type": "chart-waffle", "title": "誰拿到", "cells": [{ "label": "軍方", "pct": 48 }, { "label": "民眾", "pct": 37 }], "source_note": "配售結構" },
 *       { "type": "chart-line", "title": "房價所得比", "x": ["2014","2024"], "series": [{ "name": "全國", "points": [8.41, 10.76] }], "source_note": "政大" },
 *       { "type": "chart-heatmap", "title": "房價×房貸", "corner": "地區", "cols": ["房價所得比","房貸負擔率%"], "rows": [{ "label": "台北", "values": [16.6, 64] }] },
 *       { "type": "point",  "kw": "飛進颱風眼", "body": "追風計畫的飛機真的衝進颱風中心，投下探空儀。" },
 *       { "type": "quote",  "text": "再精準的預報，都接不住那一秒。", "by": "" },
 *       { "type": "source", "sources": ["中央社","國家太空中心","原視"], "cta": "收藏這篇・分享給需要的人・追蹤 COMPUTEX.md" }
 *     ]
 *   }
 */

import { chromium } from 'playwright';
import { mkdirSync, existsSync, readFileSync } from 'node:fs';
import { join, dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawn } from 'node:child_process';
import { platform } from 'node:os';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const repoRoot = resolve(__dirname, '..', '..');

// ── args ─────────────────────────────────────────────────────────────────────
function getArg(name, def = undefined) {
  const i = process.argv.indexOf(name);
  return i !== -1 && process.argv[i + 1] ? process.argv[i + 1] : def;
}
const scriptPath = getArg('--script');
const outRoot = getArg('--out', join(repoRoot, 'public', 'carousel-images'));
if (!scriptPath) {
  console.error('❌ 需要 --script <path-to-slide-script.json>');
  process.exit(1);
}

// ── brand tokens (COMPUTEX.md 識別) ────────────────────────────────────────────
const BRAND = {
  ground: '#1a3c34', // 主底色 (識別)
  groundDeep: '#0f2a24',
  dark: '#03080a', // source 頁深色
  darkGrad: '#0a1612',
  accent: '#00d4aa', // 識別 accent
  accentSoft: '#4fd1b0',
  text: '#f4f0ea', // 主文字
  textDim: 'rgba(244,240,234,0.62)',
};
const VIEWPORT = { width: 1080, height: 1350 };

// ── load slide script + assets ───────────────────────────────────────────────
const script = JSON.parse(readFileSync(resolve(repoRoot, scriptPath), 'utf-8'));
// v0.4: 拿掉 accent2，全 deck 統一用 BRAND.accent 識別色（哲宇 directive）

function toDataUri(absPath) {
  const buf = readFileSync(absPath);
  const ext = absPath.split('.').pop().toLowerCase();
  const mime =
    ext === 'png'
      ? 'image/png'
      : ext === 'svg'
        ? 'image/svg+xml'
        : 'image/jpeg';
  return `data:${mime};base64,${buf.toString('base64')}`;
}

const faviconUri = toDataUri(join(repoRoot, 'public', 'favicon.png'));
const heroUri = script.heroImage
  ? toDataUri(resolve(repoRoot, script.heroImage))
  : '';

// ── inline HTML template ─────────────────────────────────────────────────────
function buildTemplateHtml() {
  return `<!doctype html>
<html lang="zh-TW">
<head>
<meta charset="utf-8">
<title>COMPUTEX.md carousel</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700;900&family=Noto+Serif+TC:wght@400;600;700;900&display=swap" rel="stylesheet">
<style>
:root{
  --ground:${BRAND.ground}; --ground-deep:${BRAND.groundDeep};
  --dark:${BRAND.dark}; --dark-grad:${BRAND.darkGrad};
  --accent:${BRAND.accent}; --accent-soft:${BRAND.accentSoft};
  --text:${BRAND.text}; --text-dim:${BRAND.textDim};
}
*{margin:0;padding:0;box-sizing:border-box;}
html,body{width:1080px;height:1350px;overflow:hidden;-webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility;}
body{
  background:linear-gradient(160deg,var(--ground) 0%,var(--ground-deep) 100%);
  color:var(--text);
  font-family:'Noto Sans TC',system-ui,sans-serif;
}
.frame{position:relative;width:1080px;height:1350px;padding:96px 88px 110px;display:flex;flex-direction:column;justify-content:center;}

/* top progress bar */
.progress{position:absolute;top:0;left:0;height:8px;background:var(--accent);}

/* brand row (absolute top — out of content flow so frame justify-content controls content) */
.brandrow{position:absolute;top:90px;left:88px;right:88px;display:flex;justify-content:space-between;align-items:center;}
.wordmark{display:inline-flex;align-items:center;gap:.5rem;font-weight:700;font-size:2.04rem;letter-spacing:.01em;}
.wordmark img{width:2.28rem;height:2.28rem;}
.wordmark .dot{color:var(--accent);}
.pageno{font-size:1.8rem;color:var(--text-dim);font-variant-numeric:tabular-nums;font-weight:500;}

/* kicker */
.kicker{display:inline-block;align-self:flex-start;background:var(--accent);color:#fff;font-weight:700;
  font-size:1.8rem;padding:.35em 1em;border-radius:999px;margin-bottom:2rem;letter-spacing:.04em;}

/* big serif title */
.title{font-family:'Noto Serif TC',serif;font-weight:900;line-height:1.18;letter-spacing:.01em;white-space:pre-line;}
.subtitle{font-family:'Noto Serif TC',serif;font-weight:400;color:var(--text-dim);margin-top:1.4rem;line-height:1.5;}
.subtitle em{color:var(--accent);font-style:normal;font-weight:700;}  /* v0.8: 副標 reversal 關鍵詞高亮 */

/* cover hero */
.frame[data-type="cover"]{justify-content:flex-end;padding-bottom:128px;}
.frame.hero::before{content:"";position:absolute;inset:0;background-image:var(--hero);background-size:cover;background-position:center;z-index:-2;}
.frame.hero::after{content:"";position:absolute;inset:0;
  background:linear-gradient(180deg,rgba(15,42,36,.45) 0%,rgba(15,42,36,.72) 55%,rgba(8,22,18,.95) 100%);z-index:-1;}
.frame[data-type="cover"] .title{font-size:6.48rem;text-shadow:0 4px 24px rgba(0,0,0,.55);}
.frame[data-type="cover"] .subtitle{font-size:2.52rem;text-shadow:0 2px 12px rgba(0,0,0,.5);}
.frame[data-type="cover"] .wordmark{text-shadow:0 2px 10px rgba(0,0,0,.55);}
.frame[data-type="cover"] .kicker{box-shadow:0 4px 18px rgba(0,0,0,.4);}
.coverdate{font-family:'Noto Sans TC';font-weight:700;font-size:1.92rem;color:var(--accent);letter-spacing:.08em;margin-top:1.4rem;}
.frame[data-type="cover"] .coverdate{text-shadow:0 2px 10px rgba(0,0,0,.5);}
.swipe{margin-top:2.2rem;display:inline-flex;align-items:center;gap:.6rem;color:var(--accent);font-weight:700;font-size:2.04rem;}
.swipe .arrow{font-size:2.4rem;}

/* section — v0.3: 字級 1.2x、寬度用滿 */
.frame[data-type="section"]{justify-content:center;}
.idx{font-family:'Noto Serif TC',serif;font-weight:900;font-size:3.12rem;color:var(--accent);opacity:.9;margin-bottom:1rem;letter-spacing:.05em;}
.kw{font-family:'Noto Serif TC',serif;font-weight:900;font-size:4.56rem;line-height:1.25;color:var(--text);margin-bottom:1.5rem;white-space:pre-line;}
.kw em{color:var(--accent);font-style:normal;}
.body{font-size:2.14rem;line-height:1.78;color:rgba(244,240,234,.92);white-space:pre-line;}
/* code excerpt chip — v0.7: section 可選節錄一小段（系統名 / 指標 / 短輸出），code-block 風 */
.codeblock{font-family:'SFMono-Regular','Menlo','Consolas',monospace;font-size:1.72rem;line-height:1.7;color:rgba(244,240,234,.8);background:rgba(3,8,10,.5);border-left:5px solid var(--accent);border-radius:8px;padding:1.2rem 1.5rem;margin-top:1.9rem;white-space:pre-wrap;}
/* v0.8: code-block 語法高亮（受控 terminal 配色，哲宇 callout）*/
.codeblock .t-id{color:#5fd3bb;}                 /* 指令 / 識別字 — soft teal */
.codeblock .t-num{color:#e3b984;}                /* 數字 / 版本 — soft amber */
.codeblock .t-op{color:#5f827a;}                 /* operator / tree — dim */
.codeblock .t-cjk{color:rgba(244,240,234,.82);}  /* CJK 標籤 — base */
/* section 可選支援圖（截圖 / 紀實照）— v0.7：text 主角、圖輔助，跟 figure（圖主角）區隔 */
.secimg{width:100%;aspect-ratio:16/9;background-size:cover;background-position:top center;border-radius:10px;box-shadow:0 8px 26px rgba(0,0,0,.42);margin:1.3rem 0 .8rem;}
.seccap{font-size:1.68rem;line-height:1.5;color:rgba(244,240,234,.7);font-style:italic;margin-bottom:1rem;}
.frame[data-type="section"].secmedia{justify-content:flex-start;padding-top:158px;}

/* figure — v0.3: 字級 1.2x */
.frame[data-type="figure"]{justify-content:flex-start;padding-top:160px;padding-bottom:130px;}
.figpull{display:inline-block;align-self:flex-start;background:var(--accent);color:#fff;font-weight:700;font-size:1.8rem;padding:.35em 1em;border-radius:999px;margin-bottom:1.2rem;letter-spacing:.04em;}
.figimg{width:100%;aspect-ratio:5/3;background-size:cover;background-position:center;border-radius:12px;box-shadow:0 12px 36px rgba(0,0,0,.45);margin-bottom:1.2rem;}
.figcap{font-size:1.8rem;line-height:1.55;color:rgba(244,240,234,.78);font-style:italic;margin-bottom:.7rem;}
.figbody{font-family:'Noto Serif TC',serif;font-weight:700;font-size:2.14rem;line-height:1.7;color:var(--text);white-space:pre-line;}

/* bullets — v0.3: 字級 1.2x */
.frame[data-type="bullets"]{justify-content:center;}
.btitle{font-family:'Noto Serif TC',serif;font-weight:900;font-size:4.2rem;line-height:1.25;color:var(--text);margin-bottom:2.2rem;white-space:pre-line;}
.blist{list-style:none;display:flex;flex-direction:column;gap:1.2rem;}
.blist li{font-family:'Noto Serif TC',serif;font-size:2.88rem;line-height:1.5;color:var(--text);display:flex;gap:1rem;align-items:baseline;}
.blist[data-style="dot"] li::before{content:"●";color:var(--accent);font-size:1.68rem;}
.blist[data-style="num"] li{counter-increment:bnum;}
.blist[data-style="num"]{counter-reset:bnum;}
.blist[data-style="num"] li::before{content:counter(bnum,decimal-leading-zero);font-family:'Noto Serif TC',serif;font-weight:900;color:var(--accent);min-width:2ch;}
.blist[data-style="arrow"] li::before{content:"→";color:var(--accent);font-weight:700;}
.bcaveat{margin-top:2.2rem;padding-top:1.5rem;border-top:2px solid rgba(0,212,170,.28);font-size:2.04rem;line-height:1.5;color:var(--accent-soft);font-weight:500;}  /* v0.8: caveat 常是 punchline，從 dim italic 升為 accent + 分隔線 */

/* stat — v0.3: 字級 1.2x、寬度用滿 */
.frame[data-type="stat"]{justify-content:center;}
.statval{font-family:'Noto Serif TC',serif;font-weight:900;font-size:9.12rem;line-height:1;color:var(--accent);letter-spacing:.01em;}
.statunit{font-family:'Noto Sans TC';font-weight:700;font-size:2.64rem;color:var(--text);margin-left:.3em;}
.statlabel{font-size:2.14rem;line-height:1.78;color:rgba(244,240,234,.9);margin-top:2rem;white-space:pre-line;}

/* chart-bars — v0.5: graph.md tw-bars port（水平比例條：排序大→小、長條從0、單一accent、直接標籤＞圖例） */
.frame[data-type="chart-bars"]{justify-content:center;}
.cb-title{font-family:'Noto Serif TC',serif;font-weight:900;font-size:3.72rem;line-height:1.3;color:var(--text);margin-bottom:2.8rem;white-space:pre-line;}
.cb-title em{color:var(--accent);font-style:normal;}
.cb-row{margin-bottom:2.4rem;}
.cb-row:last-of-type{margin-bottom:0;}
.cb-head{display:flex;justify-content:space-between;align-items:baseline;gap:1.2rem;margin-bottom:.8rem;}
.cb-label{font-family:'Noto Sans TC';font-weight:500;font-size:2.04rem;line-height:1.35;color:rgba(244,240,234,.92);}
.cb-val{font-family:'Noto Serif TC',serif;font-weight:900;font-size:3.0rem;color:var(--accent);white-space:nowrap;}
.cb-track{width:100%;height:2.7rem;background:rgba(244,240,234,.08);border-radius:7px;overflow:hidden;}
.cb-fill{height:100%;background:linear-gradient(90deg,var(--accent) 0%,var(--accent-soft) 100%);border-radius:7px;}
.cb-note{font-size:1.72rem;color:var(--text-dim);font-style:italic;margin-top:.7rem;}
.cb-source{margin-top:2.6rem;font-size:1.68rem;color:var(--text-dim);}

/* chart-stat — v0.5: graph.md tw-stat port（2-4 並排關鍵數字 + 標籤 + 註記） */
.frame[data-type="chart-stat"]{justify-content:center;}
.cs-title{font-family:'Noto Serif TC',serif;font-weight:900;font-size:3.72rem;line-height:1.3;color:var(--text);margin-bottom:3rem;white-space:pre-line;}
.cs-grid{display:flex;justify-content:space-between;gap:2.4rem;}
.cs-item{flex:1;display:flex;flex-direction:column;}
.cs-item + .cs-item{padding-left:2.4rem;border-left:2px solid rgba(0,212,170,.28);}
.cs-val{font-family:'Noto Serif TC',serif;font-weight:900;font-size:5.4rem;line-height:1;color:var(--accent);letter-spacing:.01em;}
.cs-label{font-family:'Noto Sans TC';font-weight:700;font-size:2.04rem;line-height:1.4;color:var(--text);margin-top:1.3rem;}
.cs-note{font-size:1.68rem;line-height:1.5;color:var(--text-dim);margin-top:.7rem;}
.cs-source{margin-top:3rem;font-size:1.68rem;color:var(--text-dim);}

/* versus — v0.6: graph.md tw-versus port（兩制度/兩路線並排對比） */
.frame[data-type="versus"]{justify-content:center;}
.vs-title{font-family:'Noto Serif TC',serif;font-weight:900;font-size:3.6rem;line-height:1.3;color:var(--text);margin-bottom:2.4rem;white-space:pre-line;}
.vs-head{display:flex;gap:0;margin-bottom:1.6rem;}
.vs-head>div{flex:1;font-family:'Noto Serif TC',serif;font-weight:900;font-size:2.7rem;color:var(--accent);text-align:center;padding-bottom:1rem;border-bottom:3px solid var(--accent);}
.vs-head>div:first-child{margin-right:1.6rem;}
.vs-head>div:last-child{margin-left:1.6rem;}
.vs-row{display:flex;gap:0;margin-bottom:1.6rem;align-items:stretch;}
.vs-row>div{flex:1;font-family:'Noto Sans TC';font-size:2.0rem;line-height:1.5;color:rgba(244,240,234,.92);}
.vs-row>div:first-child{text-align:right;padding-right:1.6rem;border-right:2px solid rgba(0,212,170,.3);}
.vs-row>div:last-child{text-align:left;padding-left:1.6rem;}

/* chart-timeline — v0.6: graph.md tw-timeline port（節點時間軸） */
.frame[data-type="chart-timeline"]{justify-content:center;}
.tl-title{font-family:'Noto Serif TC',serif;font-weight:900;font-size:3.6rem;line-height:1.3;color:var(--text);margin-bottom:2.6rem;white-space:pre-line;}
.tl-list{position:relative;padding-left:3.4rem;}
.tl-list::before{content:"";position:absolute;left:.95rem;top:.7rem;bottom:.7rem;width:3px;background:rgba(0,212,170,.4);}
.tl-node{position:relative;margin-bottom:2.4rem;}
.tl-node:last-child{margin-bottom:0;}
.tl-node::before{content:"";position:absolute;left:-2.8rem;top:.4rem;width:1.3rem;height:1.3rem;border-radius:50%;background:var(--accent);box-shadow:0 0 0 6px var(--ground);}
.tl-year{font-family:'Noto Serif TC',serif;font-weight:900;font-size:2.34rem;color:var(--accent);}
.tl-label{font-family:'Noto Serif TC',serif;font-weight:700;font-size:2.4rem;color:var(--text);margin:.15rem 0 .35rem;}
.tl-desc{font-size:1.86rem;line-height:1.5;color:var(--text-dim);}

/* chart-waffle — v0.6: graph.md tw-waffle port（100 格部分對全體；accent 明度階，色盲友善） */
.frame[data-type="chart-waffle"]{justify-content:center;align-items:center;}
.wf-title{font-family:'Noto Serif TC',serif;font-weight:900;font-size:3.24rem;line-height:1.3;color:var(--text);margin-bottom:1.8rem;white-space:pre-line;align-self:flex-start;}
.wf-grid{display:grid;grid-template-columns:repeat(10,1fr);gap:7px;width:560px;margin-bottom:2rem;}
.wf-cell{aspect-ratio:1;border-radius:5px;background:rgba(244,240,234,.08);}
.wf-legend{display:flex;flex-direction:column;gap:1rem;align-self:flex-start;width:100%;}
.wf-leg{display:flex;align-items:center;gap:1.1rem;font-size:2.04rem;color:var(--text);}
.wf-sw{width:1.7rem;height:1.7rem;border-radius:5px;flex-shrink:0;}
.wf-pct{margin-left:auto;color:var(--text-dim);font-variant-numeric:tabular-nums;}
.wf-source{margin-top:1.8rem;font-size:1.66rem;color:var(--text-dim);align-self:flex-start;}

/* chart-heatmap — v0.6: graph.md tw-heatmap port（矩陣，每欄各自正規化色深） */
.frame[data-type="chart-heatmap"]{justify-content:center;}
.hm-title{font-family:'Noto Serif TC',serif;font-weight:900;font-size:3.24rem;line-height:1.3;color:var(--text);margin-bottom:2rem;white-space:pre-line;}
.hm-table{width:100%;border-collapse:separate;border-spacing:7px;}
.hm-table th{font-family:'Noto Sans TC';font-weight:700;font-size:1.92rem;color:var(--text-dim);padding:.5rem;text-align:center;line-height:1.3;}
.hm-table th.hm-corner{text-align:left;}
.hm-rowhead{font-family:'Noto Sans TC';font-weight:700;color:var(--text);font-size:2.04rem;white-space:nowrap;text-align:left;padding-right:.8rem;}
.hm-cell{font-family:'Noto Serif TC',serif;font-weight:900;font-size:2.4rem;color:var(--text);text-align:center;padding:1.3rem .5rem;border-radius:9px;}
.hm-source{margin-top:1.8rem;font-size:1.66rem;color:var(--text-dim);}

/* chart-line — v0.6: graph.md tw-line port（趨勢折線，inline SVG + 終點直接標籤） */
.frame[data-type="chart-line"]{justify-content:center;}
.ln-title{font-family:'Noto Serif TC',serif;font-weight:900;font-size:3.24rem;line-height:1.3;color:var(--text);margin-bottom:2rem;white-space:pre-line;}
.ln-svg{width:100%;display:block;}
.ln-svg text{font-family:'Noto Sans TC';fill:var(--text-dim);}
.ln-svg .ln-end{font-family:'Noto Sans TC';font-weight:700;}
.ln-source{margin-top:1.6rem;font-size:1.66rem;color:var(--text-dim);}

/* quote — v0.3: 字級 1.2x */
.frame[data-type="quote"]{justify-content:center;}
.qmark{font-family:'Noto Serif TC',serif;font-weight:900;font-size:8.4rem;line-height:.6;color:var(--accent);opacity:.85;margin-bottom:.6rem;}
.qtext{font-family:'Noto Serif TC',serif;font-weight:700;font-size:4.8rem;line-height:1.5;color:var(--text);white-space:pre-line;}
.qby{font-size:2.28rem;color:var(--text-dim);margin-top:2rem;}

/* source — v0.3: 字級 1.2x */
.frame[data-type="source"]{background:linear-gradient(170deg,var(--dark) 0%,var(--dark-grad) 100%);justify-content:center;}
.srctitle{font-family:'Noto Sans TC';font-weight:700;font-size:2.04rem;letter-spacing:.18em;color:var(--accent);margin-bottom:1.6rem;}
.srclist{list-style:none;}
.srclist li{font-family:'Noto Serif TC',serif;font-size:2.88rem;line-height:1.8;color:var(--text);display:flex;gap:.7rem;align-items:baseline;}
.srclist li::before{content:"·";color:var(--accent);font-weight:900;}
.srcurl{margin-top:2.4rem;font-size:2.52rem;color:var(--accent-soft);font-weight:500;word-break:break-all;}
.cta{margin-top:2rem;font-size:2.4rem;line-height:1.7;color:rgba(244,240,234,.92);font-weight:500;white-space:pre-line;}

/* watermark bottom — v0.3: 字級 1.2x */
.foot{position:absolute;left:88px;right:88px;bottom:56px;display:flex;justify-content:space-between;align-items:center;}
.foot .fmark{display:inline-flex;align-items:center;gap:.5rem;font-weight:700;font-size:1.8rem;color:rgba(244,240,234,.85);}
.foot .fmark img{width:1.92rem;height:1.92rem;}
.foot .fmark .dot{color:var(--accent);}
.foot #footurl{font-size:1.68rem!important;}
.frame[data-type="cover"] .foot,.frame[data-type="source"] .foot{display:none;}
</style>
</head>
<body>
<div class="frame" id="frame">
  <div class="progress" id="progress"></div>
  <div class="brandrow">
    <span class="wordmark"><img id="wm1" alt="">Taiwan<span class="dot">.md</span></span>
    <span class="pageno" id="pageno"></span>
  </div>
  <div id="content"></div>
  <div class="foot"><span class="fmark"><img id="wm2" alt="">Taiwan<span class="dot">.md</span></span><span id="footurl" style="font-size:1.4rem;color:rgba(244,240,234,.6)"></span></div>
</div>
<script>
const FAVICON='${faviconUri}';
const HERO='${heroUri}';
document.getElementById('wm1').src=FAVICON;
document.getElementById('wm2').src=FAVICON;

// v0.8: 輕量語法高亮 — identifier / number / operator / CJK 分色（code-block 母片用）
window.__hl = (code) => {
  const re = /([A-Za-z_][\\w.\\-@\\/]*)|(\\d[\\d.]*%?)|(=|·|→|\\||├─|└─?)|(\\s+)|([\\s\\S])/g;
  return String(code).replace(re, (m, id, num, op, ws) => {
    if (id) return '<span class="t-id">'+id+'</span>';
    if (num) return '<span class="t-num">'+num+'</span>';
    if (op) return '<span class="t-op">'+op+'</span>';
    if (ws) return ws;
    return '<span class="t-cjk">'+m+'</span>';
  });
};

window.__renderSlide = (s) => {
  const frame=document.getElementById('frame');
  const content=document.getElementById('content');
  frame.setAttribute('data-type', s.type);
  frame.classList.toggle('hero', !!(s.type==='cover' && s.hero && HERO));
  frame.classList.toggle('secmedia', s.type==='section' && !!s.imageUri);
  if (s.type==='cover' && s.hero && HERO) frame.style.setProperty('--hero','url('+HERO+')');
  // progress bar width
  document.getElementById('progress').style.width = Math.round((s.index/s.total)*100)+'%';
  // page no (hide on cover)
  document.getElementById('pageno').textContent = s.type==='cover' ? '' : (s.index+' / '+s.total);
  document.getElementById('footurl').textContent = s.url || '';

  let html='';
  if (s.type==='cover'){
    html += s.kicker ? '<span class="kicker">'+s.kicker+'</span>' : '';
    html += '<h1 class="title">'+(s.title||'')+'</h1>';
    html += s.subtitle ? '<p class="subtitle">'+s.subtitle+'</p>' : '';
    html += s.date ? '<div class="coverdate">'+s.date+'</div>' : '';
    html += '<span class="swipe">滑看完整故事 <span class="arrow">→</span></span>';
  } else if (s.type==='section' || s.type==='point'){
    // 'point' kept as alias for backward-compat; canonical is 'section'
    if (s.type==='point') document.getElementById('frame').setAttribute('data-type','section');
    html += s.idx ? '<div class="idx">'+s.idx+'</div>' : '';
    html += '<div class="kw">'+(s.kw||'')+'</div>';
    if (s.imageUri) html += '<div class="secimg" style="background-image:url('+s.imageUri+')"></div>';
    html += s.caption ? '<div class="seccap">'+s.caption+'</div>' : '';
    html += s.body ? '<div class="body">'+s.body+'</div>' : '';
    html += s.code ? '<div class="codeblock">'+window.__hl(s.code)+'</div>' : '';
  } else if (s.type==='figure'){
    html += s.pull ? '<span class="figpull">'+s.pull+'</span>' : '';
    if (s.imageUri) html += '<div class="figimg" style="background-image:url('+s.imageUri+')"></div>';
    html += s.caption ? '<div class="figcap">'+s.caption+'</div>' : '';
    html += s.body ? '<div class="figbody">'+s.body+'</div>' : '';
  } else if (s.type==='bullets'){
    html += '<div class="btitle">'+(s.title||'')+'</div>';
    const items = s.items||[];
    const style = s.item_style||'dot';
    html += '<ul class="blist" data-style="'+style+'">'+items.map(t=>'<li><span>'+t+'</span></li>').join('')+'</ul>';
    html += s.caveat ? '<div class="bcaveat">'+s.caveat+'</div>' : '';
  } else if (s.type==='stat'){
    html += '<div><span class="statval">'+(s.value||'')+'</span><span class="statunit">'+(s.unit||'')+'</span></div>';
    html += s.label ? '<div class="statlabel">'+s.label+'</div>' : '';
  } else if (s.type==='chart-bars'){
    // graph.md tw-bars: 排序大→小（除非 sort:false 固定類別）/ 長條從 0 / 寬度比例縮放
    html += s.title ? '<div class="cb-title">'+s.title+'</div>' : '';
    let bars = s.bars || [];
    if (s.sort !== false) bars = bars.slice().sort((a,b)=>(Math.abs(b.value)||0)-(Math.abs(a.value)||0));
    const max = Math.max(1, ...bars.map(b=>Math.abs(b.value)||0));
    html += bars.map(b=>{
      const w = Math.max(2, Math.round((Math.abs(b.value)||0)/max*100));
      const val = b.display != null ? b.display : (b.value != null ? b.value : '');
      return '<div class="cb-row">'
        + '<div class="cb-head"><span class="cb-label">'+(b.label||'')+'</span><span class="cb-val">'+val+'</span></div>'
        + '<div class="cb-track"><div class="cb-fill" style="width:'+w+'%"></div></div>'
        + (b.note ? '<div class="cb-note">'+b.note+'</div>' : '')
        + '</div>';
    }).join('');
    html += s.source_note ? '<div class="cb-source">'+s.source_note+'</div>' : '';
  } else if (s.type==='chart-stat'){
    // graph.md tw-stat: 2-4 並排數字
    html += s.title ? '<div class="cs-title">'+s.title+'</div>' : '';
    const items = s.stats || [];
    html += '<div class="cs-grid">'+items.map(it=>
      '<div class="cs-item">'
      + '<span class="cs-val">'+(it.value||'')+'</span>'
      + (it.label ? '<span class="cs-label">'+it.label+'</span>' : '')
      + (it.note ? '<span class="cs-note">'+it.note+'</span>' : '')
      + '</div>').join('')+'</div>';
    html += s.source_note ? '<div class="cs-source">'+s.source_note+'</div>' : '';
  } else if (s.type==='versus'){
    // graph.md tw-versus: 兩制度逐點對照
    html += s.title ? '<div class="vs-title">'+s.title+'</div>' : '';
    html += '<div class="vs-head"><div>'+(s.left||'')+'</div><div>'+(s.right||'')+'</div></div>';
    html += (s.rows||[]).map(r=>{
      const l = r.l != null ? r.l : (Array.isArray(r) ? r[0] : '');
      const rr = r.r != null ? r.r : (Array.isArray(r) ? r[1] : '');
      return '<div class="vs-row"><div>'+l+'</div><div>'+rr+'</div></div>';
    }).join('');
  } else if (s.type==='chart-timeline'){
    // graph.md tw-timeline: 節點時間軸
    html += s.title ? '<div class="tl-title">'+s.title+'</div>' : '';
    html += '<div class="tl-list">'+(s.nodes||[]).map(n=>
      '<div class="tl-node">'
      + (n.year ? '<div class="tl-year">'+n.year+'</div>' : '')
      + (n.label ? '<div class="tl-label">'+n.label+'</div>' : '')
      + (n.desc ? '<div class="tl-desc">'+n.desc+'</div>' : '')
      + '</div>').join('')+'</div>';
  } else if (s.type==='chart-waffle'){
    // graph.md tw-waffle: 100 格部分對全體；accent 明度階（色盲友善）
    // v0.8: 三 tint 明度+彩度雙軸分離，且全部明顯亮於主底 #1a3c34（critic：原 dark 類沉進背景數不出來）
    const PAL = ['#5fd9c0','#3f9e8c','#9fc4b9','#7aa99d','#c6d8d1','#8a9aa2'];
    const cells = s.cells||[];
    html += s.title ? '<div class="wf-title">'+s.title+'</div>' : '';
    const seq=[];
    cells.forEach((c,i)=>{ const cnt=Math.round(Math.abs(c.pct)||0); for(let k=0;k<cnt;k++) seq.push(i); });
    const grid = Array.from({length:100},(_,i)=>{
      const ci = seq[i];
      return ci>=0 && ci!=null ? '<div class="wf-cell" style="background:'+PAL[ci%PAL.length]+'"></div>' : '<div class="wf-cell"></div>';
    }).join('');
    html += '<div class="wf-grid">'+grid+'</div>';
    html += '<div class="wf-legend">'+cells.map((c,i)=>
      '<div class="wf-leg"><span class="wf-sw" style="background:'+PAL[i%PAL.length]+'"></span>'
      +'<span>'+(c.label||'')+'</span><span class="wf-pct">'+(c.pct!=null?c.pct+'%':'')+'</span></div>').join('')+'</div>';
    html += s.source_note ? '<div class="wf-source">'+s.source_note+'</div>' : '';
  } else if (s.type==='chart-heatmap'){
    // graph.md tw-heatmap: 矩陣，每欄各自正規化成 accent 不透明度
    const cols = s.cols||[];
    const rows = s.rows||[];
    html += s.title ? '<div class="hm-title">'+s.title+'</div>' : '';
    const colMax = cols.map((_,ci)=>Math.max(1,...rows.map(r=>Math.abs((r.values||[])[ci])||0)));
    const thead='<tr><th class="hm-corner">'+(s.corner||'')+'</th>'+cols.map(c=>'<th>'+c+'</th>').join('')+'</tr>';
    const tbody=rows.map(r=>'<tr><td class="hm-rowhead">'+(r.label||'')+'</td>'
      +(r.values||[]).map((v,ci)=>{
        // v0.8: 二次曲線拉大值差對比（critic：相近值看起來同色），低端 .12 不刺眼、高端 .62 仍克制
        const _r = (Math.abs(v) || 0) / colMax[ci];
        const op = 0.12 + _r * _r * 0.5;
        return '<td class="hm-cell" style="background:rgba(0,212,170,'+op.toFixed(2)+')">'+(v!=null?v:'')+'</td>';
      }).join('')+'</tr>').join('');
    html += '<table class="hm-table"><thead>'+thead+'</thead><tbody>'+tbody+'</tbody></table>';
    html += s.source_note ? '<div class="hm-source">'+s.source_note+'</div>' : '';
  } else if (s.type==='chart-line'){
    // graph.md tw-line: 趨勢折線，自動 y 範圍 + 終點直接標籤（不用圖例）
    html += s.title ? '<div class="ln-title">'+s.title+'</div>' : '';
    const xs = s.x||[];
    const series = s.series||[];
    const W=900,H=520,PL=78,PR=210,PT=34,PB=72;
    const allY = series.flatMap(se=>(se.points||[])).filter(v=>v!=null).map(Number);
    let ymin=Math.min(...allY), ymax=Math.max(...allY);
    if(!isFinite(ymin)){ymin=0;ymax=1;}
    if(ymin===ymax){ymin-=1;ymax+=1;}
    const pad=(ymax-ymin)*0.12; ymin-=pad; ymax+=pad;
    const n=xs.length;
    const xAt=i=> PL + (n<=1?0:(i/(n-1))*(W-PL-PR));
    const yAt=v=> PT + (1-((v-ymin)/(ymax-ymin)))*(H-PT-PB);
    const COL=['#00d4aa','#4fd1b0','#7de8d0','#1a9e85'];
    const by=H-PB; // x 軸基線 y
    let svg='<svg class="ln-svg" viewBox="0 0 '+W+' '+H+'" preserveAspectRatio="xMidYMid meet">';
    // v0.7: 軸線結構 + 每點數值標籤（哲宇 callout「缺圖說跟線條、看不太懂」）
    xs.forEach((xl,i)=>{ const x=xAt(i); svg+='<line x1="'+x+'" y1="'+PT+'" x2="'+x+'" y2="'+by+'" stroke="rgba(244,240,234,.06)"/>'; });
    svg+='<line x1="'+PL+'" y1="'+by+'" x2="'+(W-PR+50)+'" y2="'+by+'" stroke="rgba(244,240,234,.24)" stroke-width="2"/>'; // x 軸
    svg+='<line x1="'+PL+'" y1="'+PT+'" x2="'+PL+'" y2="'+by+'" stroke="rgba(244,240,234,.16)" stroke-width="2"/>'; // y 軸
    xs.forEach((xl,i)=>{ svg+='<text x="'+xAt(i)+'" y="'+(by+44)+'" text-anchor="middle" font-size="26">'+xl+'</text>'; });
    // v0.8: series 可標 ref:true → 虛線基準（dim、無點、無值標籤、單一右標）vs 實測序列（critic：平直基準畫成兩點實線像被測量）
    series.forEach((se,si)=>{
      const isRef = !!se.ref;
      const col = isRef ? 'rgba(244,240,234,.5)' : COL[si%COL.length];
      const ps=se.points||[];
      svg+='<polyline points="'+ps.map((v,i)=>xAt(i)+','+yAt(v)).join(' ')+'" fill="none" stroke="'+col+'" stroke-width="'+(isRef?3:5)+'"'+(isRef?' stroke-dasharray="11 9"':'')+' stroke-linejoin="round" stroke-linecap="round"/>';
      if(!isRef) ps.forEach((v,i)=>{
        svg+='<circle cx="'+xAt(i)+'" cy="'+yAt(v)+'" r="7" fill="'+col+'"/>';
        svg+='<text x="'+xAt(i)+'" y="'+(yAt(v)-22)+'" text-anchor="middle" font-size="29" font-weight="700" fill="'+col+'">'+v+'</text>';
      });
      const lastI=ps.length-1;
      if(lastI>=0) svg+='<text class="ln-end" x="'+(xAt(lastI)+18)+'" y="'+(yAt(ps[lastI])+8)+'" font-size="'+(isRef?23:25)+'" fill="'+col+'">'+(se.name||'')+'</text>';
    });
    svg+='</svg>';
    html += svg;
    html += s.source_note ? '<div class="ln-source">'+s.source_note+'</div>' : '';
  } else if (s.type==='quote'){
    html += '<div class="qmark">“</div>';
    html += '<div class="qtext">'+(s.text||'')+'</div>';
    html += s.by ? '<div class="qby">'+s.by+'</div>' : '';
  } else if (s.type==='source'){
    html += '<div class="srctitle">資料來源　SOURCES</div>';
    html += '<ul class="srclist">'+(s.sources||[]).map(x=>'<li>'+x+'</li>').join('')+'</ul>';
    html += s.url ? '<div class="srcurl">'+s.url+'</div>' : '';
    html += s.cta ? '<div class="cta">'+s.cta+'</div>' : '';
  }
  content.innerHTML = html;
};

window.__waitFontReady = async () => {
  await document.fonts.ready;
  await Promise.all([
    document.fonts.load('900 80px "Noto Serif TC"'),
    document.fonts.load('700 40px "Noto Serif TC"'),
    document.fonts.load('700 30px "Noto Sans TC"'),
    document.fonts.load('400 30px "Noto Sans TC"'),
  ]);
  return document.fonts.check('900 80px "Noto Serif TC"');
};
window.__doubleRaf = () => new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
</script>
</body>
</html>`;
}

// ── main ─────────────────────────────────────────────────────────────────────
async function main() {
  const slides = script.slides || [];
  if (!slides.length) {
    console.error('❌ slides 為空');
    process.exit(1);
  }
  const outDir = join(outRoot, script.slug);
  if (!existsSync(outDir)) mkdirSync(outDir, { recursive: true });

  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext({
    viewport: VIEWPORT,
    deviceScaleFactor: 2,
    reducedMotion: 'reduce',
  });
  const page = await ctx.newPage();
  await page.setContent(buildTemplateHtml(), { waitUntil: 'domcontentloaded' });
  try {
    await page.waitForFunction(
      () => typeof window.__waitFontReady === 'function',
      { timeout: 5000 },
    );
    await page.evaluate(() => window.__waitFontReady());
  } catch (_) {
    /* continue */
  }

  const total = slides.length;
  let n = 0;
  for (const slide of slides) {
    n++;
    // pre-load per-slide image (figure / section with image) as base64 to avoid network in headless
    let imageUri = '';
    if (slide.image) {
      try {
        imageUri = toDataUri(resolve(repoRoot, slide.image));
      } catch (e) {
        console.warn(`  ⚠ slide ${n} image not found: ${slide.image}`);
      }
    }
    const payload = {
      ...slide,
      imageUri,
      index: n,
      total,
      url: script.url || '',
    };
    await page.evaluate((d) => window.__renderSlide(d), payload);
    await page.evaluate(() => window.__doubleRaf());
    const file = join(outDir, `slide-${String(n).padStart(2, '0')}.png`);
    await page.screenshot({
      path: file,
      clip: { x: 0, y: 0, width: VIEWPORT.width, height: VIEWPORT.height },
      animations: 'disabled',
    });
    console.log(
      `  ✓ ${slide.type.padEnd(7)} → ${file.replace(repoRoot + '/', '')}`,
    );
  }
  await ctx.close();
  await browser.close();
  console.log(`\n✨ ${total} slides → ${outDir.replace(repoRoot + '/', '')}/`);

  // v0.4: auto-open output folder (per哲宇 directive 2026-06-03)
  // macOS: open / Linux: xdg-open / Windows: explorer
  // skip if --no-open or env CAROUSEL_NO_OPEN=1
  const noOpen =
    process.argv.includes('--no-open') || process.env.CAROUSEL_NO_OPEN === '1';
  if (!noOpen) {
    const cmd =
      platform() === 'darwin'
        ? 'open'
        : platform() === 'win32'
          ? 'explorer'
          : 'xdg-open';
    try {
      spawn(cmd, [outDir], { detached: true, stdio: 'ignore' }).unref();
      console.log(`📂 opened: ${outDir.replace(repoRoot + '/', '')}/`);
    } catch (e) {
      console.warn(`⚠ failed to auto-open folder: ${e.message}`);
    }
  }
}

main().catch((e) => {
  console.error('❌', e);
  process.exit(1);
});
