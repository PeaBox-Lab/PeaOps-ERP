"""Generic OpenID Connect client helpers."""
import httpx
from urllib.parse import urlencode


def _discover(issuer: str) -> dict:
    r = httpx.get(f"{issuer.rstrip('/')}/.well-known/openid-configuration", timeout=10)
    r.raise_for_status()
    return r.json()


def auth_url(issuer: str, client_id: str, redirect_uri: str, scopes: str, state: str) -> str:
    meta = _discover(issuer)
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": scopes,
        "state": state,
    }
    return f"{meta['authorization_endpoint']}?{urlencode(params)}"


def exchange_code(issuer: str, client_id: str, client_secret: str, redirect_uri: str, code: str) -> dict:
    meta = _discover(issuer)
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "client_secret": client_secret,
    }
    r = httpx.post(meta["token_endpoint"], data=data, timeout=10)
    r.raise_for_status()
    return r.json()


def userinfo(issuer: str, access_token: str) -> dict:
    meta = _discover(issuer)
    r = httpx.get(meta["userinfo_endpoint"], headers={"Authorization": f"Bearer {access_token}"}, timeout=10)
    r.raise_for_status()
    return r.json()
