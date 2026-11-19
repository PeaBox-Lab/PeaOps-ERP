import React, { useEffect, useState } from 'react';
import { api, type Row } from './api';
import { ErrorNote, Field, Select, Toast } from './ui';

const CID = () => {
  try { return (JSON.parse(localStorage.getItem('peaops.session.v1') ?? '{}') as { companyId?: number }).companyId ?? 1; } catch { return 1; }
};
const today = () => new Date().toISOString().slice(0, 10);

export type FieldSpec = {
  key: string; label: string;
  type?: 'text' | 'number' | 'date' | 'select' | 'textarea' | 'checkbox' | 'password';
  required?: boolean; def?: string; placeholder?: string;
  options?: Array<[string, string]>;
  optionsFrom?: { path: string; value: string; label: string; filterKey?: string; filterValue?: string };
  asNumber?: boolean; min?: number; max?: number; step?: string;
};
export type LineSpec = { key: string; label: string; type?: 'text' | 'number' | 'select'; required?: boolean; def?: string; placeholder?: string; optionsFrom?: { path: string; value: string; label: string; filterKey?: string; filterValue?: string }; asNumber?: boolean };
export type FormSpec = {
  title: string;
  fields: FieldSpec[];
  lines?: { key: string; label: string; addLabel?: string; minRows?: number; columns: LineSpec[] };
  transform?: (payload: Record<string, unknown>) => Record<string, unknown>;
};

const num = (v: string) => Number(v || 0);

function useRemoteOptions(fields: FieldSpec[]) {
  const [cache, setCache] = useState<Record<string, Array<[string, string]>>>({});
  useEffect(() => {
    const wanted = fields.filter(f => f.optionsFrom);
    if (!wanted.length) return;
    let cancelled = false;
    (async () => {
      const out: Record<string, Array<[string, string]>> = {};
      for (const f of wanted) {
        const spec = f.optionsFrom!;
        try {
          const rows = await api<Array<Record<string, unknown>>>(spec.path);
          let filtered = rows as Array<Record<string, unknown>>;
          if (spec.filterKey) filtered = filtered.filter(r => String(r[spec.filterKey!]).toLowerCase() === String(spec.filterValue).toLowerCase());
          out[f.key] = filtered.map(r => [String(r[spec.value]), String(r[spec.label])] as [string, string]);
        } catch { out[f.key] = []; }
      }
      if (!cancelled) setCache(out);
    })();
    return () => { cancelled = true; };
  }, [fields]);
  return cache;
}

function useLineRemoteOptions(columns: LineSpec[] | undefined) {
  const [cache, setCache] = useState<Record<string, Array<[string, string]>>>({});
  useEffect(() => {
    const wanted = (columns ?? []).filter(c => c.optionsFrom);
    if (!wanted.length) return;
    let cancelled = false;
    (async () => {
      const out: Record<string, Array<[string, string]>> = {};
      for (const c of wanted) {
        const spec = c.optionsFrom!;
        try {
          const rows = await api<Array<Record<string, unknown>>>(spec.path);
          let filtered = rows as Array<Record<string, unknown>>;
          if (spec.filterKey) filtered = filtered.filter(r => String(r[spec.filterKey!]).toLowerCase() === String(spec.filterValue).toLowerCase());
          out[c.key] = filtered.map(r => [String(r[spec.value]), String(r[spec.label])] as [string, string]);
        } catch { out[c.key] = []; }
      }
      if (!cancelled) setCache(out);
    })();
    return () => { cancelled = true; };
  }, [columns]);
  return cache;
}

export default function SpecForm({ spec, resolvePath, recordId, onDone }: { spec: FormSpec; resolvePath: (recordId: string) => string; recordId?: boolean; onDone: (msg: string) => void }) {
  const [values, setValues] = useState<Record<string, string>>(() => Object.fromEntries(spec.fields.map(f => [f.key, f.def ?? (f.type === 'date' ? today() : f.type === 'checkbox' ? 'false' : '')])));
  const [lineRows, setLineRows] = useState<Array<Record<string, string>>>(() => (spec.lines ? Array.from({ length: spec.lines.minRows ?? 1 }, () => Object.fromEntries(spec.lines!.columns.map(c => [c.key, c.def ?? '']))) : []));
  const [record, setRecord] = useState('1');
  const [error, setError] = useState(''); const [msg, setMsg] = useState(''); const [busy, setBusy] = useState(false);
  const remote = useRemoteOptions(spec.fields);
  const lineRemote = useLineRemoteOptions(spec.lines?.columns);
  // Pre-select the first remote option for required selects that have no value yet.
  useEffect(() => {
    const patch: Record<string, string> = {};
    for (const f of spec.fields) {
      if (f.optionsFrom && !values[f.key]) {
        const first = remote[f.key]?.[0];
        if (first) patch[f.key] = first[0];
      }
    }
    if (Object.keys(patch).length) setValues(s => ({ ...s, ...patch }));
  }, [remote]); // eslint-disable-line
  // Pre-select the first line remote option for each required/placeholder line field that is blank.
  useEffect(() => {
    const patch: Record<number, Record<string, string>> = {};
    for (let i = 0; i < lineRows.length; i++) {
      const row = lineRows[i];
      for (const c of spec.lines?.columns ?? []) {
        if (c.optionsFrom && !row[c.key]) {
          const first = lineRemote[c.key]?.[0];
          if (first) {
            patch[i] = patch[i] ?? {};
            patch[i][c.key] = first[0];
          }
        }
      }
    }
    if (Object.keys(patch).length) setLineRows(rows => rows.map((r, i) => patch[i] ? { ...r, ...patch[i] } : r));
  }, [lineRemote]); // eslint-disable-line

  const set = (k: string, v: string) => setValues(s => ({ ...s, [k]: v }));
  const setLine = (i: number, k: string, v: string) => setLineRows(rows => rows.map((r, j) => j === i ? { ...r, [k]: v } : r));
  const addLine = () => setLineRows(rows => [...rows, Object.fromEntries(spec.lines!.columns.map(c => [c.key, c.def ?? '']))]);
  const removeLine = (i: number) => setLineRows(rows => rows.length > (spec.lines?.minRows ?? 1) ? rows.filter((_, j) => j !== i) : rows);

  const submit = async () => {
    setBusy(true); setError(''); setMsg('');
    try {
      const payload: Record<string, unknown> = { company_id: CID() };
      for (const f of spec.fields) {
        const v = values[f.key];
        if (f.required && !v.trim()) throw new Error(`${f.label} is required`);
        if (!v.trim() && !f.required) continue;
        if (f.type === 'number' || f.asNumber) payload[f.key] = num(v);
        else if (f.type === 'checkbox') payload[f.key] = v === 'true';
        else payload[f.key] = v;
      }
      if (spec.lines) {
        payload[spec.lines.key] = lineRows.map(r => {
          const line: Record<string, unknown> = {};
          for (const c of spec.lines!.columns) {
            if (!Object.prototype.hasOwnProperty.call(r, c.key)) continue;
            const coerce = c.asNumber || c.type === 'number';
            line[c.key] = coerce ? num(r[c.key]) : r[c.key];
          }
          return line;
        });
      }
      if (spec.transform) Object.assign(payload, spec.transform(payload));
      const path = resolvePath(record);
      const res = await api<Row>(path, { method: 'POST', body: JSON.stringify(payload) });
      if (res && typeof res === 'object' && typeof (res as Record<string, unknown>).mailto === 'string') {
        const mailto = String((res as Record<string, unknown>).mailto);
        const m = 'SMTP not configured — opening your mail client…'; setMsg(m); onDone(m); window.open(mailto, '_self'); return;
      }
      const m = msgFor(res, path); setMsg(m); onDone(m);
    } catch (e) { setError(e instanceof Error ? e.message : 'Failed'); } finally { setBusy(false); }
  };

  return (
    <section className="panel typedForm">
      <p className="eyebrow">GUIDED FORM</p>
      <h2>{spec.title}</h2>
      {error && <ErrorNote e={error} />}{msg && <Toast msg={msg} />}
      {recordId && <Field label="Record ID" value={record} onChange={setRecord} required />}
      <div className="formGrid">
        {spec.fields.map(f => {
          const opts = f.options ?? remote[f.key];
          if (f.type === 'select' || f.optionsFrom) return <Select key={f.key} label={f.label} value={values[f.key]} onChange={v => set(f.key, v)} options={opts ?? []} />;
          if (f.type === 'textarea') return <label key={f.key} className="field wide"><span>{f.label}</span><textarea className="jsonArea small" rows={3} value={values[f.key]} onChange={e => set(f.key, e.target.value)} /></label>;
          if (f.type === 'checkbox') return <label key={f.key} className="checkField"><input type="checkbox" checked={values[f.key] === 'true'} onChange={e => set(f.key, String(e.target.checked))} /><span>{f.label}</span></label>;
          return <Field key={f.key} label={f.label} type={f.type ?? 'text'} value={values[f.key]} onChange={v => set(f.key, v)} required={f.required} placeholder={f.placeholder} min={f.min} max={f.max} step={f.step} />;
        })}
      </div>
      {spec.lines && (
        <>
          <p className="eyebrow" style={{ marginTop: 16 }}>{spec.lines.label}</p>
          <div className="lineTableHead" style={{ gridTemplateColumns: `repeat(${spec.lines.columns.length}, 1fr) 34px` }}>{spec.lines.columns.map(c => <span key={c.key}>{c.label}</span>)}<span /></div>
          {lineRows.map((row, i) => (
            <div className="lineRow" key={i} style={{ gridTemplateColumns: `repeat(${spec.lines!.columns.length}, 1fr) 34px` }}>
              {spec.lines!.columns.map(c => {
                const opts = c.optionsFrom ? lineRemote[c.key] : undefined;
                if (c.optionsFrom) {
                  return (
                    <select key={c.key} value={row[c.key]} onChange={e => setLine(i, c.key, e.target.value)} required={c.required}>
                      {(opts ?? []).map(([v, l]) => <option key={v} value={v}>{l}</option>)}
                    </select>
                  );
                }
                return <input key={c.key} type={c.type === 'number' ? 'number' : 'text'} step="any" placeholder={c.placeholder ?? c.label} value={row[c.key]} onChange={e => setLine(i, c.key, e.target.value)} />;
              })}
              <button className="textBtn" onClick={() => removeLine(i)}>✕</button>
            </div>
          ))}
          <button className="ghost small" onClick={addLine}>+ {spec.lines.addLabel ?? 'Add row'}</button>
        </>
      )}
      <div className="formActions"><button className="primary" disabled={busy} onClick={() => void submit()}>{busy ? 'Saving…' : 'Submit'}</button></div>
    </section>
  );
}

function msgFor(res: unknown, path: string): string {
  const r = res as Record<string, unknown> | null;
  if (!r) return `OK — server accepted ${path}`;
  const id = r.id ?? r.number ?? r['id'];
  return id ? `Saved (id/number: ${String(id)})` : 'Saved successfully';
}
