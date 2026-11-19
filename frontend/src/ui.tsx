import React from 'react';

export const short = (v: unknown): string => {
  if (v === null || v === undefined) return '';
  if (typeof v === 'object') { const s = JSON.stringify(v); return s.length > 80 ? `${s.slice(0, 80)}…` : s; }
  return String(v);
};

export function EmptyState({ title, help }: { title: string; help?: string }) {
  return (
    <div className="emptyState">
      <p className="eyebrow">NOTHING</p>
      <h3>{title}</h3>
      <p className="muted">{help ?? 'Switch to the Create tab to get started, or load the demo dataset from the Administration module.'}</p>
    </div>
  );
}

export function DataTable({ rows, loading, empty = 'No rows' }: { rows: Array<Record<string, unknown>> | null; loading: boolean; empty?: string }) {
  if (loading) return <p className="muted">Loading…</p>;
  if (!rows) return null;
  if (rows.length === 0) return <EmptyState title={empty} />;
  const keys = Object.keys(rows[0]);
  const [filter, setFilter] = React.useState('');
  const [sortKey, setSortKey] = React.useState<string | null>(null);
  const [sortDir, setSortDir] = React.useState<'asc' | 'desc'>('asc');
  const visible = React.useMemo(() => {
    let out = rows.filter(r => Object.values(r).some(v => String(v ?? '').toLowerCase().includes(filter.toLowerCase())));
    if (sortKey) out = [...out].sort((a, b) => {
      const av = a[sortKey], bv = b[sortKey];
      const cmp = String(av ?? '').localeCompare(String(bv ?? ''), undefined, { numeric: true });
      return sortDir === 'asc' ? cmp : -cmp;
    });
    return out;
  }, [rows, filter, sortKey, sortDir]);
  return (
    <div className="tableWrap">
      <div className="tableTools"><input placeholder="Filter rows…" value={filter} onChange={e => setFilter(e.target.value)} />{sortKey && <button className="ghost small" onClick={() => { setSortKey(null); setSortDir('asc'); }}>Clear sort ({sortKey})</button>}</div>
      <table className="table">
        <thead><tr>{keys.map(k => <th key={k}><button className="thSort" onClick={() => { if (sortKey === k) setSortDir(d => d === 'asc' ? 'desc' : 'asc'); else { setSortKey(k); setSortDir('asc'); } }}>{k}{sortKey === k ? sortDir === 'asc' ? ' ▲' : ' ▼' : ' ↕'}</button></th>)}</tr></thead>
        <tbody>{visible.map((r, i) => <tr key={i}>{keys.map(k => <td key={k}>{/status|outcome/i.test(k) ? <Pill v={r[k]} /> : short(r[k])}</td>)}</tr>)}</tbody>
      </table>
    </div>
  );
}

export const tone = (v: unknown) => {
  const s = String(v ?? '').toLowerCase();
  if (/(posted|approved|completed|paid|ready|healthy|resolved|success|live|open|sent)/.test(s)) return 'ok';
  if (/(draft|pending|processing|new|planning)/.test(s)) return 'info';
  if (/(partial|warning|medium)/.test(s)) return 'warn';
  if (/(void|blocked|denied|error|failed|locked)/.test(s)) return 'danger';
  return '';
};

export const Pill = ({ v }: { v: unknown }) => <span className={`pill ${tone(v)}`}>{short(v)}</span>;

export const Field = ({ label, value, onChange, placeholder, required, type, min, max, step }: { label: string; value: string; onChange: (v: string) => void; placeholder?: string; required?: boolean; type?: string; min?: number; max?: number; step?: string }) => (
  <label className="field"><span>{label}</span><input type={type ?? 'text'} required={required} value={value} placeholder={placeholder} min={min} max={max} step={step} onChange={e => onChange(e.target.value)} /></label>
);

export const Select = ({ label, value, onChange, options }: { label: string; value: string; onChange: (v: string) => void; options: Array<[string, string]> }) => (
  <label className="field"><span>{label}</span><select value={value} onChange={e => onChange(e.target.value)}>{options.map(([v, l]) => <option key={v} value={v}>{l}</option>)}</select></label>
);

export const ErrorNote = ({ e }: { e: string }) => (e ? <div className="error">{e}</div> : null);

export const Toast = ({ msg }: { msg: string }) => (msg ? <div className="success">{msg}</div> : null);
