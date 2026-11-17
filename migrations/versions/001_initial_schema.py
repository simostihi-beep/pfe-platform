"""initial_schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-11-17 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Table users
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column(
            'role',
            sa.Enum('student', 'supervisor', 'admin', name='user_role'),
            nullable=False,
            server_default='student',
        ),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # 2. Table projects
    op.create_table(
        'projects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('company', sa.String(length=255), nullable=True),
        sa.Column(
            'status',
            sa.Enum('draft', 'submitted', 'validated', 'rejected', name='project_status'),
            nullable=False,
            server_default='draft',
        ),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('supervisor_id', sa.Integer(), nullable=True),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(['student_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['supervisor_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_projects_id'), 'projects', ['id'], unique=False)
    op.create_index(op.f('ix_projects_student_id'), 'projects', ['student_id'], unique=False)
    op.create_index(op.f('ix_projects_supervisor_id'), 'projects', ['supervisor_id'], unique=False)

    # 3. Table milestones
    op.create_table(
        'milestones',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('progress', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_milestones_id'), 'milestones', ['id'], unique=False)
    op.create_index(op.f('ix_milestones_project_id'), 'milestones', ['project_id'], unique=False)

    # 4. Table defenses
    op.create_table(
        'defenses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('date_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('room', sa.String(length=100), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('project_id'),
    )
    op.create_index(op.f('ix_defenses_id'), 'defenses', ['id'], unique=False)

    # 5. Table d'association defense_jury
    op.create_table(
        'defense_jury',
        sa.Column('defense_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['defense_id'], ['defenses.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('defense_id', 'user_id'),
    )


def downgrade() -> None:
    op.drop_table('defense_jury')
    op.drop_index(op.f('ix_defenses_id'), table_name='defenses')
    op.drop_table('defenses')
    op.drop_index(op.f('ix_milestones_project_id'), table_name='milestones')
    op.drop_index(op.f('ix_milestones_id'), table_name='milestones')
    op.drop_table('milestones')
    op.drop_index(op.f('ix_projects_supervisor_id'), table_name='projects')
    op.drop_index(op.f('ix_projects_student_id'), table_name='projects')
    op.drop_index(op.f('ix_projects_id'), table_name='projects')
    op.drop_table('projects')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    op.execute('DROP TYPE IF EXISTS user_role')
    op.execute('DROP TYPE IF EXISTS project_status')
