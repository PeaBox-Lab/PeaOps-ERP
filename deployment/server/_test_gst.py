import urllib.request, json
req = urllib.request.Request('http://localhost:8000/api/v1/invoices/1/gst-einvoice', method='POST')
try:
    resp = urllib.request.urlopen(req)
    print('STATUS', resp.status)
    print(resp.read().decode())
except urllib.error.HTTPError as e:
    print('ERROR', e.code, e.reason)
    print(e.read().decode())