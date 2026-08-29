"""feat: improve task model

Revision ID: 2beaea6aa168
Revises: 945e36036a97
Create Date: 2026-08-29 16:35:31.432359

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2beaea6aa168'
down_revision: Union[str, Sequence[str], None] = '945e36036a97'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.String(length=255), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('kb_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('progress', sa.Integer(), nullable=False),
        sa.Column('retry_count', sa.Integer(), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),

        sa.ForeignKeyConstraint(
            ['owner_id'],
            ['users.id'],
        ),
        sa.ForeignKeyConstraint(
            ['kb_id'],
            ['knowledge_base.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('task_id'),
    )

    op.create_index(
        'ix_tasks_id',
        'tasks',
        ['id'],
        unique=False,
    )

    op.create_index(
        'ix_tasks_task_id',
        'tasks',
        ['task_id'],
        unique=True,
    )

    op.create_index(
        'ix_tasks_owner_id',
        'tasks',
        ['owner_id'],
        unique=False,
    )

    op.create_index(
        'ix_tasks_kb_id',
        'tasks',
        ['kb_id'],
        unique=False,
    )

    op.create_index(
        'ix_tasks_status',
        'tasks',
        ['status'],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_tasks_status', table_name='tasks')
    op.drop_index('ix_tasks_kb_id', table_name='tasks')
    op.drop_index('ix_tasks_owner_id', table_name='tasks')
    op.drop_index('ix_tasks_task_id', table_name='tasks')
    op.drop_index('ix_tasks_id', table_name='tasks')
    op.drop_table('tasks')