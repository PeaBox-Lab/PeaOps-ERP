import pytest
from app.security.rules import validate_password,hash_password,verify_password,normalize_permissions,authorize,create_access_token,decode_access_token

def test_strong_password_is_valid():assert validate_password('Strong-Password-2026') is True
@pytest.mark.parametrize('password',['short','alllowercase123!','ALLUPPERCASE123!','NoNumbersHere!','NoSymbolsHere123'])
def test_weak_password_rejected(password):
 with pytest.raises(ValueError):validate_password(password)
def test_password_hash_and_verify():
 encoded=hash_password('Strong-Password-2026',b'0123456789abcdef');assert encoded.startswith('pbkdf2_sha256$310000$');assert verify_password('Strong-Password-2026',encoded);assert not verify_password('Wrong-Password-2026',encoded)
def test_permission_normalization():assert normalize_permissions(['Finance:Post','finance:post',' reports:view '])==['finance:post','reports:view']
def test_explicit_permission():assert authorize({'finance:post'},'finance:post') is True
def test_domain_wildcard_permission():assert authorize({'finance:*'},'finance:post') is True
def test_admin_wildcard_permission():assert authorize({'admin:*'},'inventory:adjust') is True
def test_missing_permission_rejected():
 with pytest.raises(PermissionError):authorize({'reports:view'},'finance:post')
def test_access_token_round_trip():
 token=create_access_token('7',3,['reports:view'],'a-secret-key-with-more-than-32-characters',900,now=1000);data=decode_access_token(token,'a-secret-key-with-more-than-32-characters',now=1100);assert data['sub']=='7' and data['company_id']==3 and data['permissions']==['reports:view']
def test_expired_token_rejected():
 token=create_access_token('7',3,[],'a-secret-key-with-more-than-32-characters',60,now=1000)
 with pytest.raises(ValueError,match='expired'):decode_access_token(token,'a-secret-key-with-more-than-32-characters',now=1060)
def test_wrong_token_secret_rejected():
 token=create_access_token('7',3,[],'a-secret-key-with-more-than-32-characters',60,now=1000)
 with pytest.raises(ValueError,match='signature'):decode_access_token(token,'another-secret-key-with-more-than-32-chars',now=1010)
