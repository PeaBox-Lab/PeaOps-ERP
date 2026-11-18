
import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';
import { api, clearSession, loadSession, saveSession, money, type Session } from './api';
import { DataTable, ErrorNote, Field, Select, Toast, Pill } from './ui';
import TypedForm, { type TypedFormKind } from './typedForms';
import SpecForm, { type FormSpec } from './specForm';
import { HorizontalBarChart, Donut, CHART_COLORS } from './charts';

const CID = () => loadSession()?.companyId ?? 1;

/* ---------- generic endpoint page ---------- */
type Action = { label: string; path: (v: string) => string; body: string; method?: 'POST' | 'GET'; spec?: FormSpec };
type PageCfg = {
  id: string; title: string; getPath?: string; query?: boolean; empty?: string;
  post?: { label: string; path: string; body: string };
  form?: TypedFormKind;
  spec?: FormSpec;
  actions?: Action[]; note?: string;
};
type ModuleCfg = { id: string; label: string; icon: string; pages: PageCfg[] };

const json = (o: unknown) => JSON.stringify(o, null, 2);

function EntityPage({ page }: { page: PageCfg }) {
  const [rows, setRows] = useState<Array<Record<string, unknown>> | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(''); const [msg, setMsg] = useState('');
  const [createBody, setCreateBody] = useState(page.post?.body ?? '{}');
  const [actionValue, setActionValue] = useState('1'); const [actionIdx, setActionIdx] = useState(0);
  const [actionBody, setActionBody] = useState(page.actions?.[0]?.body ?? '{}');
  const [tab, setTab] = useState<'view' | 'create' | 'actions'>('view');

  const load = useCallback(async () => {
    if (!page.getPath) return;
    setLoading(true); setError('');
    try {
      const path = page.getPath.includes('?') ? `${page.getPath}&company_id=${CID()}` : `${page.getPath}?company_id=${CID()}`;
      const data = await api<unknown>(path);
      setRows(Array.isArray(data) ? data as Array<Record<string, unknown>> : [data as Record<string, unknown>]);
    } catch (err) { setError(err instanceof Error ? err.message : 'Failed'); }
    finally { setLoading(false); }
  }, [page.getPath]);

  useEffect(() => { void load(); }, [load]);
  useEffect(() => { setTab('view'); setActionIdx(0); setRows(null); setError(''); setMsg(''); setCreateBody(page.post?.body ?? '{}'); setActionBody(page.actions?.[0]?.body ?? '{}'); }, [page.id]);

  const runPost = async () => {
    if (!page.post) return; setError(''); setMsg('');
    try { const body = JSON.parse(createBody); const r = await api(page.post.path, { method: 'POST', body: JSON.stringify(body) }); setMsg(`Created: ${json(r)}`); void load(); } catch (err) { setError(err instanceof Error ? err.message : 'Failed'); }
  };
  const runAction = async () => {
    const a = page.actions?.[actionIdx]; if (!a) return; setError(''); setMsg('');
    try { const body = JSON.parse(actionBody); const r = await api(a.path(actionValue), { method: a.method ?? 'POST', body: a.method === 'GET' ? undefined : JSON.stringify(body) }); setMsg(`OK: ${json(r)}`); void load(); } catch (err) { setError(err instanceof Error ? err.message : 'Failed'); }
  };

  return (<>
    <header><div><p className="eyebrow">MODULE / {page.title.toUpperCase()}</p><h1>{page.title}</h1>{page.note && <p>{page.note}</p>}</div>{page.getPath && <button className="ghost" onClick={() => void load()}>Refresh</button>}</header>
    {error && <ErrorNote e={error} />}{msg && <Toast msg={msg} />}
    <div className="tabs">{page.getPath && <button className={tab === 'view' ? 'active' : ''} onClick={() => setTab('view')}>View</button>}{(page.post || page.form || page.spec) && <button className={tab === 'create' ? 'active' : ''} onClick={() => setTab('create')}>Create</button>}{page.actions && page.actions.length > 0 && <button className={tab === 'actions' ? 'active' : ''} onClick={() => setTab('actions')}>Action</button>}</div>

    {tab === 'view' && page.getPath && <section className="panel"><DataTable rows={rows} loading={loading} empty={page.empty} /></section>}
    {tab === 'create' && (page.post || page.form || page.spec) && (page.form ? <TypedForm kind={page.form} onDone={m => { setMsg(m); void load(); }} /> : page.spec ? <SpecForm spec={page.spec} resolvePath={() => page.post!.path} onDone={m => { setMsg(m); void load(); }} /> : <section className="panel"><p className="eyebrow">POST {page.post!.path}</p><h2>Create</h2><textarea className="jsonArea" rows={16} spellCheck={false} value={createBody} onChange={e => setCreateBody(e.target.value)} /><button className="primary" onClick={() => void runPost()}>Submit</button></section>)}
    {tab === 'actions' && page.actions && <section className="panel"><p className="eyebrow">ACTION</p><h2>{page.actions[actionIdx]?.label}</h2><div className="formInline">{!page.actions[actionIdx]?.spec && <Field label="Record ID" value={actionValue} onChange={setActionValue} />}<Select label="Action" value={String(actionIdx)} onChange={v => { const i = Number(v); setActionIdx(i); setActionBody(page.actions![i].body); }} options={page.actions.map((a, i) => [String(i), a.label])} /></div>{page.actions[actionIdx]?.spec ? <SpecForm spec={page.actions[actionIdx].spec!} resolvePath={id => page.actions![actionIdx].path(id)} recordId={true} onDone={m => { setMsg(m); void load(); }} /> : <><textarea className="jsonArea" rows={8} spellCheck={false} value={actionBody} onChange={e => setActionBody(e.target.value)} /><button className="primary" onClick={() => void runAction()}>Run</button></>}</section>}
  </>);
}

/* ---------- catalog ---------- */
const today = () => new Date().toISOString().slice(0, 10);

const SALES_LINES = (label = 'Line items') => ({
  key: 'lines', label, addLabel: 'Add line', minRows: 1,
  columns: [
    { key: 'item_id', label: 'Item ID', type: 'number' as const, def: '1' },
    { key: 'description', label: 'Description', def: 'Consulting services' },
    { key: 'quantity', label: 'Qty', type: 'number' as const, def: '1' },
    { key: 'unit_price', label: 'Unit price', type: 'number' as const, def: '1000' },
    { key: 'discount_percent', label: 'Disc %', type: 'number' as const, def: '0' },
    { key: 'tax_rate', label: 'Tax %', type: 'number' as const, def: '18' },
  ],
});

const PURCHASE_LINES = (label = 'Line items') => SALES_LINES(label);
const ITEM_LINES = (label = 'Lines') => ({
  key: 'lines', label, addLabel: 'Add line', minRows: 1,
  columns: [
    { key: 'item_id', label: 'Item ID', type: 'number' as const, def: '1' },
    { key: 'description', label: 'Description', def: 'Bench power supply' },
    { key: 'quantity', label: 'Qty', type: 'number' as const, def: '1' },
    { key: 'estimated_unit_cost', label: 'Est. cost', type: 'number' as const, def: '15000' },
  ],
});

const CUSTOMER_SRC = { path: `/parties?company_id=${CID()}&party_type=customer`, value: 'id', label: 'name' };
const SUPPLIER_SRC = { path: `/parties?company_id=${CID()}&party_type=supplier`, value: 'id', label: 'name' };
const PO_SRC = { path: `/purchase-orders?company_id=${CID()}`, value: 'id', label: 'number' };
const BOM_SRC = { path: `/bill-of-materials?company_id=${CID()}`, value: 'id', label: 'id' };
const ASSET_SRC = { path: `/maintenance-assets?company_id=${CID()}`, value: 'id', label: 'name' };
const BANK_SRC = { path: `/bank-accounts?company_id=${CID()}`, value: 'id', label: 'name' };

const M: ModuleCfg[] = [
  { id: 'finance', label: 'Finance', icon: '◉', pages: [
    { id: 'accounts', title: 'Chart of accounts', getPath: '/accounts', post: { label: 'Create account', path: '/accounts', body: '{}' }, spec: { title: 'New account', fields: [
      { key: 'code', label: 'Code', required: true, def: '4001', placeholder: '4001' },
      { key: 'name', label: 'Account name', required: true, def: 'Sales Revenue' },
      { key: 'account_type', label: 'Type', type: 'select', def: 'asset', options: [['asset', 'Asset'], ['liability', 'Liability'], ['equity', 'Equity'], ['revenue', 'Revenue'], ['expense', 'Expense']] },
    ] }, empty: 'No accounts yet.' },
    { id: 'number-sequences', title: 'Number sequences', post: { label: 'Create sequence', path: '/number-sequences', body: '{}' }, spec: { title: 'New number sequence', fields: [
      { key: 'document_type', label: 'Document type', type: 'select', def: 'ar_invoice', options: [['ar_invoice', 'AR invoice'], ['ap_invoice', 'AP invoice'], ['receipt', 'Receipt'], ['payment', 'Payment'], ['sales_quote', 'Sales quote'], ['sales_order', 'Sales order'], ['purchase_request', 'Purchase request'], ['rfq', 'RFQ'], ['purchase_order', 'Purchase order'], ['goods_receipt', 'Goods receipt'], ['stock_transfer', 'Stock transfer'], ['sales_delivery', 'Sales delivery']] },
      { key: 'prefix', label: 'Prefix', def: 'INV' },
      { key: 'next_number', label: 'Next number', type: 'number', def: '1', min: 1 },
      { key: 'padding', label: 'Padding', type: 'number', def: '5', min: 1, max: 12 },
    ] }, note: 'Required before documents can be numbered.' },
    { id: 'invoices', title: 'Invoices', getPath: '/invoices?invoice_type=ar', form: 'ar-invoice', post: { label: 'Create invoice', path: '/invoices', body: '{}' }, actions: [{ label: 'Post invoice', path: id => `/invoices/${id}/post`, body: '{}' }], empty: 'No AR invoices yet.', note: 'Creating an invoice reserves nothing; post it after review.' },
    { id: 'ap-invoices', title: 'Vendor invoices', getPath: '/invoices?invoice_type=ap', form: 'ap-invoice', post: { label: 'Create AP invoice', path: '/invoices', body: '{}' }, actions: [{ label: 'Post invoice', path: id => `/invoices/${id}/post`, body: '{}' }], empty: 'No AP invoices yet.' },
    { id: 'payments', title: 'Payments & allocations', form: 'payment', post: { label: 'Record receipt / payment', path: '/payments', body: '{}' }, actions: [{ label: 'Allocate payment to invoice', path: id => `/payments/${id}/allocate`, body: '{}', spec: { title: 'Allocate payment', fields: [
      { key: 'invoice_id', label: 'Invoice ID', type: 'number', required: true, def: '1', min: 1 },
      { key: 'amount', label: 'Amount', type: 'number', required: true, def: '295000', min: 0, step: 'any' },
    ] } }], note: 'Allocation links an open payment to an open invoice.' },
    { id: 'journal', title: 'Journal entries', form: 'journal', post: { label: 'Create journal', path: '/journal-entries', body: '{}' }, actions: [{ label: 'Post journal', path: id => `/journal-entries/${id}/post`, body: '{}' }], note: 'Journals must be balanced before posting.' },
    { id: 'trial-balance', title: 'Trial balance', getPath: '/trial-balance', empty: 'Nothing posted yet.' },
    { id: 'ageing', title: 'AR/AP ageing', getPath: '/ageing', note: 'Open items bucketed by due date.' },
    { id: 'fiscal-periods', title: 'Fiscal periods', getPath: '/fiscal-periods', post: { label: 'Create period', path: '/fiscal-periods', body: '{}' }, spec: { title: 'New fiscal period', fields: [
      { key: 'code', label: 'Code', required: true, def: 'FY26-Q3' },
      { key: 'name', label: 'Name', required: true, def: 'Oct–Dec 2026' },
      { key: 'start_date', label: 'Start date', type: 'date', required: true, def: '2026-10-01' },
      { key: 'end_date', label: 'End date', type: 'date', required: true, def: '2026-12-31' },
    ] } },
    { id: 'price-lists', title: 'Price lists', getPath: '/price-lists', post: { label: 'Create price list', path: '/price-lists', body: '{}' }, spec: { title: 'New price list', fields: [
      { key: 'code', label: 'Code', required: true, def: 'STD' },
      { key: 'name', label: 'Name', required: true, def: 'Standard' },
      { key: 'currency', label: 'Currency', def: 'INR' },
      { key: 'valid_from', label: 'Valid from', type: 'date', required: true, def: today() },
      { key: 'valid_until', label: 'Valid until', type: 'date', required: true, def: '2027-03-31' },
    ], lines: { key: 'lines', label: 'Items', addLabel: 'Add item', minRows: 1, columns: [
      { key: 'item_id', label: 'Item ID', type: 'number', def: '1' },
      { key: 'unit_price', label: 'Unit price', type: 'number', def: '25000' },
    ] } } },
    { id: 'bank-accounts', title: 'Bank accounts', getPath: '/bank-accounts', post: { label: 'Create bank account', path: '/bank-accounts', body: '{}' }, spec: { title: 'New bank account', fields: [
      { key: 'code', label: 'Code', required: true, def: 'HDFC-001' },
      { key: 'name', label: 'Account name', required: true, def: 'HDFC Current' },
      { key: 'currency', label: 'Currency', def: 'INR' },
      { key: 'gl_account_id', label: 'GL account ID (optional)', type: 'number', min: 1 },
    ] } },
    { id: 'bank-recon', title: 'Bank reconciliation', getPath: '/bank-reconciliations', post: { label: 'New reconciliation', path: '/bank-reconciliations', body: '{}' }, spec: { title: 'New reconciliation', fields: [
      { key: 'bank_account_id', label: 'Bank account', type: 'select', required: true, optionsFrom: { ...BANK_SRC }, asNumber: true },
      { key: 'statement_date', label: 'Statement date', type: 'date', required: true, def: today() },
      { key: 'opening_balance', label: 'Opening balance', type: 'number', def: '500000', step: 'any' },
      { key: 'closing_balance', label: 'Closing balance', type: 'number', def: '795000', step: 'any' },
      { key: 'notes', label: 'Notes', def: 'November statement' },
    ] } },
    { id: 'fixed-assets', title: 'Fixed assets', getPath: '/fixed-assets', post: { label: 'Register asset', path: '/fixed-assets', body: '{}' }, spec: { title: 'Register fixed asset', fields: [
      { key: 'code', label: 'Code', required: true, def: 'FA-0001' },
      { key: 'name', label: 'Asset name', required: true, def: 'Laptop - Design team' },
      { key: 'category', label: 'Category', def: 'IT' },
      { key: 'purchase_date', label: 'Purchase date', type: 'date', required: true, def: today() },
      { key: 'cost', label: 'Cost', type: 'number', required: true, def: '85000', step: 'any' },
      { key: 'salvage_value', label: 'Salvage value', type: 'number', def: '5000', step: 'any' },
      { key: 'useful_life_months', label: 'Useful life (months)', type: 'number', def: '36', min: 1 },
    ] }, actions: [{ label: 'Post monthly depreciation', path: id => `/fixed-assets/${id}/depreciate`, body: '{}', spec: { title: 'Post depreciation', fields: [
      { key: 'months', label: 'Months', type: 'number', required: true, def: '1', min: 1 },
    ] } }] },
  ]},
  { id: 'sales', label: 'Sales', icon: '◍', pages: [
    { id: 'parties', title: 'Customers & vendors', getPath: '/parties', form: 'party', post: { label: 'Create party', path: '/parties', body: '{}' }, empty: 'No parties yet.' },
    { id: 'quotes', title: 'Quotes', getPath: '/sales-quotes', post: { label: 'Create quote', path: '/sales-quotes', body: '{}' }, spec: { title: 'New quotation', fields: [
      { key: 'customer_id', label: 'Customer', type: 'select', required: true, asNumber: true, optionsFrom: { ...CUSTOMER_SRC } },
      { key: 'quote_date', label: 'Quote date', type: 'date', required: true, def: today() },
      { key: 'valid_until', label: 'Valid until', type: 'date', required: true, def: '2026-12-31' },
      { key: 'currency', label: 'Currency', def: 'INR' },
      { key: 'notes', label: 'Notes', def: 'Thanks for your business' },
    ], lines: SALES_LINES('Quoted items') }, actions: [{ label: 'Send quote', path: id => `/sales-quotes/${id}/send`, body: '{}' }] },
    { id: 'orders', title: 'Sales orders', getPath: '/sales-orders', post: { label: 'Create order', path: '/sales-orders', body: '{}' }, spec: { title: 'New sales order', fields: [
      { key: 'customer_id', label: 'Customer', type: 'select', required: true, asNumber: true, optionsFrom: { ...CUSTOMER_SRC } },
      { key: 'order_date', label: 'Order date', type: 'date', required: true, def: today() },
      { key: 'promised_date', label: 'Promised date (optional)', type: 'date' },
      { key: 'currency', label: 'Currency', def: 'INR' },
    ], lines: SALES_LINES('Order items') }, actions: [
      { label: 'Confirm order', path: id => `/sales-orders/${id}/confirm`, body: '{}' },
      { label: 'Convert quote → order', path: id => `/sales-quotes/${id}/convert`, body: '{}', spec: { title: 'Convert quote to order', fields: [
        { key: 'order_date', label: 'Order date', type: 'date', required: true, def: today() },
        { key: 'promised_date', label: 'Promised date (optional)', type: 'date' },
      ] } },
      { label: 'Create invoice from order', path: id => `/sales-orders/${id}/invoice`, body: '{}', spec: { title: 'Create invoice', fields: [
        { key: 'invoice_date', label: 'Invoice date', type: 'date', required: true, def: today() },
        { key: 'due_date', label: 'Due date', type: 'date', required: true, def: '2026-12-17' },
      ] } },
      { label: 'Deliver order', path: id => `/sales-orders/${id}/deliver`, body: '{}', spec: { title: 'Deliver order', fields: [
        { key: 'warehouse_id', label: 'Warehouse ID', type: 'number', required: true, def: '1', min: 1 },
        { key: 'delivery_date', label: 'Delivery date', type: 'date', required: true, def: today() },
        { key: 'idempotency_key', label: 'Idempotency key', def: '', placeholder: 'auto-generated' },
      ], lines: { key: 'lines', label: 'Items to deliver', addLabel: 'Add line', minRows: 1, columns: [
        { key: 'sales_order_line_id', label: 'Order line ID', type: 'number', def: '1' },
        { key: 'quantity', label: 'Qty', type: 'number', def: '1' },
      ] }, transform: payload => ({ idempotency_key: payload.idempotency_key && String(payload.idempotency_key).trim() ? payload.idempotency_key : crypto.randomUUID() }) } },
    ], note: 'Integrity: quote → order → delivery → invoice.' },
  ]},
  { id: 'procurement', label: 'Procurement', icon: '◔', pages: [
    { id: 'purchase-requests', title: 'Purchase requests', getPath: '/purchase-requests', post: { label: 'Create request', path: '/purchase-requests', body: '{}' }, spec: { title: 'New purchase request', fields: [
      { key: 'request_date', label: 'Request date', type: 'date', required: true, def: today() },
      { key: 'required_date', label: 'Required date', type: 'date', required: true, def: '2026-12-01' },
      { key: 'requester', label: 'Requester', required: true, def: 'admin' },
      { key: 'department', label: 'Department', def: 'Engineering' },
      { key: 'justification', label: 'Justification', def: 'Stock replenishment' },
    ], lines: ITEM_LINES('Requested items') }, actions: [{ label: 'Submit request', path: id => `/purchase-requests/${id}/submit`, body: '{}' }] },
    { id: 'rfqs', title: 'RFQs', getPath: '/rfqs', post: { label: 'Create RFQ', path: '/rfqs', body: '{}' }, spec: { title: 'New RFQ', fields: [
      { key: 'purchase_request_id', label: 'Purchase request ID (optional)', type: 'number', min: 1 },
      { key: 'rfq_date', label: 'RFQ date', type: 'date', required: true, def: today() },
      { key: 'response_due', label: 'Response due', type: 'date', required: true, def: '2026-12-01' },
      { key: 'currency', label: 'Currency', def: 'INR' },
      { key: 'notes', label: 'Notes', def: '' },
    ], lines: { key: 'lines', label: 'RFQ items', addLabel: 'Add item', minRows: 1, columns: [
      { key: 'item_id', label: 'Item ID', type: 'number', def: '1' },
      { key: 'description', label: 'Description', def: 'Bench power supply' },
      { key: 'quantity', label: 'Qty', type: 'number', def: '1' },
    ] } }, actions: [{ label: 'Issue RFQ', path: id => `/rfqs/${id}/issue`, body: '{}' }, { label: 'Compare RFQ quotes', path: id => `/rfqs/${id}/comparison`, body: '{}', method: 'GET' }] },
    { id: 'supplier-quotes', title: 'Supplier quotes', post: { label: 'Record supplier quote', path: '/supplier-quotes', body: '{}' }, spec: { title: 'New supplier quote', fields: [
      { key: 'rfq_id', label: 'RFQ ID', type: 'number', required: true, def: '1', min: 1 },
      { key: 'supplier_id', label: 'Supplier', type: 'select', required: true, asNumber: true, optionsFrom: { ...SUPPLIER_SRC } },
      { key: 'number', label: 'Quote number', required: true, def: 'SQ-0001' },
      { key: 'quote_date', label: 'Quote date', type: 'date', required: true, def: today() },
      { key: 'valid_until', label: 'Valid until', type: 'date', required: true, def: '2026-12-15' },
    ], lines: PURCHASE_LINES('Quoted lines') }, actions: [{ label: 'Convert quote → purchase order', path: id => `/supplier-quotes/${id}/convert`, body: '{}', spec: { title: 'Convert to purchase order', fields: [
      { key: 'order_date', label: 'Order date', type: 'date', required: true, def: today() },
      { key: 'promised_date', label: 'Promised date (optional)', type: 'date' },
    ] } }], note: 'Totals must be consistent or conversion is rejected.' },
    { id: 'purchase-orders', title: 'Purchase orders', getPath: '/purchase-orders', post: { label: 'Create order', path: '/purchase-orders', body: '{}' }, spec: { title: 'New purchase order', fields: [
      { key: 'supplier_id', label: 'Supplier', type: 'select', required: true, asNumber: true, optionsFrom: { ...SUPPLIER_SRC } },
      { key: 'order_date', label: 'Order date', type: 'date', required: true, def: today() },
      { key: 'promised_date', label: 'Promised date (optional)', type: 'date' },
      { key: 'currency', label: 'Currency', def: 'INR' },
    ], lines: PURCHASE_LINES('Ordered items') }, actions: [
      { label: 'Confirm order', path: id => `/purchase-orders/${id}/confirm`, body: '{}' },
      { label: 'Receive goods', path: id => `/purchase-orders/${id}/receipts`, body: '{}', spec: { title: 'Receive goods', fields: [
        { key: 'number', label: 'Receipt number', required: true, def: 'GRN-0001' },
        { key: 'receipt_date', label: 'Receipt date', type: 'date', required: true, def: today() },
        { key: 'warehouse_id', label: 'Warehouse ID', type: 'number', required: true, def: '1', min: 1 },
        { key: 'notes', label: 'Notes', def: '' },
      ], lines: { key: 'lines', label: 'Received items', addLabel: 'Add line', minRows: 1, columns: [
        { key: 'purchase_order_line_id', label: 'PO line ID', type: 'number', def: '1' },
        { key: 'quantity', label: 'Qty', type: 'number', def: '2' },
      ] } } },
      { label: 'Integrated supplier invoice', path: id => `/purchase-orders/${id}/integrated-supplier-invoice`, body: '{}', spec: { title: 'Integrated supplier invoice', fields: [
        { key: 'invoice_date', label: 'Invoice date', type: 'date', required: true, def: today() },
        { key: 'due_date', label: 'Due date', type: 'date', required: true, def: '2026-12-17' },
        { key: 'idempotency_key', label: 'Idempotency key', def: '', placeholder: 'auto-generated' },
        { key: 'quantity_tolerance', label: 'Qty tolerance', type: 'number', def: '0', min: 0, step: 'any' },
        { key: 'price_tolerance_percent', label: 'Price tolerance %', type: 'number', def: '0', min: 0, step: 'any' },
      ], lines: { key: 'lines', label: 'Invoiced lines', addLabel: 'Add line', minRows: 1, columns: [
        { key: 'purchase_order_line_id', label: 'PO line ID', type: 'number', def: '1' },
        { key: 'invoiced_quantity', label: 'Invoiced qty', type: 'number', def: '2' },
        { key: 'unit_price', label: 'Unit price', type: 'number', def: '14000' },
        { key: 'tax_rate', label: 'Tax %', type: 'number', def: '18' },
      ] }, transform: payload => ({ idempotency_key: payload.idempotency_key && String(payload.idempotency_key).trim() ? payload.idempotency_key : crypto.randomUUID() }) } },
    ] },
    { id: 'landed-costs', title: 'Landed costs', getPath: '/landed-costs', post: { label: 'Allocate landed cost', path: '/landed-costs', body: '{}' }, spec: { title: 'Allocate landed cost', fields: [
      { key: 'purchase_order_id', label: 'Purchase order', type: 'select', required: true, asNumber: true, optionsFrom: { ...PO_SRC } },
      { key: 'description', label: 'Description', def: 'Freight, insurance, customs' },
      { key: 'freight', label: 'Freight', type: 'number', def: '8000', step: 'any' },
      { key: 'insurance', label: 'Insurance', type: 'number', def: '1500', step: 'any' },
      { key: 'duty', label: 'Customs duty', type: 'number', def: '9000', step: 'any' },
      { key: 'other_charges', label: 'Other charges', type: 'number', def: '500', step: 'any' },
    ] } },
  ]},
  { id: 'inventory', label: 'Inventory', icon: '◐', pages: [
    { id: 'items', title: 'Items', getPath: '/inventory/balances', note: 'Set item master data via SQL or API. Balances shown here.' },
    { id: 'balances', title: 'Stock balances', getPath: '/inventory/balances', empty: 'No stock on hand.' },
    { id: 'ledger', title: 'Stock ledger', getPath: '/inventory/ledger', note: 'Full immutable movement history.' },
    { id: 'movements', title: 'Stock movements', post: { label: 'Create movement', path: '/inventory/movements', body: '{}' }, spec: { title: 'New stock movement', fields: [
      { key: 'item_id', label: 'Item ID', type: 'number', required: true, def: '1', min: 1 },
      { key: 'warehouse_id', label: 'Warehouse ID', type: 'number', required: true, def: '1', min: 1 },
      { key: 'movement_type', label: 'Movement type', type: 'select', def: 'opening', options: [['opening', 'Opening'], ['receipt', 'Receipt'], ['issue', 'Issue'], ['adjustment_in', 'Adjustment in'], ['adjustment_out', 'Adjustment out']] },
      { key: 'movement_date', label: 'Date', type: 'date', required: true, def: today() },
      { key: 'quantity', label: 'Quantity', type: 'number', required: true, def: '100', step: 'any' },
      { key: 'unit_cost', label: 'Unit cost', type: 'number', def: '10000', step: 'any' },
      { key: 'reference_type', label: 'Reference type', def: 'manual' },
      { key: 'notes', label: 'Notes', def: '' },
    ] } },
    { id: 'reorder', title: 'Reorder alerts', getPath: '/inventory/reorder-alerts', empty: 'All stocked well.' },
    { id: 'transfers', title: 'Stock transfers', post: { label: 'Create transfer', path: '/stock-transfers', body: '{}' }, spec: { title: 'New stock transfer', fields: [
      { key: 'transfer_date', label: 'Date', type: 'date', required: true, def: today() },
      { key: 'source_warehouse_id', label: 'From warehouse', type: 'number', required: true, def: '1', min: 1 },
      { key: 'destination_warehouse_id', label: 'To warehouse', type: 'number', required: true, def: '2', min: 1 },
      { key: 'notes', label: 'Notes', def: 'Replenishment' },
    ], lines: { key: 'lines', label: 'Items to transfer', addLabel: 'Add item', minRows: 1, columns: [
      { key: 'item_id', label: 'Item ID', type: 'number', def: '1' },
      { key: 'quantity', label: 'Qty', type: 'number', def: '10' },
    ] } }, actions: [{ label: 'Post transfer', path: id => `/stock-transfers/${id}/post`, body: '{}' }] },
    { id: 'reservations', title: 'Reservations', post: { label: 'Reserve stock', path: '/inventory/reservations', body: '{}' }, spec: { title: 'Reserve stock', fields: [
      { key: 'item_id', label: 'Item ID', type: 'number', required: true, def: '1', min: 1 },
      { key: 'warehouse_id', label: 'Warehouse ID', type: 'number', required: true, def: '1', min: 1 },
      { key: 'quantity', label: 'Quantity', type: 'number', required: true, def: '5', step: 'any' },
    ] } },
    { id: 'policies', title: 'Reorder policies', post: { label: 'Create policy', path: '/inventory/policies', body: '{}' }, spec: { title: 'New reorder policy', fields: [
      { key: 'item_id', label: 'Item ID', type: 'number', required: true, def: '1', min: 1 },
      { key: 'warehouse_id', label: 'Warehouse ID', type: 'number', required: true, def: '1', min: 1 },
      { key: 'tracking_mode', label: 'Tracking', type: 'select', def: 'lot', options: [['lot', 'Lot'], ['serial', 'Serial'], ['none', 'None']] },
      { key: 'reorder_point', label: 'Reorder point', type: 'number', def: '10', step: 'any' },
      { key: 'reorder_quantity', label: 'Reorder quantity', type: 'number', def: '50', step: 'any' },
      { key: 'allow_negative', label: 'Allow negative stock', type: 'checkbox', def: 'false' },
    ] } },
  ]},
  { id: 'crm', label: 'CRM', icon: '◓', pages: [
    { id: 'leads', title: 'Leads', getPath: '/leads', form: 'lead', post: { label: 'Create lead', path: '/leads', body: '{}' }, empty: 'No leads yet.' },
    { id: 'opportunities', title: 'Opportunities', getPath: '/opportunities', form: 'opportunity', post: { label: 'Create opportunity', path: '/opportunities', body: '{}' }, empty: 'No opportunities yet.' },
  ]},
  { id: 'manufacturing', label: 'Manufacturing', icon: '◑', pages: [
    { id: 'boms', title: 'Bills of material', getPath: '/bill-of-materials', post: { label: 'Create BOM', path: '/bill-of-materials', body: '{}' }, spec: { title: 'New BOM', fields: [
      { key: 'item_id', label: 'Finished item ID', type: 'number', required: true, def: '2', min: 1 },
      { key: 'revision', label: 'Revision', type: 'number', def: '1', min: 1 },
      { key: 'description', label: 'Description', def: 'Bench PSU assembly v1.0' },
    ] }, actions: [{ label: 'Add component line', path: id => `/bill-of-materials/${id}/lines`, body: '{}', spec: { title: 'Add component', fields: [
      { key: 'bom_id', label: 'BOM ID', type: 'number', required: true, def: '1', min: 1 },
      { key: 'component_id', label: 'Component item ID', type: 'number', required: true, def: '1', min: 1 },
      { key: 'quantity', label: 'Quantity', type: 'number', required: true, def: '1', step: 'any' },
    ] } }], empty: 'No BOMs yet.' },
    { id: 'work-orders', title: 'Work orders', getPath: '/work-orders', post: { label: 'Create work order', path: '/work-orders', body: '{}' }, spec: { title: 'New work order', fields: [
      { key: 'number', label: 'Number', required: true, def: 'WO-0001' },
      { key: 'bom_id', label: 'BOM', type: 'select', required: true, asNumber: true, optionsFrom: { ...BOM_SRC } },
      { key: 'status', label: 'Status', type: 'select', def: 'draft', options: [['draft', 'Draft'], ['planned', 'Planned'], ['released', 'Released'], ['completed', 'Completed']] },
      { key: 'planned_date', label: 'Planned date', type: 'date', required: true, def: '2026-12-01' },
      { key: 'quantity', label: 'Quantity', type: 'number', def: '10', step: 'any' },
    ] }, empty: 'No work orders yet.' },
  ]},
  { id: 'projects', label: 'Projects', icon: '◒', pages: [
    { id: 'projects', title: 'Projects', getPath: '/projects', post: { label: 'Create project', path: '/projects', body: '{}' }, spec: { title: 'New project', fields: [
      { key: 'code', label: 'Code', required: true, def: 'PRJ-001' },
      { key: 'name', label: 'Name', required: true, def: 'Plant automation rollout' },
      { key: 'description', label: 'Description', def: '' },
      { key: 'start_date', label: 'Start date', type: 'date', required: true, def: today() },
      { key: 'end_date', label: 'End date (optional)', type: 'date' },
      { key: 'status', label: 'Status', type: 'select', def: 'planning', options: [['planning', 'Planning'], ['active', 'Active'], ['on_hold', 'On hold'], ['completed', 'Completed']] },
      { key: 'budget', label: 'Budget', type: 'number', def: '5000000', step: 'any' },
    ] }, empty: 'No projects yet.' },
    { id: 'tasks', title: 'Project tasks', getPath: '/projects', post: { label: 'Add task to project #1', path: '/projects/1/tasks', body: '{}' }, spec: { title: 'Add task (project #1)', fields: [
      { key: 'project_id', label: 'Project ID', type: 'number', required: true, def: '1', min: 1 },
      { key: 'name', label: 'Task', required: true, def: 'Requirements workshop' },
      { key: 'description', label: 'Details', def: '' },
      { key: 'order', label: 'Order', type: 'number', def: '1', min: 0 },
      { key: 'assigned_to', label: 'Assigned to', def: 'admin' },
      { key: 'due_date', label: 'Due date (optional)', type: 'date' },
      { key: 'estimated_hours', label: 'Estimated hours', type: 'number', def: '16', step: 'any' },
    ] }, note: 'Change project ID in the path & body for other projects.' },
  ]},
  { id: 'maintenance', label: 'Maintenance & Assets', icon: '◕', pages: [
    { id: 'm-assets', title: 'Maintenance assets', getPath: '/maintenance-assets', post: { label: 'Register asset', path: '/maintenance-assets', body: '{}' }, spec: { title: 'Register asset', fields: [
      { key: 'code', label: 'Code', required: true, def: 'CNC-01' },
      { key: 'name', label: 'Name', required: true, def: 'CNC Lathe #1' },
      { key: 'category', label: 'Category', def: 'Shop floor' },
      { key: 'purchase_date', label: 'Purchase date', type: 'date', required: true, def: today() },
      { key: 'warranty_expiry', label: 'Warranty expiry (optional)', type: 'date' },
      { key: 'location', label: 'Location', def: 'Plant A' },
    ] }, empty: 'No assets yet.' },
    { id: 'm-work-orders', title: 'Maintenance work orders', getPath: '/maintenance-work-orders', post: { label: 'Create work order', path: '/maintenance-work-orders', body: '{}' }, spec: { title: 'New maintenance work order', fields: [
      { key: 'number', label: 'Number', required: true, def: 'MWO-0001' },
      { key: 'asset_id', label: 'Asset', type: 'select', required: true, asNumber: true, optionsFrom: { ...ASSET_SRC } },
      { key: 'requested_by', label: 'Requested by', def: 'admin' },
      { key: 'work_description', label: 'Work description', def: 'Monthly preventive service' },
      { key: 'priority', label: 'Priority', type: 'select', def: 'medium', options: [['low', 'Low'], ['medium', 'Medium'], ['high', 'High'], ['critical', 'Critical']] },
      { key: 'requested_date', label: 'Requested date', type: 'date', required: true, def: today() },
    ] }, empty: 'No work orders yet.' },
  ]},
  { id: 'finance-ops', label: 'Consolidation & Treasury', icon: '◗', pages: [
    { id: 'consolidation', title: 'Ledger consolidation', getPath: '/ledger-consolidations', post: { label: 'New consolidation run', path: '/ledger-consolidations', body: '{}' }, spec: { title: 'New consolidation run', fields: [
      { key: 'period_start', label: 'Period start', type: 'date', required: true, def: '2026-10-01' },
      { key: 'period_end', label: 'Period end', type: 'date', required: true, def: '2026-10-31' },
      { key: 'notes', label: 'Notes', def: 'Q3 consolidation' },
    ] }, empty: 'No consolidations yet.' },
    { id: 'treasury', title: 'Treasury accounts', getPath: '/treasury-accounts', post: { label: 'Create treasury account', path: '/treasury-accounts', body: '{}' }, spec: { title: 'New treasury account', fields: [
      { key: 'code', label: 'Code', required: true, def: 'HDFC-OPS' },
      { key: 'name', label: 'Name', required: true, def: 'HDFC Operations' },
      { key: 'currency', label: 'Currency', def: 'INR' },
      { key: 'balance', label: 'Opening balance', type: 'number', def: '1250000', step: 'any' },
      { key: 'account_type', label: 'Type', type: 'select', def: 'bank', options: [['bank', 'Bank'], ['cash', 'Cash'], ['investment', 'Investment'], ['fixed_deposit', 'Fixed deposit']] },
      { key: 'bank_account_id', label: 'Linked bank account ID (optional)', type: 'number', min: 1 },
    ] }, empty: 'No treasury accounts yet.' },
  ]},
  { id: 'reports', label: 'Reports', icon: '▤', pages: [
    { id: 'income-statement', title: 'Income statement', getPath: '/reports/income-statement' },
    { id: 'balance-sheet', title: 'Balance sheet', getPath: '/reports/balance-sheet' },
    { id: 'kpis', title: 'KPIs', getPath: '/reports/kpis' },
    { id: 'sales-performance', title: 'Sales performance', getPath: '/reports/sales-performance' },
    { id: 'procurement-performance', title: 'Procurement performance', getPath: '/reports/procurement-performance' },
    { id: 'inventory-summary', title: 'Inventory summary', getPath: '/reports/inventory-summary' },
    { id: 'integration-health', title: 'Integration health', getPath: '/reports/integration-health' },
    { id: 'data-quality', title: 'Data quality findings', getPath: '/reports/data-quality', empty: 'No findings — clean data.' },
    { id: 'saved-reports', title: 'Saved reports', getPath: '/reports/saved', post: { label: 'Save a report', path: '/reports/saved', body: '{}' }, spec: { title: 'Save a report', fields: [
      { key: 'name', label: 'Name', required: true, def: 'Monthly board pack' },
      { key: 'report_type', label: 'Report type', type: 'select', required: true, def: 'income_statement', options: [['income_statement', 'Income statement'], ['balance_sheet', 'Balance sheet'], ['trial_balance', 'Trial balance'], ['ar_ageing', 'AR ageing'], ['ap_ageing', 'AP ageing'], ['sales_performance', 'Sales performance'], ['procurement_performance', 'Procurement performance'], ['inventory_summary', 'Inventory summary'], ['integration_health', 'Integration health']] },
      { key: 'parameters_json', label: 'Parameters (JSON)', type: 'textarea', def: '{}' },
      { key: 'owner', label: 'Owner', def: 'admin' },
      { key: 'shared', label: 'Share with everyone', type: 'checkbox', def: 'true' },
    ], transform: payload => ({ parameters: (() => { try { return JSON.parse(String(payload.parameters_json || '{}')); } catch { return {}; } })() }) }, actions: [{ label: 'Schedule report (cron)', path: id => `/saved-reports/${id}/schedule`, body: '{}', spec: { title: 'Schedule report', fields: [
      { key: 'schedule_cron', label: 'Cron expression', required: true, def: '0 9 1 * *', placeholder: '0 9 1 * * (9am on the 1st)' },
    ] } }] },
    { id: 'run-report', title: 'Run a report', post: { label: 'Run report', path: '/reports/run', body: '{}' }, spec: { title: 'Run a report', fields: [
      { key: 'report_type', label: 'Report type', type: 'select', required: true, def: 'trial_balance', options: [['trial_balance', 'Trial balance'], ['income_statement', 'Income statement'], ['balance_sheet', 'Balance sheet'], ['ar_ageing', 'AR ageing'], ['ap_ageing', 'AP ageing'], ['sales_performance', 'Sales performance'], ['procurement_performance', 'Procurement performance'], ['inventory_summary', 'Inventory summary'], ['integration_health', 'Integration health']] },
      { key: 'parameters', label: 'Parameters (JSON)', type: 'textarea', def: '{}' },
      { key: 'generated_by', label: 'Generated by', def: 'admin' },
    ], transform: payload => ({ parameters: (() => { try { return JSON.parse(String(payload.parameters || '{}')); } catch { return {}; } })() }) }, note: 'Returns the report payload directly.' },
  ]},
  { id: 'admin', label: 'Administration', icon: '◘', pages: [
    { id: 'users', title: 'Create user', post: { label: 'Create user', path: '/admin/users', body: '{}' }, spec: { title: 'New user', fields: [
      { key: 'username', label: 'Username', required: true, def: 'finance.manager' },
      { key: 'display_name', label: 'Display name', required: true, def: 'Finance Manager' },
      { key: 'password', label: 'Password', required: true, def: 'ChangeMe-Strong-123!', placeholder: '12+ characters' },
    ] }, note: 'Passwords must be ≥ 12 characters.' },
    { id: 'roles', title: 'Create role', post: { label: 'Create role', path: '/admin/roles', body: '{}' }, spec: { title: 'New role', fields: [
      { key: 'code', label: 'Code', required: true, def: 'finance_manager' },
      { key: 'name', label: 'Role name', required: true, def: 'Finance Manager' },
      { key: 'permissions', label: 'Permissions (comma separated)', type: 'textarea', required: true, def: 'reports:read,data:write' },
    ], transform: payload => ({ permissions: String(payload.permissions || '').split(',').map(s => s.trim()).filter(Boolean) }) } },
    { id: 'approvals', title: 'Approvals', post: { label: 'Request approval', path: '/approvals', body: '{}' }, spec: { title: 'New approval request', fields: [
      { key: 'entity_type', label: 'Entity type', required: true, def: 'journal' },
      { key: 'entity_id', label: 'Entity ID', required: true, def: '1' },
      { key: 'action', label: 'Action', type: 'select', required: true, def: 'journal_post', options: [['journal_post', 'Journal post'], ['credit_override', 'Credit override'], ['inventory_adjustment', 'Inventory adjustment'], ['supplier_match_override', 'Supplier match override'], ['role_assignment', 'Role assignment']] },
      { key: 'reason', label: 'Reason', required: true, def: 'Posting month-end accrual' },
    ] }, actions: [{ label: 'Approve request', path: id => `/approvals/${id}/approve`, body: '{}', spec: { title: 'Approve request', fields: [
      { key: 'expected_version', label: 'Expected version', type: 'number', required: true, def: '1', min: 1 },
      { key: 'reason', label: 'Reason', required: true, def: 'Approved after review' },
    ] } }], note: 'Maker-checker enforced: approver ≠ requester.' },
    { id: 'mfa', title: 'MFA (TOTP)', getPath: '/auth/mfa/setup', actions: [{ label: 'Verify & enable MFA', path: () => '/auth/mfa/verify', body: '{}', spec: { title: 'Verify MFA', fields: [
      { key: 'company_id', label: 'Company ID', type: 'number', required: true, def: '1', min: 1 },
      { key: 'code', label: '6-digit code', required: true, def: '000000', placeholder: '123456' },
    ] } }], note: 'Copy the secret into your authenticator, then verify.' },
  ]},
  { id: 'platform', label: 'Platform', icon: '▦', pages: [
    { id: 'notifications', title: 'Notifications', getPath: '/notifications', post: { label: 'Create notification', path: '/notifications', body: '{}' }, spec: { title: 'New notification', fields: [
      { key: 'user_id', label: 'User ID (optional)', type: 'number', min: 1 },
      { key: 'title', label: 'Title', required: true, def: 'Welcome to PeaOps' },
      { key: 'body', label: 'Message', def: 'Your pilot tenant is ready.' },
    ] }, empty: 'No notifications.' },
    { id: 'attachments', title: 'Attachments', getPath: '/attachments', post: { label: 'Register attachment', path: '/attachments', body: '{}' }, spec: { title: 'Register attachment', fields: [
      { key: 'entity_type', label: 'Entity type', required: true, def: 'invoice' },
      { key: 'entity_id', label: 'Entity ID', required: true, def: '1' },
      { key: 'filename', label: 'Filename', required: true, def: 'PO-0001.pdf' },
      { key: 'file_path', label: 'File path', required: true, def: '/var/lib/peaops/uploads/PO-0001.pdf' },
      { key: 'content_type', label: 'Content type', def: 'application/pdf' },
    ] }, empty: 'No attachments.' },
    { id: 'events', title: 'Integration events', getPath: '/integration/events', empty: 'No integration activity yet.' },
    { id: 'trace', title: 'Integration trace', getPath: '/integration/trace', empty: 'No trace entries.' },
  ]},
];

const MODULES = M;

/* ---------- dashboard ---------- */
function Dashboard({ session }: { session: Session }) {
  const [kpi, setKpi] = useState<Record<string, string> | null>(null);
  const [sales, setSales] = useState<Array<{ customer: string; invoice_count: number; sales: string; outstanding: string }> | null>(null);
  const [ready, setReady] = useState<Record<string, string> | null>(null);
  const [errs, setErrs] = useState('');
  useEffect(() => {
    (async () => {
      try {
        const [k, sp, r] = await Promise.all([api<Record<string, string>>(`/reports/kpis?company_id=${CID()}`), api<Array<{ customer: string; invoice_count: number; sales: string; outstanding: string }>>(`/reports/sales-performance?company_id=${CID()}`), api<Record<string, string>>('/health/ready', {}, false)]);
        setKpi(k); setSales(sp); setReady(r);
      } catch (e) { setErrs(e instanceof Error ? e.message : 'Failed to load dashboard'); }
    })();
  }, []);
  const n = (v?: string) => Number(v ?? 0);
  const tiles = [
    { label: 'API status', value: String(ready?.status ?? '…'), detail: ready ? String(ready.database ?? '') : '', tone: ready?.status === 'ready' ? 'ok' : 'warn' },
    { label: 'Sales (all AR)', value: money(n(kpi?.sales)), detail: `Quote→order ${n(kpi?.quote_conversion_percent).toFixed(0)}% win rate`, tone: '' },
    { label: 'Receivables', value: money(n(kpi?.receivables)), detail: `${n(kpi?.receivable_days).toFixed(0)} days outstanding`, tone: 'warn' },
    { label: 'Inventory value', value: money(n(kpi?.inventory_value)), detail: `${n(kpi?.integration_success_percent).toFixed(0)}% integration success`, tone: 'violet' },
  ];
  const wc = [
    { label: 'Sales', value: n(kpi?.sales) }, { label: 'Purchases', value: n(kpi?.purchases) }, { label: 'Receivables', value: n(kpi?.receivables) }, { label: 'Payables', value: n(kpi?.payables) }, { label: 'Inventory', value: n(kpi?.inventory_value) },
  ];
  const topCustomers = (sales ?? []).slice(0, 6).map(s => ({ label: s.customer, value: n(s.sales) }));
  const donutParts = (sales ?? []).slice(0, 5).map((s, i) => ({ label: s.customer, value: n(s.outstanding), color: CHART_COLORS[i % CHART_COLORS.length] }));
  return (<>
    <header><div><p className="eyebrow">PEAOPS / COMMAND CENTER</p><h1>Good evening, {session.username}</h1><p>Live numbers from the local API.</p></div></header>
    {errs && <ErrorNote e={errs} />}
    <section className="heroGrid">{tiles.map(t => <div key={t.label} className={`metric ${t.tone}`}><span>{t.label}</span><strong>{t.value}</strong><small>{t.detail}</small></div>)}</section>
    <div className="chartGrid">
      <section className="panel chartCard"><p className="eyebrow">CAPITAL PROFILE</p><h2>Sales vs payables vs stock</h2><HorizontalBarChart data={wc} format={v => `₹ ${(v / 100000).toFixed(1)}L`} /></section>
      <section className="panel chartCard"><p className="eyebrow">TOP CUSTOMERS</p><h2>Billed sales</h2><HorizontalBarChart data={topCustomers} format={v => `₹ ${(v / 100000).toFixed(1)}L`} /></section>
      <section className="panel chartCard donutCard"><p className="eyebrow">OUTSTANDING AR</p><h2>Who owes the most</h2><div className="donutWrap"><Donut parts={donutParts} /><ul className="legend">{donutParts.map(p => <li key={p.label}><i style={{ background: p.color }} />{p.label} <b>{money(p.value)}</b></li>)}</ul></div></section>
    </div>
    <section className="panel"><p className="eyebrow">QUICK ACTIONS</p><h2>What teams do first</h2><div className="quickLinks"><a href="#/finance/invoices">Create an invoice →</a><a href="#/sales/quotes">Send a quote →</a><a href="#/procurement/purchase-orders">Raise a PO →</a><a href="#/reports/sales-performance">Sales performance →</a><a href="#/admin/approvals">Pending approvals →</a></div></section>
  </>);
}

/* ---------- shell ---------- */
type Route = { module: string; page: string } | { module: 'dashboard'; page: '' };
function parseHash(): Route {
  const h = window.location.hash.replace(/^#\/?/, '');
  if (!h) return { module: 'dashboard', page: '' };
  const [module, page] = h.split('/');
  return { module, page: page ?? '' };
}

function App() {
  const [session, setSession] = useState<Session | null>(() => loadSession());
  const [route, setRoute] = useState<Route>(() => parseHash());
  useEffect(() => { const h = () => setRoute(parseHash()); window.addEventListener('hashchange', h); return () => window.removeEventListener('hashchange', h); }, []);

  if (!session) return <Login onLogin={() => setSession(loadSession())} />;

  const activeModule = route.module !== 'dashboard' ? MODULES.find(m => m.id === route.module) : undefined;
  const activePage = activeModule?.pages.find(p => p.id === route.page);

  return (<div className="appShell">
    <aside className="sidebar">
      <div className="brandBlock"><div className="brand"><i>pea</i>Ops <b>ERP</b></div><small>v0.8.2 • on-prem LIVE</small></div>
      <nav className="sideNav">
        <a href="#/dashboard" className={route.module === 'dashboard' ? 'active' : ''}><span>⌂</span>Overview</a>
        {MODULES.map(m => <div key={m.id} className="navGroup"><p>{m.label}</p>{m.pages.slice(0, 4).map(p => <a key={p.id} href={`#/${m.id}/${p.id}`} className={route.module === m.id && route.page === p.id ? 'active' : ''}><span>{m.icon}</span>{p.title}</a>)}</div>)}
      </nav>
      <div className="sideFooter"><div className="who"><b>{session.username}</b><small>Company #{session.companyId}</small></div><button className="textBtn" onClick={() => { clearSession(); window.location.hash = ''; setSession(null); }}>Sign out →</button></div>
    </aside>
    <main className="content">
      {route.module === 'dashboard' && <Dashboard session={session} />}
      {activeModule && activePage && <EntityPage key={`${activeModule.id}/${activePage.id}`} page={activePage} />}
      {activeModule && !activePage && <header><div><p className="eyebrow">{activeModule.label.toUpperCase()}</p><h1>{activeModule.label}</h1></div></header>}
      {activeModule && <nav className="tabs tabsFooter">{activeModule.pages.map(p => <a key={p.id} className={route.page === p.id ? 'active' : ''} href={`#/${activeModule.id}/${p.id}`}>{p.title}</a>)}</nav>}
      {!activeModule && route.module !== 'dashboard' && <p className="muted">Unknown module. <a href="#/dashboard">Go to overview →</a></p>}
    </main>
  </div>);
}

function Login({ onLogin }: { onLogin: () => void }) {
  const [companyId, setCompanyId] = useState('1'); const [username, setUsername] = useState(''); const [password, setPassword] = useState(''); const [mfa, setMfa] = useState('');
  const [error, setError] = useState(''); const [busy, setBusy] = useState(false);
  const submit = async (e: React.FormEvent) => {
    e.preventDefault(); setBusy(true); setError('');
    try {
      const res = await api<{ access_token: string; refresh_token: string; permissions: string[] }>('/auth/login', { method: 'POST', body: JSON.stringify({ company_id: Number(companyId), username, password, ...(mfa ? { mfa_code: mfa } : {}) }) }, false);
      saveSession({ token: res.access_token, refresh: res.refresh_token, companyId: Number(companyId), username, permissions: res.permissions });
      onLogin();
    } catch (err) { setError(err instanceof Error ? err.message : 'Sign-in failed'); } finally { setBusy(false); }
  };
  return (<div className="loginWrap"><div className="loginArt"><p className="eyebrow">PEAOPS ERP</p><h1>Run your whole<br/>business from one<br/><em>clean cockpit.</em></h1><p>Finance • Sales • Procurement • Inventory • Projects • Manufacturing — on your own Linux server, Apache-2.0.</p><ul><li>✓ Multi-company, RBAC, maker-checker approvals</li><li>✓ Postgres, Docker, SSO-ready, audit trail</li><li>✓ 116 automated tests</li></ul></div>
    <form className="loginCard" onSubmit={submit}><p className="eyebrow">SIGN IN</p><h2>Welcome back</h2>{error && <ErrorNote e={error} />}
      <Field label="Company ID" value={companyId} onChange={setCompanyId} required type="number" />
      <Field label="Username" value={username} onChange={setUsername} required placeholder="admin" />
      <Field label="Password" value={password} onChange={setPassword} required type="password" placeholder="••••••••••••" />
      <Field label="MFA code (optional)" value={mfa} onChange={setMfa} placeholder="000000" />
      <button className="primary full" disabled={busy}>{busy ? 'Signing in…' : 'Sign in'}</button>
      <small className="foot">Demo: company <b>1</b>, user <b>admin</b>, password <b>Admin@123456</b></small>
    </form></div>);
}

createRoot(document.getElementById('root')!).render(<App />);
