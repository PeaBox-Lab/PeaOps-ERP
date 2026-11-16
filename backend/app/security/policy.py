from dataclasses import dataclass

@dataclass(frozen=True)
class RoutePolicy:
    method:str
    prefix:str
    permission:str

POLICIES=[
 RoutePolicy('POST','/api/v1/companies','admin:company'),RoutePolicy('POST','/api/v1/accounts','finance:configure'),
 RoutePolicy('POST','/api/v1/journal-entries','finance:journal_create'),RoutePolicy('POST','/api/v1/journal-entries/','finance:journal_post'),
 RoutePolicy('POST','/api/v1/invoices','finance:invoice'),RoutePolicy('POST','/api/v1/payments','finance:payment'),
 RoutePolicy('POST','/api/v1/sales-','sales:write'),RoutePolicy('POST','/api/v1/price-lists','sales:configure'),
 RoutePolicy('POST','/api/v1/purchase-','procurement:write'),RoutePolicy('POST','/api/v1/rfqs','procurement:write'),
 RoutePolicy('POST','/api/v1/supplier-','procurement:write'),RoutePolicy('POST','/api/v1/inventory/','inventory:write'),
 RoutePolicy('POST','/api/v1/stock-transfers','inventory:transfer'),RoutePolicy('POST','/api/v1/integration/','integration:operate'),
 RoutePolicy('POST','/api/v1/reports/saved','reports:manage'),RoutePolicy('POST','/api/v1/reports/run','reports:run'),
]
PUBLIC_PREFIXES=('/','/docs','/openapi.json','/api/v1/health/','/api/v1/auth/login','/api/v1/auth/refresh')

def permission_for(method:str,path:str):
    if method=='OPTIONS' or path=='/' or any(path.startswith(x) for x in PUBLIC_PREFIXES[1:]):return None
    if method=='GET':return 'reports:view' if path.startswith('/api/v1/reports/') else 'data:view'
    matches=[x for x in POLICIES if x.method==method and path.startswith(x.prefix)]
    if not matches:return 'data:write'
    return max(matches,key=lambda x:len(x.prefix)).permission
