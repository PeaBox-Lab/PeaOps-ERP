import json, urllib.request
BASE = 'http://localhost:8090'
login = json.loads(urllib.request.urlopen(urllib.request.Request(f'{BASE}/api/v1/auth/login', data=json.dumps({'company_id':1,'username':'superadmin','password':'Sup3r-@dmin-P@ss!'}).encode(), headers={'Content-Type':'application/json'})).read())
h = {'Authorization': f"Bearer {login['access_token']}", 'Content-Type': 'text/plain'}
csv = 'sku,name,unit\nNEW-PSU,New PSU 12V,EA\nNEW-RES,Resistor 100R,EA'
imp = urllib.request.urlopen(urllib.request.Request(f'{BASE}/api/v1/admin/bulk-import?company_id=1&entity=items', data=csv.encode(), headers=h, method='POST'))
print('bulk-import:', imp.read().decode())
print('health:', json.loads(urllib.request.urlopen(urllib.request.Request(f'{BASE}/metrics/prometheus', headers={'Authorization': f"Bearer {login['access_token']}"})).read().decode().splitlines()[0]))