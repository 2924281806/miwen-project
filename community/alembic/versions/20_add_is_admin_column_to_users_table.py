"""add is_admin column to users table

Revision ID: d49ad90b02c4
Revises: 0019_hot_topics_image
Create Date: 2026-11-13 11:08:02.904310

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'd49ad90b02c4'
down_revision: Union[str, None] = '0019_hot_topics_image'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    添加 is_admin 列到 users 表
    """
    op.add_column('users', sa.Column('is_admin', mysql.TINYINT(), server_default=sa.text('0'), nullable=False, comment='是否管理员：0否，1是'))
    op.alter_column('users', 'is_admin',
               existing_type=mysql.TINYINT(),
               server_default=sa.text('0'),
               existing_comment='是否管理员：0否，1是',
               existing_nullable=False)
    op.create_index('ix_users_is_admin', 'users', ['is_admin'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """
    删除 is_admin 列从 users 表
    """
    op.drop_column('users', 'is_admin')
   