
import base64, hashlib, hmac, json, os, secrets, time

PBKDF2_ITERATIONS=310_000


def validate_password(password:str):
    if len(password)<12:raise ValueError('Password must contain at least 12 characters')
    if not any(c.islower() for c in password):raise ValueError('Password requires a lowercase letter')
    if not any(c.isupper() for c in password):raise ValueError('Password requires an uppercase letter')
    if not any(c.isdigit() for c in password):raise ValueError('Password requires a number')
    if not any(not c.isalnum() for c in password):raise ValueError('Password requires a symbol')
    return True


def hash_password(password:str,salt:bytes|None=None):
    validate_password(password);salt=salt or os.urandom(16)
    digest=hashlib.pbkdf2_hmac('sha256',password.encode(),salt,PBKDF2_ITERATIONS)
    return f'pbkdf2_sha256${PBKDF2_ITERATIONS}${base64.urlsafe_b64encode(salt).decode()}${base64.urlsafe_b64encode(digest).decode()}'


def verify_password(password:str,encoded:str):
    try:
        algorithm,iterations,salt,digest=encoded.split('$');assert algorithm=='pbkdf2_sha256'
        actual=hashlib.pbkdf2_hmac('sha256',password.encode(),base64.urlsafe_b64decode(salt),int(iterations))
        return hmac.compare_digest(actual,base64.urlsafe_b64decode(digest))
    except (ValueError,AssertionError):return False


def normalize_permissions(values:list[str]):
    normalized=sorted(set(x.strip().lower() for x in values if x and x.strip()))
    if any(' ' in x for x in normalized):raise ValueError('Permissions cannot contain spaces')
    return normalized


def authorize(user_permissions:set[str],required:str):
    if 'admin:*' in user_permissions or 'super_admin:*' in user_permissions or required in user_permissions:return True
    domain=required.split(':',1)[0]+':*'
    if domain in user_permissions:return True
    raise PermissionError(f'Missing permission: {required}')


def _encode(value:bytes):return base64.urlsafe_b64encode(value).decode().rstrip('=')
def _decode(value:str):return base64.urlsafe_b64decode(value+'='*(-len(value)%4))


def create_access_token(subject:str,company_id:int,permissions:list[str],secret:str,expires_seconds:int=900,now:int|None=None):
    if len(secret)<32:raise ValueError('Token secret must contain at least 32 characters')
    if expires_seconds<60 or expires_seconds>86400:raise ValueError('Token lifetime must be between 60 and 86400 seconds')
    issued=now or int(time.time());header={'alg':'HS256','typ':'JWT'}
    payload={'sub':subject,'company_id':company_id,'permissions':normalize_permissions(permissions),'iat':issued,'exp':issued+expires_seconds,'jti':secrets.token_hex(12), 'typ':'access'}
    body=f'{_encode(json.dumps(header,separators=(",",":")).encode())}.{_encode(json.dumps(payload,separators=(",",":")).encode())}'
    signature=_encode(hmac.new(secret.encode(),body.encode(),hashlib.sha256).digest())
    return f'{body}.{signature}'


def decode_access_token(token:str,secret:str,now:int|None=None):
    try:
        header,payload,signature=token.split('.');body=f'{header}.{payload}'
        expected=_encode(hmac.new(secret.encode(),body.encode(),hashlib.sha256).digest())
        if not hmac.compare_digest(expected,signature):raise ValueError('Invalid token signature')
        data=json.loads(_decode(payload));current=now or int(time.time())
        if current>=int(data['exp']):raise ValueError('Token expired')
        return data
    except (ValueError,KeyError,json.JSONDecodeError) as exc:
        raise ValueError(str(exc) or 'Invalid access token')


def create_refresh_token():
    return secrets.token_urlsafe(48)

def hash_refresh_token(token:str):
    return hashlib.sha256(token.encode()).hexdigest()
