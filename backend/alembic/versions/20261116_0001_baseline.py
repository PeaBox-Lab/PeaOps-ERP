
"""PeaOps v0.8 production baseline schema.

Revision ID: 20261116_0001
Revises: None
"""
from alembic import op
from app.core.db import Base
from app.domain import models  # noqa: F401
revision='20261116_0001';down_revision=None;branch_labels=None;depends_on=None

def upgrade():
    Base.metadata.create_all(bind=op.get_bind(),checkfirst=True)

def downgrade():
    Base.metadata.drop_all(bind=op.get_bind(),checkfirst=True)
