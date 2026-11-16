import logging,time,uuid
from fastapi import Request
logger=logging.getLogger("peaops.request")

async def security_headers(request:Request,call_next):
    request_id=request.headers.get('x-request-id') or str(uuid.uuid4());started=time.perf_counter();status=500
    try:
        response=await call_next(request);status=response.status_code
        response.headers['X-Request-ID']=request_id
        response.headers['X-Content-Type-Options']='nosniff'
        response.headers['X-Frame-Options']='DENY'
        response.headers['Referrer-Policy']='no-referrer'
        response.headers['Permissions-Policy']='camera=(), microphone=(), geolocation=()'
        response.headers['Cache-Control']='no-store' if request.url.path.startswith('/api/') else 'no-cache'
        response.headers['Server-Timing']=f'app;dur={(time.perf_counter()-started)*1000:.2f}'
        return response
    finally:
        logger.info("request",extra={"request_id":request_id,"method":request.method,"path":request.url.path,"status":status,"duration_ms":round((time.perf_counter()-started)*1000,2)})
