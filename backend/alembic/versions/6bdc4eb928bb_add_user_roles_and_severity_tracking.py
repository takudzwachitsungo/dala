"""add_user_roles_and_severity_tracking

Revision ID: 6bdc4eb928bb
Revises: b680ccca5cc1
Create Date: 2025-12-22 08:48:10.402221

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6bdc4eb928bb'
down_revision: Union[str, None] = 'b680ccca5cc1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add role and peer supporter fields to users table
    op.add_column('users', sa.Column('role', sa.String(20), nullable=False, server_default='user'))
    op.add_column('users', sa.Column('is_moderator', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('is_peer_supporter', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('moderation_notes', sa.Text(), nullable=True))
    
    # Add risk tracking fields to users
    op.add_column('users', sa.Column('risk_level', sa.String(20), nullable=False, server_default='low'))
    op.add_column('users', sa.Column('last_risk_assessment', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('escalation_status', sa.String(20), nullable=True))
    
    # Add severity tracking to posts (flag_reason already exists from Phase 2)
    op.add_column('posts', sa.Column('flag_severity', sa.String(20), nullable=True))
    op.add_column('posts', sa.Column('reviewed_by_id', sa.UUID(), nullable=True))
    op.add_column('posts', sa.Column('reviewed_at', sa.DateTime(), nullable=True))
    
    # Add risk tracking to messages
    op.add_column('messages', sa.Column('risk_score', sa.Float(), nullable=True))
    op.add_column('messages', sa.Column('risk_indicators', sa.JSON(), nullable=True))
    op.add_column('messages', sa.Column('requires_escalation', sa.Boolean(), nullable=False, server_default='false'))


def downgrade() -> None:
    # Remove columns from messages
    op.drop_column('messages', 'requires_escalation')
    op.drop_column('messages', 'risk_indicators')
    op.drop_column('messages', 'risk_score')
    
    # Remove columns from posts
    op.drop_column('posts', 'reviewed_at')
    op.drop_column('posts', 'reviewed_by_id')
    op.drop_column('posts', 'flag_severity')
    
    # Remove risk tracking from users
    op.drop_column('users', 'escalation_status')
    op.drop_column('users', 'last_risk_assessment')
    op.drop_column('users', 'risk_level')
    
    # Remove role fields from users
    op.drop_column('users', 'moderation_notes')
    op.drop_column('users', 'is_peer_supporter')
    op.drop_column('users', 'is_moderator')
    op.drop_column('users', 'role')
