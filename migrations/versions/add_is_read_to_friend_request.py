"""add is_read to friend request

Revision ID: add_is_read_to_friend_request
Revises: f90a5c7fdb8e
Create Date: 2024-03-19

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_is_read_to_friend_request'
down_revision = 'f90a5c7fdb8e'  # Point to the latest revision
branch_labels = None
depends_on = None

def upgrade():
    # Add is_read column to friend_request table
    op.add_column('friend_request', sa.Column('is_read', sa.Boolean(), nullable=False, server_default='0'))

def downgrade():
    # Remove is_read column from friend_request table
    op.drop_column('friend_request', 'is_read') 