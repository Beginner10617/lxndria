"""moderation modified

Revision ID: d109d611c144
Revises: 529c866f7d2b
Create Date: 2025-02-18 21:52:25.670538

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd109d611c144'
down_revision = '529c866f7d2b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('moderators', schema=None) as batch_op:
        batch_op.add_column(sa.Column('requests_handled', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('moderators', schema=None) as batch_op:
        batch_op.drop_column('requests_handled')

    # ### end Alembic commands ###
