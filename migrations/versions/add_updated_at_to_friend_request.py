"""add updated_at to friend request

Revision ID: add_updated_at_to_friend_request
Revises: add_is_read_to_friend_request
Create Date: 2024-03-19

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'add_updated_at_to_friend_request'
down_revision = 'add_is_read_to_friend_request'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('friend_request', sa.Column('updated_at', sa.DateTime(), nullable=True))
    # Optionally, set updated_at to created_at for existing rows
    op.execute('UPDATE friend_request SET updated_at = created_at')

def downgrade():
    op.drop_column('friend_request', 'updated_at') 