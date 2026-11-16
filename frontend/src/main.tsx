import React, {useMemo, useState} from 'react';
import {createRoot} from 'react-dom/client';
import './styles.css';

type Nav='Overview'|'Requests'|'RFQs'|'Purchase orders'|'Receipts'|'Suppliers'|'Finance';
type MetricProps={label:string;value:string;detail:string;tone?:string};
const Metric=({label,value,detail,tone='green'}:MetricProps)=><div className={`metric ${tone}`}><span>{label}</span><strong>{value}</strong><small>{detail}</small></div>;
const sourcing=[['Requests','18','₹8.4L'],['RFQs issued','11','₹6.9L'],['Quotes received','27','3.4 / RFQ'],['Orders placed','14','₹5.8L']];
const orders=[
 ['PO-00128','Northstar Supply','18 Nov 2026','₹1,86,400','Partial receipt'],
 ['PO-00127','Metro Components','20 Nov 2026','₹74,250','Confirmed'],
 ['PO-00126','Pioneer Packaging','17 Nov 2026','₹2,08,800','Ready to receive'],
 ['PO-00125','Axis Industrial','25 Nov 2026','₹96,500','Draft']
];
const comparisons=[['RFQ-00038','3 suppliers','₹18,600','₹2,450'],['RFQ-00037','4 suppliers','₹64,800','₹7,200'],['RFQ-00036','2 suppliers','₹1,12,400','₹3,600']];

function App(){
 const [nav,setNav]=useState<Nav>('Overview');
 const title=useMemo(()=>nav==='Overview'?'Procurement command centre':nav,[nav]);
 return <div className="app">
  <aside><div className="brand"><i>pea</i>Ops <b>ERP</b></div><div className="scope">PROCUREMENT • v0.4.0</div>
   <nav>{(['Overview','Requests','RFQs','Purchase orders','Receipts','Suppliers','Finance'] as Nav[]).map(x=><button className={nav===x?'active':''} onClick={()=>setNav(x)} key={x}><span>{x==='Overview'?'⌂':x==='Requests'?'≡':x==='RFQs'?'◇':x==='Purchase orders'?'▤':x==='Receipts'?'↓':x==='Suppliers'?'◉':'↗'}</span>{x}</button>)}</nav>
   <div className="flow"><b>PROCURE TO PAY</b><small>Request → RFQ → Compare</small><small>PO → Receipt → Invoice</small><div><i/><i/><i/><i/></div></div>
  </aside>
  <main><header><div><p className="eyebrow">PEAOPS / PROCUREMENT</p><h1>{title}</h1><p>Turn internal demand into compared, controlled and receipt-ready purchase orders.</p></div><div className="actions"><button className="ghost">Supplier master</button><button className="primary">+ New request</button></div></header>
   <section className="metrics"><Metric label="Open commitments" value="₹18.7L" detail="32 confirmed purchase orders"/><Metric label="Sourcing pipeline" value="₹15.3L" detail="18 requests and 11 RFQs" tone="blue"/><Metric label="Identified savings" value="₹1.24L" detail="From supplier comparisons" tone="violet"/><Metric label="Late promises" value="4" detail="₹2.86L needs attention" tone="amber"/></section>
   <section className="workspace"><div className="panel sourcing"><div className="panelTitle"><div><p className="eyebrow">SOURCING</p><h2>Request-to-order progression</h2></div><button className="textBtn">Open workspace →</button></div><div className="stages">{sourcing.map((x,i)=><div className="stage" key={x[0]}><span>{x[0]}</span><strong>{x[1]}</strong><small>{x[2]}</small>{i<3&&<em>›</em>}</div>)}</div><div className="cycle"><div><b>4.8 days</b><span>average request-to-order cycle</span></div><div className="bars"><i/><i/><i/><i/><i/><i/><i/></div></div></div>
    <div className="panel compare"><div className="panelTitle"><div><p className="eyebrow">QUOTE COMPARISON</p><h2>Recent opportunities</h2></div></div>{comparisons.map(x=><div className="compareRow" key={x[0]}><div><b>{x[0]}</b><small>{x[1]}</small></div><div><b>{x[2]}</b><small>best total</small></div><span>Save {x[3]}</span></div>)}</div></section>
   <section className="panel"><div className="panelTitle"><div><p className="eyebrow">ORDER CONTROL</p><h2>Purchase orders requiring attention</h2></div><button className="textBtn">View all orders →</button></div><table><thead><tr><th>Order</th><th>Supplier</th><th>Promise</th><th>Value</th><th>Status</th><th></th></tr></thead><tbody>{orders.map(r=><tr key={r[0]}><td><b>{r[0]}</b></td><td>{r[1]}</td><td>{r[2]}</td><td>{r[3]}</td><td><span className={`pill ${r[4].toLowerCase().replaceAll(' ','-')}`}>{r[4]}</span></td><td>→</td></tr>)}</tbody></table></section>
   <section className="capabilities"><div><b>✓ Purchase requests</b><small>Need, owner and required date</small></div><div><b>✓ Competitive RFQ</b><small>Supplier responses and comparison</small></div><div><b>✓ Purchase orders</b><small>Controlled confirmation and promises</small></div><div><b>✓ Partial receipts</b><small>Remaining quantity protection</small></div></section>
  </main>
 </div>
}
createRoot(document.getElementById('root')!).render(<App/>);
