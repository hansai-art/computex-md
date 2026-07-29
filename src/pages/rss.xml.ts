import rss from '@astrojs/rss';
import fs from 'fs';
import path from 'path';
import matter from 'gray-matter';

export async function GET(context) {
  // 掃描 knowledge/ 下所有文章
  const knowledgeDir = path.join(process.cwd(), 'knowledge');
  const articles = [];

  // 遞迴掃描
  function scanDir(dir, category = '') {
    const files = fs.readdirSync(dir);
    for (const file of files) {
      const full = path.join(dir, file);
      const stat = fs.statSync(full);
      if (
        stat.isDirectory() &&
        !file.startsWith('_') &&
        file !== 'en' &&
        file !== 'about'
      ) {
        scanDir(full, file);
      } else if (file.endsWith('.md') && !file.startsWith('_')) {
        try {
          const content = fs.readFileSync(full, 'utf-8');
          const { data } = matter(content);
          if (data.title) {
            articles.push({
              title: data.title,
              description: data.description || '',
              pubDate: data.date ? new Date(data.date) : new Date(),
              link: `/${(data.category || category).toLowerCase()}/${file.replace('.md', '')}`,
              category: data.category || category,
            });
          }
        } catch {
          // YAML parse error, skip this file
        }
      }
    }
  }

  scanDir(knowledgeDir);

  // 按日期排序，取最新 50 篇
  articles.sort((a, b) => b.pubDate - a.pubDate);

  return rss({
    title: 'COMPUTEX.md：台灣 AI 硬體產業活體年鑑',
    description:
      'COMPUTEX 參展廠商、產品與歷屆展會的開放檔案庫。事實層機械抽取自官方名錄，逐項附出處連結與查證日期；官方沒公布的一律留白。',
    site: context.site || 'https://computex.taiwanai.ngo',
    items: articles.slice(0, 50),
    customData: '<language>zh-TW</language>',
  });
}
