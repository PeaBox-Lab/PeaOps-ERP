
"""v0.8.2 expansion: MFA, notifications, attachments, bank recon, fixed assets, CRM, manufacturing, projects, maintenance, consolidation, treasury.

Revision ID: 20261117_0002
Revises: 20261116_0001
"""
from alembic import op
import sqlalchemy as sa
from app.core.db import Base
from app.domain import models  # noqa: F401
revision='20261117_0002';down_revision='20261116_0001';branch_labels=None;depends_on=None

NEW_TABLES=['notifications','attachments','bank_reconciliations','fixed_assets','leads','opportunities','bill_of_materials','bill_of_material_lines','work_orders','projects','project_tasks','maintenance_assets','maintenance_work_orders','ledger_consolidations','treasury_accounts']

def _ensure_columns(table, columns):
    bind=op.get_bind(); inspector=sa.inspect(bind)
    existing={c['name'] for c in inspector.get_columns(table)}
    for col in columns:
        if col['name'] not in existing:
            op.add_column(table, sa.Column(col['name'], col['type'], nullable=col.get('nullable',True), server_default=col.get('server_default')))

def _ensure_tables():
    bind=op.get_bind(); inspector=sa.inspect(bind)
    existing=set(inspector.get_table_names())
    for name in NEW_TABLES:
        if name not in existing and name in Base.metadata.tables:
            Base.metadata.tables[name].create(bind)

def upgrade():
    _ensure_columns('users',[
        {'name':'mfa_secret','type':sa.String(64),'nullable':True},
        {'name':'mfa_enabled','type':sa.Boolean,'nullable':False,'server_default':sa.text('false')},
    ])
    _ensure_tables()

def downgrade():
    bind=op.get_bind(); inspector=sa.inspect(bind)
    existing=set(inspector.get_table_names())
    for name in NEW_TABLES:
        if name in existing:
            op.drop_table(name)
    cols={c['name'] for c in sa.inspect(bind).get_columns('users')}
    for name in ['mfa_enabled','mfa_secret']:
        if name in cols:
            op.drop_column('users',name)
