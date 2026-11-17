
import pytest
from app.security.policy import permission_for
from app.security.sod import validate_role_permissions,require_distinct_actor,require_version
from app.security.rules import create_refresh_token,hash_refresh_token

def test_health_is_public():assert permission_for('GET','/api/v1/health/ready') is None
def test_login_is_public():assert permission_for('POST','/api/v1/auth/login') is None
def test_reports_read_requires_view():assert permission_for('GET','/api/v1/reports/kpis')=='reports:view'
def test_general_read_requires_data_view():assert permission_for('GET','/api/v1/companies')=='data:view'
def test_journal_write_permission():assert permission_for('POST','/api/v1/journal-entries')=='finance:journal_create'
def test_inventory_write_permission():assert permission_for('POST','/api/v1/inventory/movements')=='inventory:write'
def test_unknown_write_is_protected():assert permission_for('POST','/api/v1/unknown')=='data:write'
def test_compatible_role_permissions():assert validate_role_permissions(['finance:journal_create','reports:view']) is True
def test_incompatible_finance_permissions_rejected():
 with pytest.raises(ValueError,match='Incompatible'):validate_role_permissions(['finance:journal_create','finance:journal_approve'])
def test_incompatible_admin_audit_rejected():
 with pytest.raises(ValueError,match='Incompatible'):validate_role_permissions(['admin:users','audit:security_review'])
def test_maker_cannot_approve_own_high_risk_action():
 with pytest.raises(PermissionError,match='Maker-checker'):require_distinct_actor('7','7','journal_post')
def test_distinct_checker_can_approve():assert require_distinct_actor('7','8','journal_post') is True
def test_low_risk_same_actor_allowed():assert require_distinct_actor('7','7','report_export') is True
def test_version_increments():assert require_version(3,3)==4
def test_stale_version_rejected():
 with pytest.raises(ValueError,match='Stale version'):require_version(2,3)
def test_refresh_tokens_are_random_and_hashable():
 a=create_refresh_token();b=create_refresh_token();assert a!=b and len(a)>=32 and hash_refresh_token(a)!=hash_refresh_token(b)

class _Approval:
 def __init__(self,company_id=1,entity_type='journal_entry',entity_id='7',action='journal_post',status='approved',approved_by='9'):
  self.company_id=company_id;self.entity_type=entity_type;self.entity_id=entity_id;self.action=action;self.status=status;self.approved_by=approved_by

def test_approved_record_binds_exact_action_and_entity():
 from app.security.sod import require_approved_record
 assert require_approved_record(_Approval(),1,'journal_entry','7','journal_post') is True

def test_approved_record_rejects_wrong_entity():
 from app.security.sod import require_approved_record
 with pytest.raises(ValueError,match='target entity'):require_approved_record(_Approval(),1,'journal_entry','8','journal_post')

def test_approved_record_rejects_wrong_action():
 from app.security.sod import require_approved_record
 with pytest.raises(ValueError,match='authorize'):require_approved_record(_Approval(),1,'journal_entry','7','credit_override')

def test_pending_record_cannot_authorize():
 from app.security.sod import require_approved_record
 with pytest.raises(ValueError,match='not approved'):require_approved_record(_Approval(status='pending',approved_by=None),1,'journal_entry','7','journal_post')

def test_cross_company_approval_rejected():
 from app.security.sod import require_approved_record
 with pytest.raises(PermissionError,match='different company'):require_approved_record(_Approval(company_id=2),1,'journal_entry','7','journal_post')
