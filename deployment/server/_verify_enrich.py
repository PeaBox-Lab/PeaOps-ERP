import json, urllib.request
BASE = 'http://localhost:8080'
login = json.loads(urllib.request.urlopen(urllib.request.Request(f'{BASE}/api/v1/auth/login', data=json.dumps({'company_id':1,'username':'admin','password':'Admin@123456'}).encode(), headers={'Content-Type':'application/json'})).read())
h = {'Authorization': f"Bearer {login['access_token']}"}
r = lambda p: json.loads(urllib.request.urlopen(urllib.request.Request(f'{BASE}/api/v1{p}', headers=h)).read())
print('accounts:', len(r('/accounts?company_id=1')))
print('fiscal periods:', [(p['code'], p['status']) for p in r('/fiscal-periods?company_id=1')])
print('parties:', len(r('/parties?company_id=1')))
print('items:', len(r('/inventory/balances?company_id=1')) if isinstance(r('/inventory/balances?company_id=1'), list) else '?')
print('kpis:', r('/reports/kpis?company_id=1'))
print('top customers:', [(c['customer'], c['sales']) for c in r('/reports/sales-performance?company_id=1')])