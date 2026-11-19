import { useEffect, useState } from 'react';
import { loadSession, saveSession, type Session } from '../api';

const API_ROOT = `${window.location.origin}/api`;

export function CompanySwitcher({ onSwitch }: { onSwitch: (s: Session) => void }) {
  const session = loadSession();
  const [companies, setCompanies] = useState<Array<{ id: number; code: string; name: string }>>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!session) return;
    fetch(`/api/v1/me/companies`, { headers: { Authorization: `Bearer ${session.token}` } })
      .then(r => r.json())
      .then((list: Array<{ id: number; code: string; name: string }>) => { if (!Array.isArray(list)) setError('Could not load companies'); else setCompanies(list); })
      .catch(() => setError('Could not load companies'));
  }, [session?.token]);

  const choose = async (companyId: number) => {
    if (!session || busy) return;
    if (companyId === session.companyId) return;
    setBusy(true); setError('');
    try {
      const res = await fetch(`/api/v1/auth/switch-company`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${session.token}` },
        body: JSON.stringify({ company_id: companyId }),
      });
      const data = await res.json() as { access_token: string; refresh_token: string; expires_in: number; permissions: string[]; company_id: number; company_name: string; must_change_password: boolean };
      if (!res.ok) throw new Error((data as { detail?: string })?.detail ?? 'Switch failed');
      const next: Session = {
        token: data.access_token,
        refresh: data.refresh_token,
        companyId: data.company_id,
        username: session.username,
        permissions: data.permissions,
        expiresAt: Date.now() + data.expires_in * 1000,
        mustChangePassword: !!data.must_change_password,
      };
      saveSession(next);
      onSwitch(next);
      window.location.href = '/';
    } catch (e) { setError(e instanceof Error ? e.message : 'Switch failed'); } finally { setBusy(false); }
  };

  if (!session || companies.length <= 1) return null;

  return (
    <div className="companySwitcher">
      <label className="eyebrow">Company</label>
      <select
        aria-label="Switch company"
        value={session.companyId}
        onChange={e => choose(Number(e.target.value))}
        disabled={busy}
      >
        {companies.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
      </select>
      {error && <p className="error" style={{ marginTop: 6 }}>{error}</p>}
    </div>
  );
}