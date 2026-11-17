
import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';
import { api, root, clearSession, loadSession, saveSession, money, type Session } from './api';
import { DataTable, ErrorNote, Field, Select, Toast, Pill } from './ui';

const CID = () => loadSession()?.companyId ?? 1;

/* ---------- generic endpoint page ---------- */
type Action = { label: string; path: (v: string) => string; body: string; method?: 'POST' | 'GET' };
type PageCfg = {
  id: string; title: string; getPath?: string; query?: boolean; empty?: string;
  post?: { label: string; path: string; body: string };
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
    <div className="tabs">{page.getPath && <button className={tab === 'view' ? 'active' : ''} onClick={() => setTab('view')}>View</button>}{page.post && <button className={tab === 'create' ? 'active' : ''} onClick={() => setTab('create')}>Create</button>}{page.actions && page.actions.length > 0 && <button className={tab === 'actions' ? 'active' : ''} onClick={() => setTab('actions')}>Action</button>}</div>

    {tab === 'view' && page.getPath && <section className="panel"><DataTable rows={rows} loading={loading} empty={page.empty} /></section>}
    {tab === 'create' && page.post && <section className="panel"><p className="eyebrow">POST {page.post.path}</p><h2>Create</h2><textarea className="jsonArea" rows={16} spellCheck={false} value={createBody} onChange={e => setCreateBody(e.target.value)} /><button className="primary" onClick={() => void runPost()}>Submit</button></section>}
    {tab === 'actions' && page.actions && <section className="panel"><p className="eyebrow">ACTION</p><h2>{page.actions[actionIdx]?.label}</h2><div className="formInline"><Field label="Record ID" value={actionValue} onChange={setActionValue} /><Select label="Action" value={String(actionIdx)} onChange={v => { const i = Number(v); setActionIdx(i); setActionBody(page.actions![i].body); }} options={page.actions.map((a, i) => [String(i), a.label])} /></div><textarea className="jsonArea" rows={8} spellCheck={false} value={actionBody} onChange={e => setActionBody(e.target.value)} /><button className="primary" onClick={() => void runAction()}>Run</button></section>}
  </>);
}

/* ---------- catalog ---------- */
const QUOTE_LINE = { "item_id": 1, "description": "Consulting services", "quantity": 1, "unit_price": 1000, "discount_percent": 0, "tax_rate": 18 };
const M: ModuleCfg[] = [
  { id: 'finance', label: 'Finance', icon: '◉', pages: [
    { id: 'accounts', title: 'Chart of accounts', getPath: '/accounts', post: { label: 'Create account', path: '/accounts', body: json({ company_id: CID(), code: '4001', name: 'Sales Revenue', account_type: 'revenue' }) }, empty: 'No accounts yet.' },
    { id: 'invoices', title: 'Invoices', getPath: '/invoices?invoice_type=ar', post: { label: 'Create invoice', path: '/invoices', body: json({ company_id: CID(), party_id: 1, invoice_type: 'ar', invoice_date: '2026-11-17', due_date: '2026-12-17', currency: 'INR', lines: [{ description: 'Consulting services', quantity: 10, unit_price: 25000, tax_rate: 18 }] }) }, actions: [{ label: 'Post invoice', path: id => `/invoices/${id}/post`, body: '{}' }], empty: 'No AR invoices yet.', note: 'Creating an invoice reserves nothing; post it after review.' },
    { id: 'ap-invoices', title: 'Vendor invoices', getPath: '/invoices?invoice_type=ap', post: { label: 'Create AP invoice', path: '/invoices', body: json({ company_id: CID(), party_id: 2, invoice_type: 'ap', invoice_date: '2026-11-17', due_date: '2026-12-17', lines: [{ description: 'Software licence', quantity: 1, unit_price: 50000, tax_rate: 18 }] }) }, actions: [{ label: 'Post invoice', path: id => `/invoices/${id}/post`, body: '{}' }], empty: 'No AP invoices yet.' },
    { id: 'payments', title: 'Payments & allocations', post: { label: 'Record receipt / payment', path: '/payments', body: json({ company_id: CID(), party_id: 1, payment_type: 'receipt', reference: 'RCT-0001', payment_date: '2026-11-17', amount: 295000 }) }, actions: [{ label: 'Allocate payment to invoice', path: id => `/payments/${id}/allocate`, body: json({ invoice_id: 1, amount: 295000 }) }], note: 'Allocation links an open payment to an open invoice.' },
    { id: 'journal', title: 'Journal entries', post: { label: 'Create journal', path: '/journal-entries', body: json({ company_id: CID(), reference: 'JV-0001', description: 'Accrual entry', lines: [{ account_id: 1, debit: 10000, credit: 0 }, { account_id: 2, credit: 10000 }] }) }, actions: [{ label: 'Post journal', path: id => `/journal-entries/${id}/post`, body: '{}' }], note: 'Journals must be balanced before posting.' },
    { id: 'trial-balance', title: 'Trial balance', getPath: '/trial-balance', empty: 'Nothing posted yet.' },
    { id: 'ageing', title: 'AR/AP ageing', getPath: '/ageing', note: 'Open items bucketed by due date.' },
    { id: 'fiscal-periods', title: 'Fiscal periods', getPath: '/fiscal-periods', post: { label: 'Create period', path: '/fiscal-periods', body: json({ company_id: CID(), code: 'FY26-Q3', name: 'Oct-Dec 2026', start_date: '2026-10-01', end_date: '2026-12-31' }) } },
    { id: 'price-lists', title: 'Price lists', getPath: '/price-lists', post: { label: 'Create price list', path: '/price-lists', body: json({ company_id: CID(), code: 'STD', name: 'Standard', currency: 'INR', valid_from: '2026-11-17', valid_until: '2027-03-31', lines: [{ item_id: 1, unit_price: 25000 }] }) } },
    { id: 'bank-accounts', title: 'Bank accounts', getPath: '/bank-accounts', post: { label: 'Create bank account', path: '/bank-accounts', body: json({ company_id: CID(), code: 'HDFC-001', name: 'HDFC Current', currency: 'INR', gl_account_id: null }) } },
    { id: 'bank-recon', title: 'Bank reconciliation', getPath: '/bank-reconciliations', post: { label: 'New reconciliation', path: '/bank-reconciliations', body: json({ company_id: CID(), bank_account_id: 1, statement_date: '2026-11-17', opening_balance: 500000, closing_balance: 795000, notes: 'November statement' }) } },
    { id: 'fixed-assets', title: 'Fixed assets', getPath: '/fixed-assets', post: { label: 'Register asset', path: '/fixed-assets', body: json({ company_id: CID(), code: 'FA-0001', name: 'Laptop - Design team', purchase_date: '2026-11-17', cost: 85000, useful_life_months: 36, salvage_value: 5000, category: 'IT' }) }, actions: [{ label: 'Post monthly depreciation', path: id => `/fixed-assets/${id}/depreciate`, body: json({ months: 1 }) }] },
  ]},
  { id: 'sales', label: 'Sales', icon: '◍', pages: [
    { id: 'parties', title: 'Customers & vendors', getPath: '/parties', post: { label: 'Create party', path: '/parties', body: json({ company_id: CID(), party_type: 'customer', code: 'CUST-002', name: 'New Customer Pvt Ltd', credit_limit: 100000 }) }, empty: 'No parties yet.' },
    { id: 'quotes', title: 'Quotes', getPath: '/sales-quotes', post: { label: 'Create quote', path: '/sales-quotes', body: json({ company_id: CID(), customer_id: 1, quote_date: '2026-11-17', valid_until: '2026-12-31', currency: 'INR', lines: [QUOTE_LINE] }) }, actions: [{ label: 'Send quote', path: id => `/sales-quotes/${id}/send`, body: '{}' }] },
    { id: 'orders', title: 'Sales orders', getPath: '/sales-orders', post: { label: 'Create order', path: '/sales-orders', body: json({ company_id: CID(), customer_id: 1, order_date: '2026-11-17', lines: [QUOTE_LINE] }) }, actions: [{ label: 'Confirm order', path: id => `/sales-orders/${id}/confirm`, body: '{}' }, { label: 'Convert quote → order', path: id => `/sales-quotes/${id}/convert`, body: json({ order_date: '2026-11-17' }) }, { label: 'Create invoice from order', path: id => `/sales-orders/${id}/invoice`, body: json({ invoice_date: '2026-11-17', due_date: '2026-12-17' }) }, { label: 'Deliver order', path: id => `/sales-orders/${id}/deliver`, body: json({ idempotency_key: 'deliver-0001', warehouse_id: 1, delivery_date: '2026-11-17', lines: [{ sales_order_line_id: 1, quantity: 1 }] }) }], note: 'Integrity: quote → order → delivery → invoice.' },
  ]},
  { id: 'procurement', label: 'Procurement', icon: '◔', pages: [
    { id: 'purchase-requests', title: 'Purchase requests', getPath: '/purchase-requests', post: { label: 'Create request', path: '/purchase-requests', body: json({ company_id: CID(), request_date: '2026-11-17', required_date: '2026-12-01', requester: 'admin', department: 'Engineering', lines: [{ item_id: 1, description: 'Bench power supply', quantity: 2, estimated_unit_cost: 15000 }] }) }, actions: [{ label: 'Submit request', path: id => `/purchase-requests/${id}/submit`, body: '{}' }] },
    { id: 'rfqs', title: 'RFQs', getPath: '/rfqs', post: { label: 'Create RFQ', path: '/rfqs', body: json({ company_id: CID(), rfq_date: '2026-11-17', response_due: '2026-12-01', lines: [{ item_id: 1, description: 'Bench power supply', quantity: 2 }] }) }, actions: [{ label: 'Issue RFQ', path: id => `/rfqs/${id}/issue`, body: '{}' }, { label: 'Compare RFQ quotes', path: id => `/rfqs/${id}/comparison`, body: '{}', method: 'GET' }] },
    { id: 'supplier-quotes', title: 'Supplier quotes', post: { label: 'Record supplier quote', path: '/supplier-quotes', body: json({ company_id: CID(), rfq_id: 1, supplier_id: 2, number: 'SQ-0001', quote_date: '2026-11-17', valid_until: '2026-12-15', lines: [{ item_id: 1, description: 'Bench power supply', quantity: 2, unit_price: 14000, discount_percent: 0, tax_rate: 18 }] }) }, actions: [{ label: 'Convert quote → purchase order', path: id => `/supplier-quotes/${id}/convert`, body: json({ order_date: '2026-11-17' }) }], note: 'Totals must be consistent or conversion is rejected.' },
    { id: 'purchase-orders', title: 'Purchase orders', getPath: '/purchase-orders', post: { label: 'Create order', path: '/purchase-orders', body: json({ company_id: CID(), supplier_id: 2, order_date: '2026-11-17', lines: [{ item_id: 1, description: 'Bench power supply', quantity: 2, unit_price: 14000, discount_percent: 0, tax_rate: 18 }] }) }, actions: [{ label: 'Confirm order', path: id => `/purchase-orders/${id}/confirm`, body: '{}' }, { label: 'Receive goods', path: id => `/purchase-orders/${id}/receipts`, body: json({ receipt_date: '2026-11-17', number: 'GRN-0001', warehouse_id: 1, lines: [{ purchase_order_line_id: 1, quantity: 2 }] }) }, { label: 'Integrated supplier invoice', path: id => `/purchase-orders/${id}/integrated-supplier-invoice`, body: json({ idempotency_key: 'ap-invoice-0001', invoice_date: '2026-11-17', due_date: '2026-12-17', lines: [{ purchase_order_line_id: 1, invoiced_quantity: 2, unit_price: 14000, tax_rate: 18 }] }) }] },
    { id: 'landed-costs', title: 'Landed costs', getPath: '/landed-costs', post: { label: 'Allocate landed cost', path: '/landed-costs', body: json({ company_id: CID(), purchase_order_id: 1, description: 'Freight, insurance, customs', freight: 8000, insurance: 1500, duty: 9000, other_charges: 500 }) } },
  ]},
  { id: 'inventory', label: 'Inventory', icon: '◐', pages: [
    { id: 'items', title: 'Items', getPath: '/inventory/balances', note: 'Set item master data via SQL or API. Balances shown here.' },
    { id: 'balances', title: 'Stock balances', getPath: '/inventory/balances', empty: 'No stock on hand.' },
    { id: 'ledger', title: 'Stock ledger', getPath: '/inventory/ledger', note: 'Full immutable movement history.' },
    { id: 'movements', title: 'Stock movements', post: { label: 'Create movement', path: '/inventory/movements', body: json({ company_id: CID(), item_id: 1, warehouse_id: 1, movement_type: 'opening', movement_date: '2026-11-17', quantity: 100, unit_cost: 10000 }) } },
    { id: 'reorder', title: 'Reorder alerts', getPath: '/inventory/reorder-alerts', empty: 'All stocked well.' },
    { id: 'transfers', title: 'Stock transfers', post: { label: 'Create transfer', path: '/stock-transfers', body: json({ company_id: CID(), transfer_date: '2026-11-17', source_warehouse_id: 1, destination_warehouse_id: 2, lines: [{ item_id: 1, quantity: 10 }] }) }, actions: [{ label: 'Post transfer', path: id => `/stock-transfers/${id}/post`, body: '{}' }] },
    { id: 'reservations', title: 'Reservations', post: { label: 'Reserve stock', path: '/inventory/reservations', body: json({ company_id: CID(), item_id: 1, warehouse_id: 1, quantity: 5 }) } },
    { id: 'policies', title: 'Reorder policies', post: { label: 'Create policy', path: '/inventory/policies', body: json({ company_id: CID(), item_id: 1, warehouse_id: 1, tracking_mode: 'lot', reorder_point: 10, reorder_quantity: 50 }) } },
  ]},
  { id: 'crm', label: 'CRM', icon: '◓', pages: [
    { id: 'leads', title: 'Leads', getPath: '/leads', post: { label: 'Create lead', path: '/leads', body: json({ company_id: CID(), name: 'Priya Sharma - Procurement Head', email: 'priya@example.com', phone: '+91 98765 43210', source: 'trade_show', owner: 'admin' }) }, empty: 'No leads yet.' },
    { id: 'opportunities', title: 'Opportunities', getPath: '/opportunities', post: { label: 'Create opportunity', path: '/opportunities', body: json({ company_id: CID(), customer_id: 1, title: 'ACME - Annual support renewal', stage: 'proposal', amount: 1500000, probability: 60 }) }, empty: 'No opportunities yet.' },
  ]},
  { id: 'manufacturing', label: 'Manufacturing', icon: '◑', pages: [
    { id: 'boms', title: 'Bills of material', getPath: '/bill-of-materials', post: { label: 'Create BOM', path: '/bill-of-materials', body: json({ company_id: CID(), item_id: 2, revision: 1, description: 'Bench PSU assembly v1.0' }) }, actions: [{ label: 'Add component line', path: id => `/bill-of-materials/${id}/lines`, body: json({ bom_id: 1, component_id: 1, quantity: 1 }) }], empty: 'No BOMs yet.' },
    { id: 'work-orders', title: 'Work orders', getPath: '/work-orders', post: { label: 'Create work order', path: '/work-orders', body: json({ company_id: CID(), number: 'WO-0001', bom_id: 1, status: 'draft', planned_date: '2026-12-01', quantity: 10 }) }, empty: 'No work orders yet.' },
  ]},
  { id: 'projects', label: 'Projects', icon: '◒', pages: [
    { id: 'projects', title: 'Projects', getPath: '/projects', post: { label: 'Create project', path: '/projects', body: json({ company_id: CID(), code: 'PRJ-001', name: 'Plant automation rollout', start_date: '2026-11-17', status: 'planning', budget: 5000000 }) }, empty: 'No projects yet.' },
    { id: 'tasks', title: 'Project tasks', getPath: '/projects', post: { label: 'Add task', path: '/projects/1/tasks', body: json({ project_id: 1, name: 'Requirements workshop', order: 1, assigned_to: 'admin', due_date: '2026-11-30', estimated_hours: 16 }) }, note: 'Adds a task to project #1. Change project id in the path & body.' },
  ]},
  { id: 'maintenance', label: 'Maintenance & Assets', icon: '◕', pages: [
    { id: 'm-assets', title: 'Maintenance assets', getPath: '/maintenance-assets', post: { label: 'Register asset', path: '/maintenance-assets', body: json({ company_id: CID(), code: 'CNC-01', name: 'CNC Lathe #1', category: 'Shop floor', purchase_date: '2026-11-17', location: 'Plant A' }) }, empty: 'No assets yet.' },
    { id: 'm-work-orders', title: 'Maintenance work orders', getPath: '/maintenance-work-orders', post: { label: 'Create work order', path: '/maintenance-work-orders', body: json({ company_id: CID(), number: 'MWO-0001', asset_id: 1, requested_by: 'admin', work_description: 'Monthly preventive service', priority: 'medium' }) }, empty: 'No work orders yet.' },
  ]},
  { id: 'finance-ops', label: 'Consolidation & Treasury', icon: '◗', pages: [
    { id: 'consolidation', title: 'Ledger consolidation', getPath: '/ledger-consolidations', post: { label: 'New consolidation run', path: '/ledger-consolidations', body: json({ company_id: CID(), period_start: '2026-10-01', period_end: '2026-10-31', notes: 'Q3 consolidation' }) }, empty: 'No consolidations yet.' },
    { id: 'treasury', title: 'Treasury accounts', getPath: '/treasury-accounts', post: { label: 'Create treasury account', path: '/treasury-accounts', body: json({ company_id: CID(), code: 'HDFC-OPS', name: 'HDFC Operations', currency: 'INR', balance: 1250000, account_type: 'bank' }) }, empty: 'No treasury accounts yet.' },
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
    { id: 'saved-reports', title: 'Saved reports', getPath: '/reports/saved', post: { label: 'Save a report', path: '/reports/saved', body: json({ company_id: CID(), name: 'Monthly board pack', report_type: 'income_statement', parameters: {}, owner: 'admin', shared: true }) }, actions: [{ label: 'Schedule report (cron)', path: id => `/saved-reports/${id}/schedule`, body: json({ schedule_cron: '0 9 1 * *' }) }] },
    { id: 'run-report', title: 'Run a report', post: { label: 'Run report', path: '/reports/run', body: json({ company_id: CID(), report_type: 'trial_balance', parameters: {}, generated_by: 'admin' }) }, note: 'Returns the report payload directly.' },
  ]},
  { id: 'admin', label: 'Administration', icon: '◘', pages: [
    { id: 'users', title: 'Create user', post: { label: 'Create user', path: '/admin/users', body: json({ company_id: CID(), username: 'finance.manager', display_name: 'Finance Manager', password: 'ChangeMe-Strong-123!' }) }, note: 'Passwords must be ≥ 12 characters.' },
    { id: 'roles', title: 'Create role', post: { label: 'Create role', path: '/admin/roles', body: json({ company_id: CID(), code: 'finance_manager', name: 'Finance Manager', permissions: ['reports:read', 'data:write'] }) } },
    { id: 'approvals', title: 'Approvals', post: { label: 'Request approval', path: '/approvals', body: json({ company_id: CID(), entity_type: 'journal', entity_id: '1', action: 'journal_post', reason: 'Posting month-end accrual' }) }, actions: [{ label: 'Approve request', path: id => `/approvals/${id}/approve`, body: json({ expected_version: 1, reason: 'Approved after review' }) }], note: 'Maker-checker enforced: approver ≠ requester.' },
    { id: 'mfa', title: 'MFA (TOTP)', getPath: '/auth/mfa/setup', actions: [{ label: 'Verify & enable MFA', path: () => '/auth/mfa/verify', body: json({ company_id: CID(), code: '000000' }) }], note: 'Copy the secret into your authenticator, then verify.' },
  ]},
  { id: 'platform', label: 'Platform', icon: '▦', pages: [
    { id: 'notifications', title: 'Notifications', getPath: '/notifications', post: { label: 'Create notification', path: '/notifications', body: json({ company_id: CID(), user_id: null, title: 'Welcome to PeaOps', body: 'Your pilot tenant is ready.' }) }, empty: 'No notifications.' },
    { id: 'attachments', title: 'Attachments', getPath: '/attachments', post: { label: 'Register attachment', path: '/attachments', body: json({ company_id: CID(), entity_type: 'invoice', entity_id: '1', filename: 'PO-0001.pdf', file_path: '/var/lib/peaops/uploads/PO-0001.pdf', content_type: 'application/pdf' }) }, empty: 'No attachments.' },
    { id: 'events', title: 'Integration events', getPath: '/integration/events', empty: 'No integration activity yet.' },
    { id: 'trace', title: 'Integration trace', getPath: '/integration/trace', empty: 'No trace entries.' },
  ]},
];

const MODULES = M;

/* ---------- dashboard ---------- */
function Dashboard({ session }: { session: Session }) {
  const [kpi, setKpi] = useState<Record<string, unknown> | null>(null);
  const [ready, setReady] = useState<Record<string, unknown> | null>(null);
  const [errs, setErrs] = useState('');
  useEffect(() => {
    (async () => {
      try {
        const [k, r] = await Promise.all([api<Record<string, unknown>>(`/reports/kpis?company_id=${CID()}`), api<Record<string, unknown>>('/health/ready', {}, false)]);
        setKpi(k); setReady(r);
      } catch (e) { setErrs(e instanceof Error ? e.message : 'Failed to load dashboard'); }
    })();
  }, []);
  const tiles = [
    { label: 'API status', value: String(ready?.status ?? '…'), detail: ready ? String(ready.database ?? '') : '', tone: ready?.status === 'ready' ? 'ok' : 'warn' },
    { label: 'Sales this month', value: money(kpi?.sales_this_month ?? 0), detail: 'AR total billed', tone: '' },
    { label: 'Outstanding AR', value: money(kpi?.outstanding_ar ?? 0), detail: 'Open customer balances', tone: 'warn' },
    { label: 'Inventory value', value: money(kpi?.inventory_value ?? 0), detail: 'At average cost', tone: 'violet' },
  ];
  return (<>
    <header><div><p className="eyebrow">PEAOPS / COMMAND CENTER</p><h1>Good evening, {session.username}</h1><p>Everything here is wired to the local API.</p></div></header>
    {errs && <ErrorNote e={errs} />}
    <section className="heroGrid">{tiles.map(t => <div key={t.label} className={`metric ${t.tone}`}><span>{t.label}</span><strong>{t.value}</strong><small>{t.detail}</small></div>)}</section>
    <section className="panel"><p className="eyebrow">QUICK LINKS</p><h2>What teams do first</h2><div className="quickLinks"><a href="#/finance/invoices">Create an invoice →</a><a href="#/procurement/purchase-orders">Raise a purchase order →</a><a href="#/reports/sales-performance">Sales performance →</a><a href="#/admin/approvals">Pending approvals →</a></div></section>
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
