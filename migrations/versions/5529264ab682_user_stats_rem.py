"""User-stats rem

Revision ID: 5529264ab682
Revises: 6ff2f6be4b08
Create Date: 2025-02-07 17:00:34.771063

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5529264ab682'
down_revision = '6ff2f6be4b08'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('comments',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('parent_id', sa.VARCHAR(length=10), nullable=False),
    sa.Column('username', sa.String(length=80), nullable=True),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('upvotes', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['username'], ['user.username'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('comments')
    # ### end Alembic commands ###
