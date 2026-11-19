"""Phase A: force-password-change + posting-date for journals.

Revision ID: 20261118_0003
Revises: 20261117_0002
"""
from alembic import op
import sqlalchemy as sa
from app.core.db import Base
from app.domain import models  # noqa: F401

revision = '20261118_0003'
down_revision = '20261117_0002'
branch_labels = None
depends_on = None

def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    user_cols = {c['name'] for c in inspector.get_columns('users')}
    if 'must_change_password' not in user_cols:
        op.add_column('users', sa.Column('must_change_password', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    entry_cols = {c['name'] for c in inspector.get_columns('journal_entries')}
    if 'posting_date' not in entry_cols:
        op.add_column('journal_entries', sa.Column('posting_date', sa.Date(), nullable=True))

def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    user_cols = {c['name'] for c in inspector.get_columns('users')}
    if 'must_change_password' in user_cols:
        op.drop_column('users', 'must_change_password')
    entry_cols = {c['name'] for c in inspector.get_columns('journal_entries')}
    if 'posting_date' in entry_cols:
        op.drop_column('journal_entries', 'posting_date')