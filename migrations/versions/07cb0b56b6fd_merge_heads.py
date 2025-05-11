"""merge heads

Revision ID: 07cb0b56b6fd
Revises: add_university_to_user, add_updated_at_to_friend_request
Create Date: 2025-05-11 00:52:03.118994

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '07cb0b56b6fd'
down_revision = ('add_university_to_user', 'add_updated_at_to_friend_request')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
