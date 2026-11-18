import React from 'react';

export type BarDatum = { label: string; value: number };

export function HorizontalBarChart({ data, format = (n) => n.toLocaleString('en-IN'), maxRows = 8 }: { data: BarDatum[]; format?: (n: number) => string; maxRows?: number }) {
  const rows = data.slice(0, maxRows);
  const max = Math.max(...rows.map(r => Math.abs(r.value)), 1);
  if (rows.length === 0) return <p className="muted">Nothing to chart yet.</p>;
  return (
    <div className="barChart">
      {rows.map(r => (
        <div className="barRow" key={r.label}>
          <span className="barLabel" title={r.label}>{r.label}</span>
          <div className="barTrack"><div className="barFill" style={{ width: `${Math.max((Math.abs(r.value) / max) * 100, 2)}%` }} /></div>
          <span className="barValue">{format(r.value)}</span>
        </div>
      ))}
    </div>
  );
}

export function Donut({ parts }: { parts: Array<{ label: string; value: number; color: string }> }) {
  const total = parts.reduce((s, p) => s + p.value, 0) || 1;
  let acc = 0;
  const R = 70, C = 2 * Math.PI * R;
  return (
    <svg viewBox="0 0 200 200" className="donut" role="img" aria-label="Distribution chart">
      <circle cx="100" cy="100" r={R} fill="none" stroke="#eef1ef" strokeWidth="26" />
      {parts.filter(p => p.value > 0).map(p => {
        const frac = p.value / total;
        const dash = frac * C;
        const el = (
          <circle key={p.label} cx="100" cy="100" r={R} fill="none" stroke={p.color} strokeWidth="26"
            strokeDasharray={`${dash} ${C - dash}`} strokeDashoffset={-acc * C}
            transform="rotate(-90 100 100)" strokeLinecap="butt" />
        );
        acc += frac;
        return el;
      })}
      <text x="100" y="96" textAnchor="middle" className="donutCenter">{Math.round(total).toLocaleString('en-IN')}</text>
      <text x="100" y="114" textAnchor="middle" className="donutSub">TOTAL</text>
    </svg>
  );
}

export const CHART_COLORS = ['#197357', '#3b81bd', '#7869bd', '#d49135', '#b56718', '#279671', '#a33e32', '#2f5e8f'];
