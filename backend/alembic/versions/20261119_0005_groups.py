"""Company groups for holding-company / multi-company deployments.

Revision ID: 20261119_0005
Revises: 20261118_0004
"""
from alembic import op
import sqlalchemy as sa
from app.core.db import Base
from app.domain import models  # noqa: F401

revision = '20261119_0005'
down_revision = '20261118_0004'
branch_labels = None
depends_on = None

def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())
    for name in ["groups", "group_companies", "group_members"]:
        if name not in tables and name in Base.metadata.tables:
            Base.metadata.tables[name].create(bind)

def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())
    for name in ["group_members", "group_companies", "groups"]:
        if name in tables:
            op.drop_table(name)