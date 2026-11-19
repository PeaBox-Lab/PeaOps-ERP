const API = import.meta.env.VITE_API_URL ?? '/api/v1';

export type Session = { token: string; refresh: string; companyId: number; username: string; permissions: string[]; expiresAt: number; mustChangePassword: boolean };
const KEY = 'peaops.session.v1';

export const loadSession = (): Session | null => {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return null;
    const s = JSON.parse(raw) as Session;
    if (!s.token || !s.refresh || !s.companyId || typeof s.expiresAt !== 'number') { clearSession(); return null; }
    return s;
  } catch { clearSession(); return null; }
};
export const saveSession = (s: Session) => localStorage.setItem(KEY, JSON.stringify(s));
export const clearSession = () => localStorage.removeItem(KEY);

const SKEW_MS = 30_000;
let refreshInFlight: Promise<Session | null> | null = null;

async function tryRefresh(s: Session): Promise<Session | null> {
  if (refreshInFlight) return refreshInFlight;
  refreshInFlight = (async () => {
    try {
      const res = await fetch(`${API}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: s.refresh }),
      });
      if (!res.ok) return null;
      const data = await res.json() as { access_token: string; expires_in: number };
      const fresh: Session = { ...s, token: data.access_token, expiresAt: Date.now() + data.expires_in * 1000 };
      saveSession(fresh);
      return fresh;
    } catch {
      return null;
    }
  })();
  try { return await refreshInFlight; } finally { refreshInFlight = null; }
}

async function ensureFresh(s: Session | null): Promise<Session | null> {
  if (!s) return null;
  if (Date.now() < s.expiresAt - SKEW_MS) return s;
  return tryRefresh(s);
}

const expireToLogin = () => { clearSession(); window.location.hash = ''; window.location.reload(); };

async function request<T>(base: string, path: string, init: RequestInit = {}, auth = true): Promise<T> {
  let s = loadSession();
  if (auth) { s = await ensureFresh(s); if (!s) { expireToLogin(); throw new Error('Session expired — sign in again'); } }
  const doFetch = async () => fetch(`${base}${path}`, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...(auth && s ? { Authorization: `Bearer ${s!.token}` } : {}), ...(init.headers || {}) },
  });
  let res = await doFetch();
  if (auth && res.status === 401) {
    s = s ? await tryRefresh(s) : null;
    if (!s) { expireToLogin(); throw new Error('Session expired — sign in again'); }
    res = await doFetch();
  }
  if (!res.ok) {
    let detail = `${res.status} ${res.statusText}`;
    try { const b = await res.json() as { detail?: string }; if (b?.detail) detail = String(b.detail); } catch {}
    if (res.status === 401) { expireToLogin(); }
    throw new Error(detail);
  }
  if (res.status === 204) return undefined as T;
  const ct = res.headers.get('content-type') ?? '';
  if (!ct.includes('application/json')) return (await res.text()) as unknown as T;
  return (await res.json()) as T;
}
export const api = <T>(path: string, init: RequestInit = {}, auth = true) => request<T>(API, path, init, auth);

export type Row = Record<string, unknown>;
export const money = (v: unknown) => Number(v ?? 0).toLocaleString('en-IN', { style: 'currency', currency: 'INR' });
