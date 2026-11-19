"""Add SSO settings table.

Revision ID: 20261119_0007
Revises: 20261119_0006
"""
from alembic import op
import sqlalchemy as sa
from app.core.db import Base
from app.domain import models  # noqa: F401

revision = '20261119_0007'
down_revision = '20261119_0006'
branch_labels = None
depends_on = None

def upgrade():
    bind = op.get_bind(); inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())
    if 'sso_settings' not in tables:
        Base.metadata.tables['sso_settings'].create(bind)

def downgrade():
    bind = op.get_bind(); inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())
    if 'sso_settings' in tables:
        op.drop_table('sso_settings')