
HIGH_RISK_ACTIONS={'journal_post','credit_override','inventory_adjustment','supplier_match_override','role_assignment'}
INCOMPATIBLE={
 'finance:journal_create':{'finance:journal_approve'},
 'procurement:request':{'procurement:approve'},
 'admin:users':{'audit:security_review'},
}

def validate_role_permissions(permissions:list[str]):
    values=set(permissions)
    for permission,conflicts in INCOMPATIBLE.items():
        if permission in values and values.intersection(conflicts):raise ValueError(f'Incompatible permissions: {permission} and {sorted(values.intersection(conflicts))[0]}')
    return True

def require_distinct_actor(created_by:str|None,acting_user:str,action:str):
    if action in HIGH_RISK_ACTIONS and created_by and str(created_by)==str(acting_user):raise PermissionError(f'Maker-checker violation for {action}')
    return True

def require_version(expected:int,current:int):
    if expected!=current:raise ValueError(f'Stale version: expected={expected}, current={current}')
    return current+1


def require_approved_record(record, company_id:int, entity_type:str, entity_id:str, action:str):
    if record is None: raise ValueError('Approval record not found')
    if record.company_id != company_id: raise PermissionError('Approval belongs to a different company')
    if record.entity_type != entity_type or str(record.entity_id) != str(entity_id): raise ValueError('Approval does not match target entity')
    if record.action != action: raise ValueError('Approval does not authorize this action')
    if record.status != 'approved' or not record.approved_by: raise ValueError('Approval is not approved')
    return True
