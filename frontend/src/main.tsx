import React, {useMemo, useState} from 'react';
import {createRoot} from 'react-dom/client';
import './styles.css';

type Nav = 'Dashboard'|'Receivables'|'Payables'|'Banking'|'Periods';
type MetricProps={title:string;value:string;hint:string;tone?:string};
const Metric=({title,value,hint,tone='teal'}:MetricProps)=><div className={`metric ${tone}`}><span>{title}</span><strong>{value}</strong><small>{hint}</small></div>;
const ageing=[['Current','₹4,82,000',48],['1–30','₹1,26,000',27],['31–60','₹68,000',15],['61–90','₹31,000',7],['90+','₹14,500',3]];
const activity=[['AR-00128','Acme Retail','₹74,340','Open'],['RCPT-00047','Orion Foods','₹42,000','Allocated'],['AP-00092','Northstar Supply','₹96,800','Due'],['AR-00127','Bluebird Labs','₹18,250','Partial']];

function App(){
 const [nav,setNav]=useState<Nav>('Dashboard');
 const heading=useMemo(()=>nav==='Dashboard'?'Finance command centre':nav,[nav]);
 return <div className="app">
  <aside><div className="brand"><i>pea</i>Ops <b>ERP</b></div><div className="scope">FINANCE • v0.2.0</div>
   <nav>{(['Dashboard','Receivables','Payables','Banking','Periods'] as Nav[]).map(x=><button className={nav===x?'active':''} onClick={()=>setNav(x)} key={x}><span>{x==='Dashboard'?'⌂':x==='Receivables'?'↗':x==='Payables'?'↙':x==='Banking'?'▣':'◫'}</span>{x}</button>)}</nav>
   <div className="foundation"><b>Core modules</b><small>Sales • Procurement • Inventory</small><small>Coming in planned releases</small></div>
  </aside>
  <main><header><div><p className="eyebrow">PEAOPS / FINANCE</p><h1>{heading}</h1><p>Control receivables, payables, cash and accounting periods.</p></div><div className="actions"><button className="ghost">View API</button><button className="primary">+ New transaction</button></div></header>
   <section className="metrics"><Metric title="Cash position" value="₹12.46L" hint="3 active bank accounts"/><Metric title="Receivables" value="₹7.22L" hint="₹1.14L overdue" tone="blue"/><Metric title="Payables" value="₹5.08L" hint="₹96.8K due this week" tone="amber"/><Metric title="Net working capital" value="₹14.60L" hint="AR + cash − AP" tone="violet"/></section>
   <section className="grid"><div className="panel wide"><div className="panelTitle"><div><p className="eyebrow">COLLECTIONS</p><h2>AR ageing</h2></div><button className="textBtn">Open report →</button></div><div className="ageing">{ageing.map(([label,value,pct])=><div className="ageRow" key={label as string}><b>{label}</b><div className="bar"><i style={{width:`${pct}%`}}/></div><strong>{value}</strong></div>)}</div></div>
    <div className="panel"><p className="eyebrow">PERIOD CONTROL</p><h2>November 2026</h2><div className="period"><span className="status">OPEN</span><p>Transactions can be posted through <b>30 Nov</b>.</p><button>Review fiscal periods</button></div></div></section>
   <section className="panel"><div className="panelTitle"><div><p className="eyebrow">LATEST</p><h2>Finance activity</h2></div><button className="textBtn">See all →</button></div><table><thead><tr><th>Document</th><th>Party</th><th>Amount</th><th>Status</th></tr></thead><tbody>{activity.map(r=><tr key={r[0]}><td><b>{r[0]}</b></td><td>{r[1]}</td><td>{r[2]}</td><td><span className={`pill ${r[3].toLowerCase()}`}>{r[3]}</span></td></tr>)}</tbody></table></section>
   <section className="capabilities"><div><b>✓ AR & AP invoices</b><small>Draft, post, collect and pay</small></div><div><b>✓ Partial allocations</b><small>Outstanding balance controls</small></div><div><b>✓ Ageing analysis</b><small>Current through 90+ days</small></div><div><b>✓ Numbering & periods</b><small>Controlled finance setup</small></div></section>
  </main>
 </div>
}
createRoot(document.getElementById('root')!).render(<App/>);
