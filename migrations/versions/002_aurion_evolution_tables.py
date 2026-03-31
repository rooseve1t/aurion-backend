"""Aurion Evolution: trusted_devices, feed_cards, evolution_proposals + users extensions

Revision ID: 002
Revises: 001
Create Date: 2026-03-30 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- Расширение таблицы users ---
    op.add_column('users', sa.Column(
        'telegram_id', sa.String(20), nullable=True, unique=True
    ))
    op.add_column('users', sa.Column(
        'webauthn_credentials', sa.JSON(), nullable=True, server_default='[]'
    ))
    op.create_index('ix_users_telegram_id', 'users', ['telegram_id'], unique=True)

    # --- Таблица trusted_devices ---
    op.create_table(
        'trusted_devices',
        sa.Column('id', sa.CHAR(36), primary_key=True),
        sa.Column('user_id', sa.CHAR(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('device_fingerprint', sa.String(255), nullable=False),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('added_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('last_seen_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('revoked', sa.Boolean(), nullable=False, server_default='false'),
    )
    op.create_index('ix_trusted_devices_user_id', 'trusted_devices', ['user_id'])
    op.create_unique_constraint(
        'uq_trusted_devices_user_fingerprint',
        'trusted_devices',
        ['user_id', 'device_fingerprint']
    )

    # --- Таблица feed_cards ---
    op.create_table(
        'feed_cards',
        sa.Column('id', sa.CHAR(36), primary_key=True),
        sa.Column('user_id', sa.CHAR(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('type', sa.String(20), nullable=False),
        sa.Column('domain', sa.String(20), nullable=False),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('priority', sa.String(10), nullable=False, server_default='low'),
        sa.Column('requires_confirmation', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('confirmed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('dismissed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_feed_cards_user_id', 'feed_cards', ['user_id'])
    op.create_index('ix_feed_cards_user_created', 'feed_cards', ['user_id', 'created_at'])

    # --- Таблица evolution_proposals ---
    op.create_table(
        'evolution_proposals',
        sa.Column('id', sa.CHAR(36), primary_key=True),
        sa.Column('user_id', sa.CHAR(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('diff', sa.Text(), nullable=False),
        sa.Column('affected_files', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('test_command', sa.String(500), nullable=False, server_default='pytest'),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('commit_hash', sa.String(40), nullable=True),
        sa.Column('error_log', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_evolution_proposals_user_id', 'evolution_proposals', ['user_id'])


def downgrade() -> None:
    op.drop_table('evolution_proposals')
    op.drop_table('feed_cards')
    op.drop_table('trusted_devices')
    op.drop_index('ix_users_telegram_id', table_name='users')
    op.drop_column('users', 'webauthn_credentials')
    op.drop_column('users', 'telegram_id')
