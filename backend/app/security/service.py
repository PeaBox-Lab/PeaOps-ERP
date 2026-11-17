
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.db import get_db
from app.domain.models import User, RolePermission, UserRole
from .rules import decode_access_token, authorize

bearer=HTTPBearer(auto_error=False)


def current_principal(credentials:HTTPAuthorizationCredentials|None=Depends(bearer)):
    if not credentials:raise HTTPException(401,'Authentication required')
    try:return decode_access_token(credentials.credentials,settings.secret_key)
    except ValueError as exc:raise HTTPException(401,str(exc))


def require_permission(permission:str):
    def dependency(principal=Depends(current_principal)):
        try:authorize(set(principal.get('permissions',[])),permission)
        except PermissionError as exc:raise HTTPException(403,str(exc))
        return principal
    return dependency


def permissions_for_user(db:Session,user_id:int):
    q=(select(RolePermission.permission).join(UserRole,UserRole.role_id==RolePermission.role_id).where(UserRole.user_id==user_id))
    return sorted(set(db.scalars(q).all()))
