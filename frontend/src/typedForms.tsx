import React, { useEffect, useMemo, useState } from 'react';
import { api, money, type Row } from './api';
import { ErrorNote, Field, Select, Toast } from './ui';

const CID = () => {
  try { return (JSON.parse(localStorage.getItem('peaops.session.v1') ?? '{}') as { companyId?: number }).companyId ?? 1; } catch { return 1; }
};

export type TypedFormKind = 'ar-invoice' | 'ap-invoice' | 'party' | 'payment' | 'journal' | 'lead' | 'opportunity';
type Props = { kind: TypedFormKind; onDone: (msg: string) => void };

const num = (v: string) => Number(v || 0);

function useResource<T extends Row>(path: string): T[] {
  const [rows, setRows] = useState<T[]>([]);
  useEffect(() => { void api<T[]>(`${path}${path.includes('?') ? '&' : '?'}company_id=${CID()}`).then(setRows).catch(() => setRows([])); }, [path]);
  return rows;
}

function Shell({ title, error, msg, onSubmit, busy, children }: { title: string; error: string; msg: string; onSubmit: () => void; busy: boolean; children: React.ReactNode }) {
  return (
    <section className="panel typedForm">
      <p className="eyebrow">GUIDED FORM</p>
      <h2>{title}</h2>
      {error && <ErrorNote e={error} />}{msg && <Toast msg={msg} />}
      {children}
      <div className="formActions"><button className="primary" disabled={busy} onClick={onSubmit}>{busy ? 'Saving…' : 'Save'}</button></div>
    </section>
  );
}

function InvoiceForm({ type, onDone }: { type: 'ar' | 'ap'; onDone: (m: string) => void }) {
  const parties = useResource<Row>('/parties');
  const [partyId, setPartyId] = useState('');
  const [dueDate, setDueDate] = useState(() => new Date(Date.now() + 30 * 864e5).toISOString().slice(0, 10));
  const [lines, setLines] = useState([{ description: 'Consulting services', quantity: '10', unit_price: '25000', tax_rate: '18' }]);
  const [error, setError] = useState(''); const [msg, setMsg] = useState(''); const [busy, setBusy] = useState(false);
  const invoiceType: 'ar' | 'ap' = type;
  const filtered = parties.filter(p => (invoiceType === 'ar' ? p.party_type === 'customer' : p.party_type === 'supplier'));
  useEffect(() => { if (!partyId && filtered.length) setPartyId(String(filtered[0].id)); }, [filtered.length]); // eslint-disable-line
  const totals = useMemo(() => lines.reduce((acc, l) => { const net = num(l.quantity) * num(l.unit_price); const tax = net * num(l.tax_rate) / 100; return { net: acc.net + net, tax: acc.tax + tax }; }, { net: 0, tax: 0 }), [lines]);
  const submit = async () => {
    setBusy(true); setError(''); setMsg('');
    try {
      const today = new Date().toISOString().slice(0, 10);
      const r = await api<Row>('/invoices', { method: 'POST', body: JSON.stringify({ company_id: CID(), party_id: Number(partyId), invoice_type: invoiceType, invoice_date: today, due_date: dueDate, lines: lines.map(l => ({ description: l.description, quantity: num(l.quantity), unit_price: num(l.unit_price), tax_rate: num(l.tax_rate) })) }) });
      const m = `Invoice ${String(r.number)} created (draft)`; setMsg(m); onDone(m);
    } catch (e) { setError(e instanceof Error ? e.message : 'Failed'); } finally { setBusy(false); }
  };
  return (
    <Shell title={invoiceType === 'ar' ? 'New customer invoice' : 'New vendor bill'} error={error} msg={msg} onSubmit={submit} busy={busy}>
      <div className="formGrid">
        <Select label={invoiceType === 'ar' ? 'Customer' : 'Supplier'} value={partyId} onChange={setPartyId} options={filtered.map(p => [String(p.id), String(p.name)])} />
        <Field label="Due date" type="date" value={dueDate} onChange={setDueDate} />
      </div>
      <div className="lineTableHead"><span>Description</span><span>Qty</span><span>Unit price</span><span>Tax %</span><span></span></div>
      {lines.map((l, i) => (
        <div className="lineRow" key={i}>
          <input value={l.description} placeholder="Description" onChange={e => setLines(ls => ls.map((x, j) => j === i ? { ...x, description: e.target.value } : x))} />
          <input type="number" min="0" step="any" value={l.quantity} onChange={e => setLines(ls => ls.map((x, j) => j === i ? { ...x, quantity: e.target.value } : x))} />
          <input type="number" min="0" step="any" value={l.unit_price} onChange={e => setLines(ls => ls.map((x, j) => j === i ? { ...x, unit_price: e.target.value } : x))} />
          <input type="number" min="0" max="100" value={l.tax_rate} onChange={e => setLines(ls => ls.map((x, j) => j === i ? { ...x, tax_rate: e.target.value } : x))} />
          <button className="textBtn" onClick={() => setLines(ls => ls.length > 1 ? ls.filter((_, j) => j !== i) : ls)}>✕</button>
        </div>
      ))}
      <button className="ghost small" onClick={() => setLines(ls => [...ls, { description: '', quantity: '1', unit_price: '0', tax_rate: '18' }])}>+ Add line</button>
      <div className="totals"><span>Subtotal: <b>{money(totals.net)}</b></span><span>Tax: <b>{money(totals.tax)}</b></span><span className="grand">Total: <b>{money(totals.net + totals.tax)}</b></span></div>
    </Shell>
  );
}

function PartyForm({ onDone }: { onDone: (m: string) => void }) {
  const [partyType, setPartyType] = useState<'customer' | 'supplier'>('customer');
  const [code, setCode] = useState(''); const [name, setName] = useState(''); const [gstin, setGstin] = useState(''); const [credit, setCredit] = useState('100000');
  const [error, setError] = useState(''); const [msg, setMsg] = useState(''); const [busy, setBusy] = useState(false);
  const submit = async () => {
    setBusy(true); setError(''); setMsg('');
    try { const r = await api<Row>('/parties', { method: 'POST', body: JSON.stringify({ company_id: CID(), party_type: partyType, code, name, gstin: gstin || null, credit_limit: num(credit) }) }); const m = `${partyType === 'customer' ? 'Customer' : 'Supplier'} ${String(r.code)} created`; setMsg(m); onDone(m); setCode(''); setName(''); } catch (e) { setError(e instanceof Error ? e.message : 'Failed'); } finally { setBusy(false); }
  };
  return (
    <Shell title="New party" error={error} msg={msg} onSubmit={submit} busy={busy}>
      <div className="formGrid">
        <Select label="Party type" value={partyType} onChange={v => setPartyType(v as 'customer' | 'supplier')} options={[['customer', 'Customer'], ['supplier', 'Supplier']]} />
        <Field label="Code" value={code} onChange={setCode} required placeholder="CUST-002" />
        <Field label="Name" value={name} onChange={setName} required placeholder="Acme Retail Pvt Ltd" />
        <Field label="GSTIN (optional)" value={gstin} onChange={setGstin} placeholder="22AAAAA0000A1Z5" />
        <Field label="Credit limit (₹)" type="number" value={credit} onChange={setCredit} />
      </div>
    </Shell>
  );
}

function PaymentForm({ onDone }: { onDone: (m: string) => void }) {
  const parties = useResource<Row>('/parties');
  const [paymentType, setPaymentType] = useState<'receipt' | 'payment'>('receipt');
  const [partyId, setPartyId] = useState(''); const [reference, setReference] = useState('RCT-0002'); const [amount, setAmount] = useState('');
  const [error, setError] = useState(''); const [msg, setMsg] = useState(''); const [busy, setBusy] = useState(false);
  const filtered = parties.filter(p => (paymentType === 'receipt' ? p.party_type === 'customer' : p.party_type === 'supplier'));
  useEffect(() => { if (!partyId && filtered.length) setPartyId(String(filtered[0].id)); }, [filtered.length]); // eslint-disable-line
  const submit = async () => {
    setBusy(true); setError(''); setMsg('');
    try { const r = await api<Row>('/payments', { method: 'POST', body: JSON.stringify({ company_id: CID(), party_id: Number(partyId), payment_type: paymentType, reference, payment_date: new Date().toISOString().slice(0, 10), amount: num(amount) }) }); const m = `Payment ${String(r.reference)} recorded — allocate it next`; setMsg(m); onDone(m); setAmount(''); } catch (e) { setError(e instanceof Error ? e.message : 'Failed'); } finally { setBusy(false); }
  };
  return (
    <Shell title={paymentType === 'receipt' ? 'Record customer receipt' : 'Record vendor payment'} error={error} msg={msg} onSubmit={submit} busy={busy}>
      <div className="formGrid">
        <Select label="Payment type" value={paymentType} onChange={v => setPaymentType(v as 'receipt' | 'payment')} options={[['receipt', 'Receipt (money in)'], ['payment', 'Payment (money out)']]} />
        <Select label={paymentType === 'receipt' ? 'Customer' : 'Supplier'} value={partyId} onChange={setPartyId} options={filtered.map(p => [String(p.id), String(p.name)])} />
        <Field label="Reference" value={reference} onChange={setReference} required />
        <Field label="Amount (₹)" type="number" value={amount} onChange={setAmount} required placeholder="295000" />
      </div>
    </Shell>
  );
}

function JournalForm({ onDone }: { onDone: (m: string) => void }) {
  const accounts = useResource<Row>('/accounts');
  const [reference, setReference] = useState('JV-0001'); const [description, setDescription] = useState('Month-end accrual');
  const [lines, setLines] = useState([{ account_id: '', debit: '0', credit: '0', memo: '' }, { account_id: '', debit: '0', credit: '0', memo: '' }]);
  const [error, setError] = useState(''); const [msg, setMsg] = useState(''); const [busy, setBusy] = useState(false);
  const totals = useMemo(() => lines.reduce((acc, l) => ({ debit: acc.debit + num(l.debit), credit: acc.credit + num(l.credit) }), { debit: 0, credit: 0 }), [lines]);
  const balanced = totals.debit === totals.credit && totals.debit > 0;
  const submit = async () => {
    setBusy(true); setError(''); setMsg('');
    try { const r = await api<Row>('/journal-entries', { method: 'POST', body: JSON.stringify({ company_id: CID(), reference, description, lines: lines.map(l => ({ account_id: Number(l.account_id), memo: l.memo, debit: num(l.debit), credit: num(l.credit) })) }) }); const m = `Journal ${String(r.reference)} created (draft)`; setMsg(m); onDone(m); } catch (e) { setError(e instanceof Error ? e.message : 'Failed'); } finally { setBusy(false); }
  };
  return (
    <Shell title="New journal entry" error={error} msg={msg} onSubmit={submit} busy={busy}>
      <div className="formGrid"><Field label="Reference" value={reference} onChange={setReference} required /><Field label="Description" value={description} onChange={setDescription} required /></div>
      <div className="lineTableHead journal"><span>Account</span><span>Debit</span><span>Credit</span><span>Memo</span></div>
      {lines.map((l, i) => (
        <div className="lineRow journal" key={i}>
          <select value={l.account_id} onChange={e => setLines(ls => ls.map((x, j) => j === i ? { ...x, account_id: e.target.value } : x))}>
            <option value="">Select account…</option>
            {accounts.map(a => <option key={String(a.id)} value={String(a.id)}>{String(a.code)} — {String(a.name)}</option>)}
          </select>
          <input type="number" min="0" step="any" value={l.debit} onChange={e => setLines(ls => ls.map((x, j) => j === i ? { ...x, debit: e.target.value, credit: '0' } : x))} />
          <input type="number" min="0" step="any" value={l.credit} onChange={e => setLines(ls => ls.map((x, j) => j === i ? { ...x, credit: e.target.value, debit: '0' } : x))} />
          <input value={l.memo} onChange={e => setLines(ls => ls.map((x, j) => j === i ? { ...x, memo: e.target.value } : x))} />
        </div>
      ))}
      <button className="ghost small" onClick={() => setLines(ls => [...ls, { account_id: '', debit: '0', credit: '0', memo: '' }])}>+ Add line</button>
      <div className={balanced ? 'totals ok' : 'totals bad'}><span>Debits: <b>{money(totals.debit)}</b></span><span>Credits: <b>{money(totals.credit)}</b></span><span className="grand">{balanced ? 'Balanced ✓' : 'Unbalanced — adjust lines'}</span></div>
    </Shell>
  );
}

function LeadForm({ onDone }: { onDone: (m: string) => void }) {
  const [name, setName] = useState(''); const [email, setEmail] = useState(''); const [phone, setPhone] = useState(''); const [source, setSource] = useState('trade_show');
  const [error, setError] = useState(''); const [msg, setMsg] = useState(''); const [busy, setBusy] = useState(false);
  const submit = async () => {
    setBusy(true); setError(''); setMsg('');
    try { const r = await api<Row>('/leads', { method: 'POST', body: JSON.stringify({ company_id: CID(), name, email: email || null, phone: phone || null, source, owner: 'admin' }) }); const m = `Lead "${String(r.name)}" added`; setMsg(m); onDone(m); setName(''); setEmail(''); } catch (e) { setError(e instanceof Error ? e.message : 'Failed'); } finally { setBusy(false); }
  };
  return (
    <Shell title="New lead" error={error} msg={msg} onSubmit={submit} busy={busy}>
      <div className="formGrid">
        <Field label="Name" value={name} onChange={setName} required placeholder="Priya Sharma — Procurement Head" />
        <Field label="Email" type="email" value={email} onChange={setEmail} placeholder="priya@example.com" />
        <Field label="Phone" value={phone} onChange={setPhone} placeholder="+91 98765 43210" />
        <Select label="Source" value={source} onChange={setSource} options={[['trade_show', 'Trade show'], ['referral', 'Referral'], ['website', 'Website'], ['outbound', 'Outbound']]} />
      </div>
    </Shell>
  );
}

function OpportunityForm({ onDone }: { onDone: (m: string) => void }) {
  const parties = useResource<Row>('/parties');
  const [title, setTitle] = useState(''); const [customerId, setCustomerId] = useState(''); const [amount, setAmount] = useState(''); const [stage, setStage] = useState('proposal'); const [probability, setProbability] = useState('60');
  const [error, setError] = useState(''); const [msg, setMsg] = useState(''); const [busy, setBusy] = useState(false);
  const customers = parties.filter(p => p.party_type === 'customer');
  useEffect(() => { if (!customerId && customers.length) setCustomerId(String(customers[0].id)); }, [customers.length]); // eslint-disable-line
  const submit = async () => {
    setBusy(true); setError(''); setMsg('');
    try { const r = await api<Row>('/opportunities', { method: 'POST', body: JSON.stringify({ company_id: CID(), customer_id: customerId ? Number(customerId) : null, title, stage, amount: num(amount), probability: num(probability) }) }); const m = `Opportunity "${String(r.title)}" opened`; setMsg(m); onDone(m); setTitle(''); setAmount(''); } catch (e) { setError(e instanceof Error ? e.message : 'Failed'); } finally { setBusy(false); }
  };
  return (
    <Shell title="New opportunity" error={error} msg={msg} onSubmit={submit} busy={busy}>
      <div className="formGrid">
        <Field label="Title" value={title} onChange={setTitle} required placeholder="ACME — annual support renewal" />
        <Select label="Customer" value={customerId} onChange={setCustomerId} options={customers.map(p => [String(p.id), String(p.name)])} />
        <Field label="Expected amount (₹)" type="number" value={amount} onChange={setAmount} placeholder="1500000" />
        <Select label="Stage" value={stage} onChange={setStage} options={[['prospecting', 'Prospecting'], ['qualification', 'Qualification'], ['proposal', 'Proposal'], ['negotiation', 'Negotiation'], ['won', 'Won']]} />
        <Field label="Probability %" type="number" value={probability} onChange={setProbability} />
      </div>
    </Shell>
  );
}

export default function TypedForm({ kind, onDone }: Props) {
  switch (kind) {
    case 'ar-invoice': return <InvoiceForm type="ar" onDone={onDone} />;
    case 'ap-invoice': return <InvoiceForm type="ap" onDone={onDone} />;
    case 'party': return <PartyForm onDone={onDone} />;
    case 'payment': return <PaymentForm onDone={onDone} />;
    case 'journal': return <JournalForm onDone={onDone} />;
    case 'lead': return <LeadForm onDone={onDone} />;
    case 'opportunity': return <OpportunityForm onDone={onDone} />;
  }
}
