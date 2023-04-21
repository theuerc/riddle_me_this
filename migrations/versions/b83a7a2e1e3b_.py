"""empty message

Revision ID: b83a7a2e1e3b
Revises:
Create Date: 2023-04-13 19:20:14.200445

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b83a7a2e1e3b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=80), nullable=False),
    sa.Column('email', sa.String(length=80), nullable=False),
    sa.Column('password', sa.LargeBinary(length=128), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('first_name', sa.String(length=30), nullable=True),
    sa.Column('last_name', sa.String(length=30), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('is_admin', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_table('roles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('transcripts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('json_string', sa.String(), nullable=True),
    sa.Column('text', sa.Text(), nullable=True),
    sa.Column('language_code', sa.String(length=10), nullable=False),
    sa.Column('is_generated', sa.Boolean(), nullable=False),
    sa.Column('video_id', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    )
    op.create_table('videos',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('snippet_published_at', sa.DateTime(), nullable=True),
    sa.Column('snippet_channel_id', sa.String(), nullable=True),
    sa.Column('snippet_title', sa.String(), nullable=True),
    sa.Column('snippet_description', sa.Text(), nullable=True),
    sa.Column('snippet_channel_title', sa.String(), nullable=True),
    sa.Column('snippet_category_id', sa.String(), nullable=True),
    sa.Column('content_details_definition', sa.String(), nullable=True),
    sa.Column('content_details_licensed_content', sa.Boolean(), nullable=True),
    sa.Column('status_upload_status', sa.String(), nullable=True),
    sa.Column('status_privacy_status', sa.String(), nullable=True),
    sa.Column('status_license', sa.String(), nullable=True),
    sa.Column('status_public_stats_viewable', sa.Boolean(), nullable=True),
    sa.Column('status_made_for_kids', sa.Boolean(), nullable=True),
    sa.Column('statistics_view_count', sa.Integer(), nullable=True),
    sa.Column('statistics_like_count', sa.Integer(), nullable=True),
    sa.Column('statistics_favorite_count', sa.Integer(), nullable=True),
    sa.Column('statistics_comment_count', sa.Integer(), nullable=True),
    sa.Column('video_id', sa.String(), nullable=True),
    sa.Column('snippet_thumbnails_maxres_url', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('roles')
    op.drop_table('users')
    op.drop_table('transcripts')
    op.drop_table('videos')
    # ### end Alembic commands ###
