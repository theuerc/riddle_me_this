"""empty message

Revision ID: 59a9cca10714
Revises: b149cbc48f51
Create Date: 2023-04-18 18:27:09.145579

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '59a9cca10714'
down_revision = 'b149cbc48f51'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('transcripts', schema=None) as batch_op:
        batch_op.alter_column('language_code',
               existing_type=sa.VARCHAR(length=10),
               nullable=True)

    with op.batch_alter_table('videos', schema=None) as batch_op:
        batch_op.add_column(sa.Column('video_id', sa.String(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('videos', schema=None) as batch_op:
        batch_op.drop_column('video_id')

    with op.batch_alter_table('transcripts', schema=None) as batch_op:
        batch_op.alter_column('language_code',
               existing_type=sa.VARCHAR(length=10),
               nullable=False)

    # ### end Alembic commands ###
