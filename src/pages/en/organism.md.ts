import type { APIRoute } from 'astro';
import {
  buildOrganismMarkdown,
  ORGANISM_MD_HEADERS,
} from '../../utils/organismText';

export const prerender = true;

export const GET: APIRoute = async () =>
  new Response(buildOrganismMarkdown('en'), {
    headers: ORGANISM_MD_HEADERS,
  });
