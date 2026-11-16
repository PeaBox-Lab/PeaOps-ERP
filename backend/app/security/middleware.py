from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.config import settings
from .policy import permission_for
from .rules import decode_access_token,authorize

async def authorization_policy(request:Request,call_next):
    required=permission_for(request.method,request.url.path)
    if not required:return await call_next(request)
    header=request.headers.get('authorization','')
    if not header.startswith('Bearer '):return JSONResponse(status_code=401,content={'detail':'Authentication required'})
    try:
        principal=decode_access_token(header[7:],settings.secret_key);authorize(set(principal.get('permissions',[])),required)
        request.state.principal=principal
    except PermissionError as exc:return JSONResponse(status_code=403,content={'detail':str(exc)})
    except ValueError as exc:return JSONResponse(status_code=401,content={'detail':str(exc)})
    return await call_next(request)
