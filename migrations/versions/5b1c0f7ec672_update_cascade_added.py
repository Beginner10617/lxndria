"""Update cascade added

Revision ID: 5b1c0f7ec672
Revises: 798598a5bc4c
Create Date: 2025-03-15 21:42:54.283910

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5b1c0f7ec672'
down_revision = '798598a5bc4c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('bookmarks', schema=None) as batch_op:
        batch_op.drop_constraint('bookmarks_username_fkey', type_='foreignkey')
        batch_op.drop_constraint('bookmarks_discussion_id_fkey', type_='foreignkey')
        batch_op.drop_constraint('bookmarks_problem_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'discussion', ['discussion_id'], ['id'], onupdate='CASCADE')
        batch_op.create_foreign_key(None, 'problem', ['problem_id'], ['id'], onupdate='CASCADE')
        batch_op.create_foreign_key(None, 'user', ['username'], ['username'], onupdate='CASCADE')

    with op.batch_alter_table('comments', schema=None) as batch_op:
        batch_op.drop_constraint('comments_username_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'user', ['username'], ['username'], onupdate='CASCADE')

    with op.batch_alter_table('discussion', schema=None) as batch_op:
        batch_op.drop_constraint('discussion_author_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'user', ['author'], ['username'], onupdate='CASCADE')

    with op.batch_alter_table('moderators', schema=None) as batch_op:
        batch_op.drop_constraint('moderators_username_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'user', ['username'], ['username'], onupdate='CASCADE')

    with op.batch_alter_table('notifications', schema=None) as batch_op:
        batch_op.drop_constraint('notifications_username_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'user', ['username'], ['username'], onupdate='CASCADE')

    with op.batch_alter_table('problem_attempts', schema=None) as batch_op:
        batch_op.drop_constraint('problem_attempts_problem_id_fkey', type_='foreignkey')
        batch_op.drop_constraint('problem_attempts_username_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'problem', ['problem_id'], ['id'], onupdate='CASCADE')
        batch_op.create_foreign_key(None, 'user', ['username'], ['username'], onupdate='CASCADE')

    with op.batch_alter_table('profile', schema=None) as batch_op:
        batch_op.drop_constraint('profile_username_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'user', ['username'], ['username'], onupdate='CASCADE')

    with op.batch_alter_table('report', schema=None) as batch_op:
        batch_op.drop_constraint('report_handled_by_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'user', ['handled_by'], ['username'], onupdate='CASCADE')

    with op.batch_alter_table('solutions', schema=None) as batch_op:
        batch_op.drop_constraint('solutions_problem_id_fkey', type_='foreignkey')
        batch_op.drop_constraint('solutions_username_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'user', ['username'], ['username'], onupdate='CASCADE')
        batch_op.create_foreign_key(None, 'problem', ['problem_id'], ['id'], onupdate='CASCADE')

    with op.batch_alter_table('upvotes', schema=None) as batch_op:
        batch_op.drop_constraint('upvotes_solution_id_fkey', type_='foreignkey')
        batch_op.drop_constraint('upvotes_username_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'user', ['username'], ['username'], onupdate='CASCADE')
        batch_op.create_foreign_key(None, 'solutions', ['solution_id'], ['id'], onupdate='CASCADE')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('upvotes', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('upvotes_username_fkey', 'user', ['username'], ['username'])
        batch_op.create_foreign_key('upvotes_solution_id_fkey', 'solutions', ['solution_id'], ['id'])

    with op.batch_alter_table('solutions', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('solutions_username_fkey', 'user', ['username'], ['username'])
        batch_op.create_foreign_key('solutions_problem_id_fkey', 'problem', ['problem_id'], ['id'])

    with op.batch_alter_table('report', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('report_handled_by_fkey', 'user', ['handled_by'], ['username'])

    with op.batch_alter_table('profile', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('profile_username_fkey', 'user', ['username'], ['username'])

    with op.batch_alter_table('problem_attempts', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('problem_attempts_username_fkey', 'user', ['username'], ['username'])
        batch_op.create_foreign_key('problem_attempts_problem_id_fkey', 'problem', ['problem_id'], ['id'])

    with op.batch_alter_table('notifications', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('notifications_username_fkey', 'user', ['username'], ['username'])

    with op.batch_alter_table('moderators', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('moderators_username_fkey', 'user', ['username'], ['username'])

    with op.batch_alter_table('discussion', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('discussion_author_fkey', 'user', ['author'], ['username'])

    with op.batch_alter_table('comments', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('comments_username_fkey', 'user', ['username'], ['username'])

    with op.batch_alter_table('bookmarks', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('bookmarks_problem_id_fkey', 'problem', ['problem_id'], ['id'])
        batch_op.create_foreign_key('bookmarks_discussion_id_fkey', 'discussion', ['discussion_id'], ['id'])
        batch_op.create_foreign_key('bookmarks_username_fkey', 'user', ['username'], ['username'])

    # ### end Alembic commands ###
