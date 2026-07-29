/**
 * /api/organism.json：生命體的完整數值
 *
 * 其他 /api/*.json 是 scripts/core/*.mjs 寫進 public/api/ 的靜態檔。這一支走
 * Astro 路由而不是那條路，因為它跟 /organism 與 /organism.md 同一個資料源
 * （src/data/organism.json），走同一支 builder 就不會有「頁面改了、JSON 沒改」
 * 的漂移。三份輸出永遠是同一次計算的三種格式。
 */
import type { APIRoute } from 'astro';
import {
  buildOrganismJson,
  ORGANISM_JSON_HEADERS,
} from '../../utils/organismText';

export const prerender = true;

export const GET: APIRoute = async () =>
  new Response(JSON.stringify(buildOrganismJson(), null, 2), {
    headers: ORGANISM_JSON_HEADERS,
  });
