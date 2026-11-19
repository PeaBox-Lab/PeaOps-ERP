import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: Number(__ENV.VUS || 25),
  duration: __ENV.DURATION || '30s',
};

export function setup() {
  const BASE = __ENV.BASE_URL || 'http://localhost:8090';
  const login = http.post(`${BASE}/api/v1/auth/login`, JSON.stringify({
    company_id: 1,
    username: 'admin',
    password: 'Admin@123456',
  }), { headers: { 'Content-Type': 'application/json' } });

  check(login, { 'login 200': r => r.status === 200 });

  const token = login.json('access_token');
  return { BASE, TOKEN: token };
}

export default function (data) {
  const h = { headers: { Authorization: `Bearer ${data.TOKEN}` } };

  const endpoints = [
    `${data.BASE}/api/v1/health/ready`,
    `${data.BASE}/api/v1/items?company_id=1`,
    `${data.BASE}/api/v1/accounts?company_id=1`,
    `${data.BASE}/api/v1/reports/kpis?company_id=1`,
    `${data.BASE}/api/v1/reports/sales-performance?company_id=1`,
    `${data.BASE}/api/v1/invoices?company_id=1`,
    `${data.BASE}/api/v1/search?company_id=1&q=Bench&limit=5`,
  ];

  for (const url of endpoints) {
    const res = http.get(url, h);
    check(res, { '200': r => r.status === 200 });
  }
  sleep(1);
}