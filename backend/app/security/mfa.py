import base64, hashlib, hmac, time, secrets

def totp_code(secret: str, step: int = 30, digits: int = 6) -> str:
    counter = int(time.time()) // step
    msg = counter.to_bytes(8, "big")
    key = base64.b32decode(secret, casefold=True)
    h = hmac.new(key, msg, hashlib.sha1).digest()
    offset = h[-1] & 0x0f
    code = (int.from_bytes(h[offset:offset+4], "big") & 0x7fffffff) % (10 ** digits)
    return str(code).zfill(digits)

def verify_totp(secret: str, code: str, step: int = 30, digits: int = 6) -> bool:
    return totp_code(secret, step, digits) == code

def generate_secret() -> str:
    return base64.b32encode(secrets.token_bytes(20)).decode()