/**
 * backend.ts — Feedback backend 兩種實作 + factory。
 *
 *  - SupabaseBackend：正式。supabase-js（dynamic import,只在 mode=supabase 才載）。
 *  - MockBackend：瀏覽器內 localStorage,給 preview / e2e 測試。完整模擬 login→email→
 *    nickname→submit,不需要任何外部服務。
 *
 * 隔離原則：任何 init/SDK 載入失敗 → factory 回 null,widget 降級成 github-only。
 */
import type {
  FeedbackBackend,
  FeedbackDraft,
  FeedbackUser,
  MyFeedbackItem,
  OAuthProvider,
  SubmitResult,
} from './types';
import { resolveDisplayName } from './types';
import {
  SUPABASE_URL,
  SUPABASE_ANON_KEY,
  resolveBackendKind,
} from '../../config/feedback.mjs';

// ─────────────────────────────────────────────────────────────────────────────
// Mock backend（測試用）
// ─────────────────────────────────────────────────────────────────────────────
const LS_USER = 'twmd_fb_user';
const LS_NICK = 'twmd_fb_nickname';
const LS_ITEMS = 'twmd_fb_items';

interface MockUserRecord {
  uid: string;
  email: string;
  oauthName: string | null;
}

class MockBackend implements FeedbackBackend {
  readonly kind = 'mock' as const;

  async init(): Promise<void> {
    /* nothing to load */
  }

  private read(): MockUserRecord | null {
    try {
      const raw = localStorage.getItem(LS_USER);
      return raw ? (JSON.parse(raw) as MockUserRecord) : null;
    } catch {
      return null;
    }
  }

  private toUser(rec: MockUserRecord): FeedbackUser {
    const nickname = localStorage.getItem(LS_NICK);
    return {
      uid: rec.uid,
      email: rec.email,
      displayName: resolveDisplayName(nickname, rec.oauthName, rec.email),
      // v2 低阻力：OAuth 給了名字就不再問暱稱（只有 email-only 且沒設過才問）。
      needsNickname: !nickname && !rec.oauthName,
    };
  }

  async currentUser(): Promise<FeedbackUser | null> {
    const rec = this.read();
    return rec ? this.toUser(rec) : null;
  }

  private uuid(): string {
    return (crypto as any).randomUUID
      ? crypto.randomUUID()
      : 'mock-' + Math.abs(Date.now()).toString(36);
  }

  async signInWithOAuth(provider: OAuthProvider): Promise<void> {
    const rec: MockUserRecord = {
      uid: this.uuid(),
      email:
        provider === 'github'
          ? 'tester@users.noreply.github.com'
          : 'tester.google@gmail.com',
      oauthName: provider === 'github' ? 'GitHub 測試者' : 'Google 測試者',
    };
    localStorage.setItem(LS_USER, JSON.stringify(rec));
  }

  async signInWithEmail(email: string): Promise<{ sent: boolean }> {
    // mock：直接登入,sent:false 代表「已登入,繼續」（不用去收信）。
    const rec: MockUserRecord = { uid: this.uuid(), email, oauthName: null };
    localStorage.setItem(LS_USER, JSON.stringify(rec));
    return { sent: false };
  }

  async saveNickname(nickname: string): Promise<FeedbackUser> {
    const rec = this.read();
    if (!rec) throw new Error('not signed in');
    localStorage.setItem(LS_NICK, (nickname || '').trim());
    return this.toUser(rec);
  }

  async submit(draft: FeedbackDraft): Promise<SubmitResult> {
    const rec = this.read();
    if (!rec) throw new Error('not signed in');
    const id = this.uuid();
    const row = {
      id,
      created_at: new Date().toISOString(),
      uid: rec.uid,
      display_name: this.toUser(rec).displayName,
      status: 'new',
      ...draft,
    };
    let items: unknown[] = [];
    try {
      items = JSON.parse(localStorage.getItem(LS_ITEMS) || '[]');
    } catch {
      items = [];
    }
    items.push(row);
    localStorage.setItem(LS_ITEMS, JSON.stringify(items));
    return { id };
  }

  async myFeedback(): Promise<MyFeedbackItem[]> {
    const rec = this.read();
    if (!rec) return [];
    let items: any[] = [];
    try {
      items = JSON.parse(localStorage.getItem(LS_ITEMS) || '[]');
    } catch {
      items = [];
    }
    return items
      .filter((it) => it.uid === rec.uid)
      .reverse()
      .map((it) => ({
        id: it.id,
        type: it.type,
        body: it.body,
        status: it.status || 'new',
        issueUrl: it.issue_url || null,
        issueNumber: it.issue_number || null,
        triageNote: it.triage_note || null,
        createdAt: it.created_at,
        articleTitle: it.articleTitle || it.article_title || null,
        quote: it.quote || null,
      }));
  }

  async signOut(): Promise<void> {
    localStorage.removeItem(LS_USER);
    localStorage.removeItem(LS_NICK);
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Supabase backend（正式）
// ─────────────────────────────────────────────────────────────────────────────
class SupabaseBackend implements FeedbackBackend {
  readonly kind = 'supabase' as const;
  private sb: any = null;

  async init(): Promise<void> {
    const { createClient } = await import('@supabase/supabase-js');
    this.sb = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
      auth: {
        persistSession: true,
        autoRefreshToken: true,
        detectSessionInUrl: true,
      },
    });
  }

  private async session() {
    const { data } = await this.sb.auth.getSession();
    return data?.session || null;
  }

  async currentUser(): Promise<FeedbackUser | null> {
    const session = await this.session();
    const u = session?.user;
    if (!u) return null;
    const email: string = u.email || '';
    const oauthName: string | null =
      u.user_metadata?.full_name || u.user_metadata?.name || null;

    // 確保 profiles 有一列（email 落地 = goal「至少拿到 email」）。
    let nickname: string | null = null;
    try {
      const { data: prof } = await this.sb
        .from('profiles')
        .select('nickname,email')
        .eq('uid', u.id)
        .maybeSingle();
      if (!prof) {
        await this.sb
          .from('profiles')
          .upsert({ uid: u.id, email }, { onConflict: 'uid' });
      } else {
        nickname = prof.nickname || null;
        if (!prof.email && email) {
          await this.sb.from('profiles').update({ email }).eq('uid', u.id);
        }
      }
    } catch {
      /* profile fetch best-effort；不擋登入 */
    }

    return {
      uid: u.id,
      email,
      displayName: resolveDisplayName(nickname, oauthName, email),
      // v2 低阻力：OAuth 給了名字就不再問暱稱。
      needsNickname: !nickname && !oauthName,
    };
  }

  async signInWithOAuth(provider: OAuthProvider): Promise<void> {
    await this.sb.auth.signInWithOAuth({
      provider,
      options: { redirectTo: location.href },
    });
    // OAuth 會 redirect 離開頁面；回來後 detectSessionInUrl 還原 session。
  }

  async signInWithEmail(email: string): Promise<{ sent: boolean }> {
    const { error } = await this.sb.auth.signInWithOtp({
      email,
      options: { emailRedirectTo: location.href },
    });
    if (error) throw error;
    return { sent: true }; // 寄出 magic-link,使用者去收信點連結。
  }

  async saveNickname(nickname: string): Promise<FeedbackUser> {
    const session = await this.session();
    const u = session?.user;
    if (!u) throw new Error('not signed in');
    await this.sb
      .from('profiles')
      .upsert(
        { uid: u.id, email: u.email || '', nickname: (nickname || '').trim() },
        { onConflict: 'uid' },
      );
    const user = await this.currentUser();
    if (!user) throw new Error('lost session');
    return user;
  }

  async submit(draft: FeedbackDraft): Promise<SubmitResult> {
    const user = await this.currentUser();
    if (!user) throw new Error('not signed in');
    const { data, error } = await this.sb
      .from('feedback')
      .insert({
        uid: user.uid,
        display_name: user.displayName, // 只存 display_name,email 不進 feedback 列
        article_slug: draft.articleSlug,
        article_title: draft.articleTitle,
        category: draft.category,
        lang: draft.lang,
        source_url: draft.sourceUrl,
        type: draft.type,
        body: draft.body,
        correct_info: draft.correctInfo || null,
        quote: draft.quote || null,
        page_kind: draft.pageKind || null,
        status: 'new',
      })
      .select('id')
      .single();
    if (error) throw error;
    return { id: data.id };
  }

  async myFeedback(): Promise<MyFeedbackItem[]> {
    // RLS 自動限定為自己的列（feedback_select_own policy）。
    const { data, error } = await this.sb
      .from('feedback')
      .select('*')
      .order('created_at', { ascending: false })
      .limit(30);
    if (error) throw error;
    return (data || []).map((r: any) => ({
      id: r.id,
      type: r.type,
      body: r.body,
      status: r.status,
      issueUrl: r.issue_url ?? null,
      issueNumber: r.issue_number ?? null,
      triageNote: r.triage_note ?? null, // 0003 後才有；缺欄位 → undefined → null
      createdAt: r.created_at,
      articleTitle: r.article_title ?? null,
      quote: r.quote ?? null,
    }));
  }

  async signOut(): Promise<void> {
    await this.sb.auth.signOut();
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Factory
// ─────────────────────────────────────────────────────────────────────────────
/**
 * 回傳已 init 的 backend,或 null（= widget 走 github-only fallback）。
 * 任何錯誤都 swallow 成 null,確保不影響主站。
 */
export async function createBackend(): Promise<FeedbackBackend | null> {
  const kind = resolveBackendKind();
  try {
    if (kind === 'supabase') {
      const b = new SupabaseBackend();
      await b.init();
      return b;
    }
    if (kind === 'mock') {
      const b = new MockBackend();
      await b.init();
      return b;
    }
    return null; // 'off' / 'github-only'
  } catch (err) {
    console.warn('[feedback] backend init failed, degrading:', err);
    return null;
  }
}
