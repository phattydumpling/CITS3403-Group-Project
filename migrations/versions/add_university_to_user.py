"""add university to user

Revision ID: add_university_to_user
Revises: 6dcae28483c9
Create Date: 2024-05-05

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_university_to_user'
down_revision = '6dcae28483c9'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('user', sa.Column('university', sa.String(length=120), nullable=True))

def downgrade():
    op.drop_column('user', 'university') 