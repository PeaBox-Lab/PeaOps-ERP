
from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.config import settings
from .policy import permission_for
from .rules import decode_access_token, authorize
import json

async def authorization_policy(request: Request, call_next):
    # Identify required permission
    required = permission_for(request.method, request.url.path)
    if not required:
        return await call_next(request)
    header = request.headers.get('authorization', '')
    if not header.startswith('Bearer '):
        return JSONResponse(status_code=401, content={'detail': 'Authentication required'})
    try:
        principal = decode_access_token(header[7:], settings.secret_key)
        authorize(set(principal.get('permissions', [])), required)
    except PermissionError as exc:
        return JSONResponse(status_code=403, content={'detail': str(exc)})
    except ValueError as exc:
        return JSONResponse(status_code=401, content={'detail': str(exc)})

    # Enforce company isolation for non-wildcard users
    perms = set(principal.get('permissions', []))
    is_wildcard = 'admin:*' in perms or 'super_admin:*' in perms
    if not is_wildcard:
        token_company = str(principal.get('company_id', ''))
        # query params
        q_company = request.query_params.getlist('company_id')
        if q_company and any(str(v) != token_company for v in q_company):
            return JSONResponse(status_code=403, content={'detail': 'Cross-company access denied'})
        # JSON body
        try:
            body_bytes = await request.body()
            if body_bytes:
                body = json.loads(body_bytes)
                if isinstance(body, dict):
                    body_cid = body.get('company_id')
                    if body_cid is not None and str(body_cid) != token_company:
                        return JSONResponse(status_code=403, content={'detail': 'Cross-company access denied'})
        except Exception:
            pass

    request.state.principal = principal
    return await call_next(request)
