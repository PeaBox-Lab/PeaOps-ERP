import React from 'react';

export const esc = (s: string) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;');

export const short = (v: unknown): string => {
  if (v === null || v === undefined) return '';
  if (typeof v === 'object') { const s = JSON.stringify(v); return s.length > 80 ? `${s.slice(0, 80)}…` : s; }
  return String(v);
};

export function DataTable({ rows, loading, empty = 'No rows' }: { rows: Array<Record<string, unknown>> | null; loading: boolean; empty?: string }) {
  if (loading) return <p className="muted">Loading…</p>;
  if (!rows) return null;
  if (rows.length === 0) return <p className="muted">{empty}</p>;
  const keys = Object.keys(rows[0]);
  return (
    <div className="tableWrap">
      <table className="table">
        <thead><tr>{keys.map(k => <th key={k}>{k}</th>)}</tr></thead>
        <tbody>{rows.map((r, i) => <tr key={i}>{keys.map(k => <td key={k}>{short(r[k])}</td>)}</tr>)}</tbody>
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
