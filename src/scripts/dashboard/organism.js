import { isEn, animateValue } from './shared.js';

// Cross-module state adapter：renderOrganism 的 concern hints（免疫/語言器官）讀
// allArticles — monolith 時代共用頂層 let，拆模組後 orchestrator 以 setter 供給。
let allArticles = [];
export function setOrganismArticles(a) {
  allArticles = a;
}

// ── Organism Anatomy ──
const organColorMap = {
  '❤️': '#ef4444',
  '🫀': '#ef4444',
  心臟: '#ef4444',
  Heart: '#ef4444',
  '🧠': '#8b5cf6',
  大腦: '#8b5cf6',
  Brain: '#8b5cf6',
  '🫁': '#3b82f6',
  肺: '#3b82f6',
  Lungs: '#3b82f6',
  '🦴': '#f59e0b',
  骨骼: '#f59e0b',
  Skeleton: '#f59e0b',
  '🩸': '#f87171',
  血液: '#f87171',
  Blood: '#f87171',
  '👁️': '#06b6d4',
  眼睛: '#06b6d4',
  Eyes: '#06b6d4',
  '🦷': '#e2e8f0',
  牙齒: '#e2e8f0',
  Teeth: '#e2e8f0',
  '💪': '#ec4899',
  肌肉: '#ec4899',
  Muscles: '#ec4899',
  '🧬': '#a855f7',
  DNA: '#a855f7',
  '🛡️': '#4ade80',
  免疫: '#4ade80',
  Immunity: '#4ade80',
};
function getOrganColor(o) {
  return (
    organColorMap[o.emoji] ||
    organColorMap[o.name] ||
    organColorMap[o.nameZh] ||
    null
  );
}

function renderOrganism(data) {
  const organFileMap = {
    heart: {
      file: 'knowledge/',
      label: 'knowledge/',
      desc: isEn ? 'Content directory' : '內容目錄',
    },
    immune: {
      file: 'docs/editorial/EDITORIAL.md',
      label: 'EDITORIAL.md',
      desc: isEn ? 'Quality guidelines' : '品質規範',
    },
    dna: {
      file: 'docs/editorial/EDITORIAL.md',
      label: 'EDITORIAL.md',
      desc: isEn ? 'Editorial DNA' : '編輯基因',
    },
    skeleton: {
      file: 'astro.config.mjs',
      label: 'astro.config.mjs',
      desc: isEn ? 'Framework config' : '框架配置',
    },
    breath: {
      file: '.github/workflows/',
      label: '.github/workflows/',
      desc: isEn ? 'CI/CD pipelines' : 'CI/CD 管線',
    },
    reproduce: {
      file: 'CONTRIBUTING.md',
      label: 'CONTRIBUTING.md',
      desc: isEn ? 'Contributor guide' : '貢獻指南',
    },
    senses: {
      file: '.github/ISSUE_TEMPLATE/',
      label: '.github/ISSUE_TEMPLATE/',
      desc: isEn ? 'Issue templates' : 'Issue 模板',
    },
    translation: {
      file: 'src/content/',
      label: 'src/content/',
      desc: isEn ? 'Translation files' : '翻譯檔案',
    },
  };

  const grid = document.getElementById('organ-grid');
  grid.innerHTML = data.organs
    .map((o) => {
      const defaultColor =
        o.score >= 70 ? '#4ade80' : o.score >= 40 ? '#facc15' : '#f87171';
      const barColor = getOrganColor(o) || defaultColor;
      const trendIcon = o.trend === 'up' ? '↑' : o.trend === 'down' ? '↓' : '→';
      const trendClass = o.trend;
      const isHeart =
        o.emoji === '❤️' || o.emoji === '🫀' || o.name === 'Heart';
      const heartClass = isHeart ? ' organ-card-heart' : '';
      const scoreTint =
        o.score < 30
          ? 'background:rgba(248,113,113,0.04);'
          : o.score >= 70
            ? 'background:rgba(74,222,128,0.04);'
            : '';
      const topBorder = 'border-top:3px solid ' + barColor + ';';
      const organKey = (o.id || o.name || '').toLowerCase();
      const fileInfo = organFileMap[organKey] || null;
      const fileFooter = fileInfo
        ? `<div class="organ-file"><a href="https://github.com/hansai-art/computex-md/tree/main/${fileInfo.file}" target="_blank" rel="noopener" class="organ-file-link">📁 ${fileInfo.label}</a></div>`
        : '';
      // Concern hint based on organ type
      let concern = '';
      if (organKey === 'immune' || organKey === '免疫系統') {
        const naked = allArticles.filter((a) => (a.fnCount || 0) === 0).length;
        concern = isEn
          ? `${naked} articles without footnotes`
          : `${naked} 篇無腳註`;
      } else if (organKey === 'language' || organKey === '語言器官') {
        const esPct = Math.round(
          (allArticles.filter((a) => a.translations?.es).length /
            allArticles.length) *
            100,
        );
        concern = isEn
          ? `ES ${esPct}%, JA needs growth`
          : `ES ${esPct}%，JA 待成長`;
      }
      const concernHtml = concern
        ? `<div class="organ-concern">${concern}</div>`
        : '';

      return `<div class="organ-card${heartClass}" style="${topBorder}${scoreTint}">
          <div class="organ-header">
            <span class="organ-emoji">${o.emoji}</span>
            <span class="organ-name">${isEn ? o.name : o.nameZh}</span>
          </div>
          <div class="organ-metaphor">${o.metaphor}</div>
          <div class="organ-score-row">
            <div class="organ-score" data-score="${o.score}" style="color:${barColor}">${o.score}</div>
            <span class="organ-trend ${trendClass}">${trendIcon}</span>
          </div>
          <div class="organ-bar"><div class="organ-bar-fill" style="width:${o.score}%;background:${barColor}"></div></div>
          ${concernHtml}
          ${fileFooter}
        </div>`;
    })
    .join('');

  // Animate organ scores
  document.querySelectorAll('.organ-score[data-score]').forEach((el, i) => {
    const target = parseInt(el.dataset.score, 10);
    el.textContent = '0';
    setTimeout(() => animateValue(el, 0, target, 700), i * 100);
  });
}

export { renderOrganism };
