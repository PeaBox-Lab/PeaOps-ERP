import React, {useMemo, useState} from 'react';
import {createRoot} from 'react-dom/client';
import './styles.css';

type Nav='Overview'|'Quotations'|'Orders'|'Customers'|'Price lists'|'Finance';
type MetricProps={label:string;value:string;detail:string;tone?:string};
const Metric=({label,value,detail,tone='green'}:MetricProps)=><div className={`metric ${tone}`}><span>{label}</span><strong>{value}</strong><small>{detail}</small></div>;
const pipeline=[['Draft','14','₹4.8L'],['Sent','22','₹9.6L'],['Accepted','8','₹3.1L'],['Converted','17','₹7.4L']];
const orders=[
 ['SO-00142','Nova Retail','18 Nov 2026','₹1,24,800','Confirmed'],
 ['SO-00141','Bluebird Labs','20 Nov 2026','₹86,400','Credit hold'],
 ['SO-00140','Orion Foods','17 Nov 2026','₹2,18,750','Ready to invoice'],
 ['SO-00139','Acme Retail','25 Nov 2026','₹74,340','Draft']
];

function App(){
 const [nav,setNav]=useState<Nav>('Overview');
 const title=useMemo(()=>nav==='Overview'?'Sales command centre':nav,[nav]);
 return <div className="app">
  <aside><div className="brand"><i>pea</i>Ops <b>ERP</b></div><div className="scope">SALES • v0.3.0</div>
   <nav>{(['Overview','Quotations','Orders','Customers','Price lists','Finance'] as Nav[]).map(x=><button className={nav===x?'active':''} onClick={()=>setNav(x)} key={x}><span>{x==='Overview'?'⌂':x==='Quotations'?'◇':x==='Orders'?'▤':x==='Customers'?'◉':x==='Price lists'?'₹':'↗'}</span>{x}</button>)}</nav>
   <div className="flow"><b>QUOTE TO CASH</b><small>Quote → Order → Promise</small><small>Invoice → Payment</small><div><i/><i/><i/><i/></div></div>
  </aside>
  <main><header><div><p className="eyebrow">PEAOPS / SALES</p><h1>{title}</h1><p>Move customer demand from quotation to a controlled, invoice-ready order.</p></div><div className="actions"><button className="ghost">Import prices</button><button className="primary">+ New quotation</button></div></header>
   <section className="metrics"><Metric label="Open pipeline" value="₹24.9L" detail="61 active quotations"/><Metric label="Confirmed orders" value="₹16.2L" detail="29 awaiting fulfilment" tone="blue"/><Metric label="Conversion rate" value="42.7%" detail="Rolling 30 days" tone="violet"/><Metric label="Credit holds" value="3" detail="₹2.14L pending review" tone="amber"/></section>
   <section className="workspace"><div className="panel pipeline"><div className="panelTitle"><div><p className="eyebrow">PIPELINE</p><h2>Quotation progression</h2></div><button className="textBtn">Open quotations →</button></div><div className="stages">{pipeline.map((x,i)=><div className="stage" key={x[0]}><span>{x[0]}</span><strong>{x[1]}</strong><small>{x[2]}</small>{i<3&&<em>›</em>}</div>)}</div><div className="conversion"><div><b>17 quotations converted</b><span>in the current period</span></div><div className="spark"><i/><i/><i/><i/><i/><i/><i/></div></div></div>
    <div className="panel promise"><p className="eyebrow">DELIVERY PROMISES</p><h2>This week</h2><div className="donut"><b>86%</b><span>on time</span></div><div className="promiseStats"><span><b>24</b> due</span><span><b>3</b> at risk</span><span><b>1</b> overdue</span></div></div></section>
   <section className="panel"><div className="panelTitle"><div><p className="eyebrow">ORDER CONTROL</p><h2>Orders requiring attention</h2></div><button className="textBtn">View all orders →</button></div><table><thead><tr><th>Order</th><th>Customer</th><th>Promise</th><th>Value</th><th>Status</th><th></th></tr></thead><tbody>{orders.map(r=><tr key={r[0]}><td><b>{r[0]}</b></td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td><span className={`pill ${r[4].toLowerCase().replaceAll(' ','-')}`}>{r[4]}</span></td><td>→</td></tr>)}</tbody></table></section>
   <section className="capabilities"><div><b>✓ Customer pricing</b><small>Dated price lists by item</small></div><div><b>✓ Quotations</b><small>Discount, tax and validity control</small></div><div><b>✓ Credit exposure</b><small>AR plus confirmed-order checks</small></div><div><b>✓ Invoice handoff</b><small>Confirmed order to draft AR invoice</small></div></section>
  </main>
 </div>
}
createRoot(document.getElementById('root')!).render(<App/>);
