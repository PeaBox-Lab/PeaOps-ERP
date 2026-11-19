"""Phase A expansion: SMTP settings table.

Revision ID: 20261118_0004
Revises: 20261118_0003
"""
from alembic import op
import sqlalchemy as sa
from app.core.db import Base
from app.domain import models  # noqa: F401

revision = '20261118_0004'
down_revision = '20261118_0003'
branch_labels = None
depends_on = None

def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if 'smtp_settings' not in set(inspector.get_table_names()):
        Base.metadata.tables['smtp_settings'].create(bind)

def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if 'smtp_settings' in set(inspector.get_table_names()):
        op.drop_table('smtp_settings')