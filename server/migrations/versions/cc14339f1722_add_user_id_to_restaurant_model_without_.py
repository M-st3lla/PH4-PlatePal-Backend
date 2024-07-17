"""Add user_id to Restaurant model

Revision ID: 809fc7236946
Revises: <previous_revision_id>
Create Date: <date>

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '809fc7236946'
down_revision = 'valid_previous_revision_id'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('restaurant', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key('fk_restaurant_user', 'user', ['user_id'], ['id'])


def downgrade():
    with op.batch_alter_table('restaurant', schema=None) as batch_op:
        batch_op.drop_constraint('fk_restaurant_user', type_='foreignkey')
        batch_op.drop_column('user_id')
