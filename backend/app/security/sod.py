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
