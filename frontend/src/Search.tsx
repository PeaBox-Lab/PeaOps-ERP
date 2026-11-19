import React, { useEffect, useState } from 'react';

const API = import.meta.env.VITE_API_URL ?? '/api/v1';

export type Hit = { type: string; id: number; label: string; sub?: string };

export function SearchResults({ query }: { query: string }) {
  const [hits, setHits] = useState<Hit[] | null>(null);
  const [error, setError] = useState('');
  useEffect(() => {
    const q = (query || '').trim();
    if (q.length < 2) { setHits([]); return; }
    const token = (() => { try { const s = JSON.parse(localStorage.getItem('peaops.session.v1') ?? 'null') as { token?: string } | null; return s?.token ?? ''; } catch { return ''; } })();
    fetch(`${API}/search?company_id=${(() => { try { return (JSON.parse(localStorage.getItem('peaops.session.v1') ?? '{}') as { companyId?: number }).companyId ?? 1; } catch { return 1; } })()}&q=${encodeURIComponent(q)}&limit=20`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json())
      .then(d => setHits((d.hits as Hit[]) ?? []))
      .catch(e => setError(e instanceof Error ? e.message : 'Search failed'));
  }, [query]);

  const mapType = (t: string) => ({ invoice: 'Invoice', sales_order: 'Order', purchase_order: 'PO', sales_quote: 'Quote', party: 'Party', item: 'Item' }[t] ?? t);

  if (hits === null && !error) return <p className="muted">Searching…</p>;
  if (error) return <p className="error">{error}</p>;
  if (!hits || hits.length === 0) return <p className="muted">No results for “{query}”.</p>;

  return (<section className="panel"><div className="tableWrap"><table className="table"><thead><tr><th>Type</th><th>Reference</th><th>Detail</th></tr></thead><tbody>{hits.map((h, i) => <tr key={i}><td><span className="pill ok">{mapType(h.type)}</span></td><td>{h.label}</td><td className="muted">{h.sub ?? ''}</td></tr>)}</tbody></table></div></section>);
}

export function SearchBox({ onSubmit }: { onSubmit: (q: string) => void }) {
  const [q, setQ] = React.useState('');
  return (
    <form className="searchForm" onSubmit={e => { e.preventDefault(); const v = q.trim(); if (v.length >= 2) onSubmit(v); }}>
      <span className="searchIcon">⌕</span>
      <input aria-label="Search" placeholder="Search invoices, orders, parties, items…" value={q} onChange={e => setQ(e.target.value)} />
    </form>
  );
}
