"""Add address to parties and hsn_code to items — for GST e-invoice.

Revision ID: 20261119_0006
Revises: 20261119_0005
"""
from alembic import op
import sqlalchemy as sa
from app.core.db import Base
from app.domain import models  # noqa: F401

revision = '20261119_0006'
down_revision = '20261119_0005'
branch_labels = None
depends_on = None

def upgrade():
    bind = op.get_bind(); inspector = sa.inspect(bind)
    p_cols = {c['name'] for c in inspector.get_columns('parties')}
    if 'address' not in p_cols:
        op.add_column('parties', sa.Column('address', sa.Text(), nullable=False, server_default=sa.text("''")))
    i_cols = {c['name'] for c in inspector.get_columns('items')}
    if 'hsn_code' not in i_cols:
        op.add_column('items', sa.Column('hsn_code', sa.String(10), nullable=False, server_default=sa.text("''")))

def downgrade():
    bind = op.get_bind(); inspector = sa.inspect(bind)
    p_cols = {c['name'] for c in inspector.get_columns('parties')}
    if 'address' in p_cols:
        op.drop_column('parties', 'address')
    i_cols = {c['name'] for c in inspector.get_columns('items')}
    if 'hsn_code' in i_cols:
        op.drop_column('items', 'hsn_code')