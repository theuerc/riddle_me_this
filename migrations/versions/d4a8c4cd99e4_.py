"""empty message

Revision ID: d4a8c4cd99e4
Revises: 572c4a5ab670
Create Date: 2023-04-18 17:48:51.909039

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd4a8c4cd99e4'
down_revision = '572c4a5ab670'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('access_token')
        batch_op.drop_column('refresh_token')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('refresh_token', sa.VARCHAR(), nullable=True))
        batch_op.add_column(sa.Column('access_token', sa.VARCHAR(), nullable=True))

    # ### end Alembic commands ###
