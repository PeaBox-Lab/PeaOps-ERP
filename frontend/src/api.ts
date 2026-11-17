const API = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1';
const ROOT = import.meta.env.VITE_API_ROOT ?? 'http://localhost:8000';

export type Session = { token: string; refresh: string; companyId: number; username: string; permissions: string[] };
const KEY = 'peaops.session.v1';
export const loadSession = (): Session | null => {
  try { const raw = localStorage.getItem(KEY); return raw ? JSON.parse(raw) as Session : null; } catch { return null; }
};
export const saveSession = (s: Session) => localStorage.setItem(KEY, JSON.stringify(s));
export const clearSession = () => localStorage.removeItem(KEY);
export const stripQuery = (p: string) => p;

async function request<T>(base: string, path: string, init: RequestInit = {}, auth = true): Promise<T> {
  const s = loadSession();
  const res = await fetch(`${base}${path}`, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...(auth && s ? { Authorization: `Bearer ${s.token}` } : {}), ...(init.headers || {}) },
  });
  if (!res.ok) {
    let detail = `${res.status} ${res.statusText}`;
    try { const b = await res.json() as { detail?: string }; if (b?.detail) detail = String(b.detail); } catch {}
    throw new Error(detail);
  }
  if (res.status === 204) return undefined as T;
  const ct = res.headers.get('content-type') ?? '';
  if (!ct.includes('application/json')) return (await res.text()) as unknown as T;
  return (await res.json()) as T;
}
export const api = <T>(path: string, init: RequestInit = {}, auth = true) => request<T>(API, path, init, auth);
export const root = <T>(path: string, init: RequestInit = {}, auth = true) => request<T>(ROOT, path, init, auth);
export const csvUrl = (path: string) => `${API}${path}`;

export type Row = Record<string, unknown>;
export const money = (v: unknown) => Number(v ?? 0).toLocaleString('en-IN', { style: 'currency', currency: 'INR' });
export const dateShort = (v: unknown) => (typeof v === 'string' ? v.slice(0, 10) : String(v ?? ''));
