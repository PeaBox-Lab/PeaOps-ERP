import React, { useState } from 'react';
import { loadSession } from '../api';

export default function AddCompanyForm({ onDone }: { onDone?: (msg: string) => void }) {
  const [code, setCode] = useState(''); const [name, setName] = useState(''); const [currency, setCurrency] = useState('INR'); const [username, setUsername] = useState('admin'); const [display, setDisplay] = useState('Company Administrator');
  const [busy, setBusy] = useState(false); const [error, setError] = useState(''); const [result, setResult] = useState<Record<string, unknown> | null>(null);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault(); setBusy(true); setError(''); setResult(null);
    const session = loadSession();
    if (!session) { setError('Session expired'); setBusy(false); return; }
    try {
      const res = await fetch('/api/v1/admin/companies/provision', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${session.token}` },
        body: JSON.stringify({ code: code.toUpperCase().trim(), name: name.trim(), base_currency: currency.toUpperCase().trim(), admin_username: username.trim().toLowerCase() || 'admin', admin_display_name: display.trim() || 'Company Administrator' }),
      });
      const data = await res.json() as Record<string, unknown>;
      if (!res.ok) throw new Error((data as { detail?: string })?.detail ?? 'Create failed');
      setResult(data);
      onDone?.(`Created company ${String(data.code)} with admin ${String(data.admin_username)}`);
    } catch (err) { setError(err instanceof Error ? err.message : 'Create failed'); } finally { setBusy(false); }
  };

  return (
    <section className="panel typedForm">
      <p className="eyebrow">SUPER-ADMIN</p>
      <h2>Add a new company</h2>
      <p className="muted">Creates the company, COA, fiscal periods, posting profiles, SMTP placeholder, warehouse, and number sequences. A strong admin password is generated and shown once.</p>
      {error && <p className="error">{error}</p>}
      {result && (
        <div className="panel" style={{ background: '#def3e8', border: '1px solid #9edcc4' }}>
          <p className="eyebrow">CREDENTIALS — copy now</p>
          <p><b>Company:</b> {String(result.code)} — {String(result.name)}</p>
          <p><b>Admin user:</b> {String(result.admin_username)}</p>
          <p><b>Admin password:</b> <code style={{ userSelect: 'all' }}>{String(result.admin_password)}</code></p>
          <p className="muted">You won't see this password again. Share it securely, sign in at <code>/{String(result.id)}</code> using the login form, change it immediately.</p>
        </div>
      )}
      <form onSubmit={submit} className="formGrid">
        <label className="field"><span>Company code</span><input value={code} onChange={e => setCode(e.target.value)} required placeholder="BETA" maxLength={20} pattern="[A-Za-z0-9_-]+" /></label>
        <label className="field"><span>Company name</span><input value={name} onChange={e => setName(e.target.value)} required placeholder="Beta Exports Ltd" minLength={2} /></label>
        <label className="field"><span>Base currency</span><select value={currency} onChange={e => setCurrency(e.target.value)}><option>INR</option><option>USD</option><option>EUR</option><option>GBP</option><option>AED</option><option>SGD</option></select></label>
        <label className="field"><span>Admin username</span><input value={username} onChange={e => setUsername(e.target.value)} required placeholder="admin" minLength={3} /></label>
        <label className="field"><span>Admin display name</span><input value={display} onChange={e => setDisplay(e.target.value)} placeholder="Company Administrator" /></label>
        <button className="primary" disabled={busy} type="submit">{busy ? 'Creating…' : 'Create company'}</button>
      </form>
    </section>
  );
}
