"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-03-21 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Создание расширения pgvector
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    
    # Таблица пользователей
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('username', sa.String(length=64), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('two_factor_enabled', sa.Boolean(), nullable=False),
        sa.Column('two_factor_secret', sa.String(length=32), nullable=True),
        sa.Column('backup_codes', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_verified', sa.Boolean(), nullable=False),
        sa.Column('display_name', sa.String(length=100), nullable=True),
        sa.Column('avatar_url', sa.String(length=500), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('preferences', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('notifications_enabled', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    
    # Таблица воспоминаний
    op.create_table(
        'memory_entries',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('content_type', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=True),
        sa.Column('embedding', postgresql.ARRAY(postgresql.FLOAT()), nullable=True),
        sa.Column('tags', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('categories', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('importance', sa.Integer(), nullable=False),
        sa.Column('priority', sa.String(length=20), nullable=False),
        sa.Column('sentiment', sa.String(length=20), nullable=True),
        sa.Column('emotion', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('context', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('source', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('access_count', sa.Integer(), nullable=False),
        sa.Column('last_accessed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_memory_entries_user_id'), 'memory_entries', ['user_id'], unique=False)
    op.create_index(op.f('ix_memory_entries_created_at'), 'memory_entries', ['created_at'], unique=False)
    
    # Таблица устройств умного дома
    op.create_table(
        'devices',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('device_type', sa.String(length=50), nullable=False),
        sa.Column('manufacturer', sa.String(length=100), nullable=True),
        sa.Column('model', sa.String(length=100), nullable=True),
        sa.Column('room', sa.String(length=100), nullable=True),
        sa.Column('location', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('protocol', sa.String(length=20), nullable=False),
        sa.Column('address', sa.String(length=200), nullable=True),
        sa.Column('topic', sa.String(length=200), nullable=True),
        sa.Column('status_topic', sa.String(length=200), nullable=True),
        sa.Column('state', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('capabilities', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('settings', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_online', sa.Boolean(), nullable=False),
        sa.Column('is_enabled', sa.Boolean(), nullable=False),
        sa.Column('battery_level', sa.Integer(), nullable=True),
        sa.Column('power_consumption', sa.Integer(), nullable=True),
        sa.Column('energy_usage', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_secure', sa.Boolean(), nullable=False),
        sa.Column('encryption_enabled', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_seen_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_command_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_devices_user_id'), 'devices', ['user_id'], unique=False)
    
    # Таблица логов команд устройств
    op.create_table(
        'device_command_log',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('device_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('command', sa.String(length=100), nullable=False),
        sa.Column('parameters', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=False),
        sa.Column('response', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('execution_time_ms', sa.Integer(), nullable=True),
        sa.Column('source', sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(['device_id'], ['devices.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_device_command_log_device_id'), 'device_command_log', ['device_id'], unique=False)
    op.create_index(op.f('ix_device_command_log_user_id'), 'device_command_log', ['user_id'], unique=False)
    op.create_index(op.f('ix_device_command_log_created_at'), 'device_command_log', ['created_at'], unique=False)
    
    # Таблица агентов
    op.create_table(
        'agents',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('agent_type', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('config', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('capabilities', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('model', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_enabled', sa.Boolean(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('tasks_completed', sa.Integer(), nullable=False),
        sa.Column('success_rate', sa.Float(), nullable=False),
        sa.Column('avg_response_time_ms', sa.Integer(), nullable=True),
        sa.Column('priority', sa.Integer(), nullable=False),
        sa.Column('max_concurrent_tasks', sa.Integer(), nullable=False),
        sa.Column('timeout_seconds', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_task_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agents_user_id'), 'agents', ['user_id'], unique=False)
    
    # Таблица задач агентов
    op.create_table(
        'agent_tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('agent_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('task_type', sa.String(length=50), nullable=False),
        sa.Column('input_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('output_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('progress', sa.Integer(), nullable=False),
        sa.Column('result', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('parent_task_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('swarm_task_id', sa.String(length=100), nullable=True),
        sa.Column('priority', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('execution_time_ms', sa.Integer(), nullable=True),
        sa.Column('timeout_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tokens_used', sa.Integer(), nullable=True),
        sa.Column('cost_estimate', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['parent_task_id'], ['agent_tasks.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agent_tasks_agent_id'), 'agent_tasks', ['agent_id'], unique=False)
    op.create_index(op.f('ix_agent_tasks_user_id'), 'agent_tasks', ['user_id'], unique=False)
    op.create_index(op.f('ix_agent_tasks_created_at'), 'agent_tasks', ['created_at'], unique=False)
    
    # Таблица логов агентов
    op.create_table(
        'agent_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('agent_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('level', sa.String(length=10), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('details', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('event_type', sa.String(length=50), nullable=True),
        sa.Column('context', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ),
        sa.ForeignKeyConstraint(['task_id'], ['agent_tasks.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agent_logs_agent_id'), 'agent_logs', ['agent_id'], unique=False)
    op.create_index(op.f('ix_agent_logs_created_at'), 'agent_logs', ['created_at'], unique=False)
    
    # Таблица банковских подключений
    op.create_table(
        'bank_connections',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('bank_code', sa.String(length=20), nullable=False),
        sa.Column('bank_name', sa.String(length=100), nullable=False),
        sa.Column('client_id', sa.String(length=100), nullable=True),
        sa.Column('client_secret', sa.Text(), nullable=True),
        sa.Column('access_token', sa.Text(), nullable=True),
        sa.Column('refresh_token', sa.Text(), nullable=True),
        sa.Column('token_expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_connected', sa.Boolean(), nullable=False),
        sa.Column('last_sync_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('sync_enabled', sa.Boolean(), nullable=False),
        sa.Column('sync_frequency', sa.Integer(), nullable=False),
        sa.Column('accounts_limit', sa.Integer(), nullable=True),
        sa.Column('webhook_secret', sa.String(length=100), nullable=True),
        sa.Column('encryption_key_id', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bank_connections_user_id'), 'bank_connections', ['user_id'], unique=False)
    
    # Таблица банковских счетов
    op.create_table(
        'bank_accounts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('bank_connection_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('external_id', sa.String(length=100), nullable=False),
        sa.Column('account_number', sa.String(length=50), nullable=True),
        sa.Column('account_name', sa.String(length=200), nullable=False),
        sa.Column('account_type', sa.String(length=50), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('balance', sa.Float(), nullable=False),
        sa.Column('available_balance', sa.Float(), nullable=True),
        sa.Column('credit_limit', sa.Float(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_archived', sa.Boolean(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('bank_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_sync_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['bank_connection_id'], ['bank_connections.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bank_accounts_bank_connection_id'), 'bank_accounts', ['bank_connection_id'], unique=False)
    op.create_index(op.f('ix_bank_accounts_user_id'), 'bank_accounts', ['user_id'], unique=False)
    
    # Таблица транзакций
    op.create_table(
        'transactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('account_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('external_id', sa.String(length=100), nullable=True),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('merchant_name', sa.String(length=200), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('mcc_code', sa.Integer(), nullable=True),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('balance_after', sa.Float(), nullable=True),
        sa.Column('transaction_type', sa.String(length=20), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('transaction_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('posted_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('location', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('bank_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('tags', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_recurring', sa.Boolean(), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('ai_category', sa.String(length=100), nullable=True),
        sa.Column('sentiment', sa.String(length=20), nullable=True),
        sa.ForeignKeyConstraint(['account_id'], ['bank_accounts.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_transactions_account_id'), 'transactions', ['account_id'], unique=False)
    op.create_index(op.f('ix_transactions_user_id'), 'transactions', ['user_id'], unique=False)
    op.create_index(op.f('ix_transactions_transaction_date'), 'transactions', ['transaction_date'], unique=False)
    
    # Таблица тарифов
    op.create_table(
        'tariffs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('display_name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('billing_interval', sa.String(length=20), nullable=False),
        sa.Column('trial_days', sa.Integer(), nullable=False),
        sa.Column('features', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('limits', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_public', sa.Boolean(), nullable=False),
        sa.Column('sort_order', sa.Integer(), nullable=False),
        sa.Column('badge', sa.String(length=50), nullable=True),
        sa.Column('color', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_tariffs_name'), 'tariffs', ['name'], unique=True)
    
    # Таблица подписок
    op.create_table(
        'subscriptions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tariff_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('current_period_start', sa.DateTime(timezone=True), nullable=False),
        sa.Column('current_period_end', sa.DateTime(timezone=True), nullable=False),
        sa.Column('trial_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('auto_renew', sa.Boolean(), nullable=False),
        sa.Column('next_billing_amount', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['tariff_id'], ['tariffs.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_subscriptions_user_id'), 'subscriptions', ['user_id'], unique=False)
    op.create_index(op.f('ix_subscriptions_tariff_id'), 'subscriptions', ['tariff_id'], unique=False)
    
    # Таблица платежей
    op.create_table(
        'payments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('subscription_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('provider', sa.String(length=20), nullable=False),
        sa.Column('external_id', sa.String(length=100), nullable=True),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('paid', sa.Boolean(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('payment_method', sa.String(length=50), nullable=True),
        sa.Column('payment_method_details', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('paid_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('refunded_amount', sa.Float(), nullable=False),
        sa.Column('refunds', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('fee', sa.Float(), nullable=True),
        sa.Column('net_amount', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['subscription_id'], ['subscriptions.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_payments_user_id'), 'payments', ['user_id'], unique=False)
    op.create_index(op.f('ix_payments_subscription_id'), 'payments', ['subscription_id'], unique=False)
    
    # Таблица квантовых задач
    op.create_table(
        'quantum_jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('job_type', sa.String(length=50), nullable=False),
        sa.Column('algorithm', sa.String(length=100), nullable=True),
        sa.Column('input_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('parameters', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('problem_size', sa.Integer(), nullable=True),
        sa.Column('backend', sa.String(length=100), nullable=False),
        sa.Column('backend_config', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('shots', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('progress', sa.Integer(), nullable=False),
        sa.Column('result', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('solution', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('objective_value', sa.Float(), nullable=True),
        sa.Column('execution_time_ms', sa.Integer(), nullable=True),
        sa.Column('quantum_volume', sa.Integer(), nullable=True),
        sa.Column('fidelity', sa.Float(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('error_rate', sa.Float(), nullable=True),
        sa.Column('priority', sa.Integer(), nullable=False),
        sa.Column('queue_position', sa.Integer(), nullable=True),
        sa.Column('estimated_completion', sa.DateTime(timezone=True), nullable=True),
        sa.Column('credits_used', sa.Integer(), nullable=True),
        sa.Column('cost_estimate', sa.Float(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('error_code', sa.String(length=50), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('timeout_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cache_key', sa.String(length=100), nullable=True),
        sa.Column('cached_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('tags', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_quantum_jobs_user_id'), 'quantum_jobs', ['user_id'], unique=False)
    op.create_index(op.f('ix_quantum_jobs_created_at'), 'quantum_jobs', ['created_at'], unique=False)
    
    # Таблица OSINT логов
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('service', sa.String(length=50), nullable=False),
        sa.Column('query_type', sa.String(length=50), nullable=False),
        sa.Column('query', sa.String(length=1000), nullable=False),
        sa.Column('result_count', sa.Integer(), nullable=False),
        sa.Column('results', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('summary', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('response_time_ms', sa.Integer(), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('status_code', sa.Integer(), nullable=True),
        sa.Column('credits_used', sa.Integer(), nullable=True),
        sa.Column('cost_estimate', sa.Float(), nullable=True),
        sa.Column('rate_limit_remaining', sa.Integer(), nullable=True),
        sa.Column('source_ip', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('cache_key', sa.String(length=100), nullable=True),
        sa.Column('cached_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cache_ttl_seconds', sa.Integer(), nullable=False),
        sa.Column('risk_level', sa.String(length=20), nullable=True),
        sa.Column('categories', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_logs_user_id'), 'audit_logs', ['user_id'], unique=False)
    op.create_index(op.f('ix_audit_logs_created_at'), 'audit_logs', ['created_at'], unique=False)
    
    # Таблица экспериментов эволюции
    op.create_table(
        'evolution_experiments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('experiment_type', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('objective', sa.Text(), nullable=False),
        sa.Column('success_criteria', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('baseline_metrics', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('prompt', sa.Text(), nullable=False),
        sa.Column('generated_code', sa.Text(), nullable=True),
        sa.Column('language', sa.String(length=20), nullable=False),
        sa.Column('framework', sa.String(length=50), nullable=True),
        sa.Column('validation_status', sa.String(length=20), nullable=False),
        sa.Column('validation_errors', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('security_issues', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('test_status', sa.String(length=20), nullable=False),
        sa.Column('test_results', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('coverage_percent', sa.Float(), nullable=True),
        sa.Column('performance_metrics', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('execution_status', sa.String(length=20), nullable=False),
        sa.Column('execution_result', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('execution_time_ms', sa.Integer(), nullable=True),
        sa.Column('resource_usage', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('git_branch', sa.String(length=100), nullable=True),
        sa.Column('commit_hash', sa.String(length=40), nullable=True),
        sa.Column('diff_content', sa.Text(), nullable=True),
        sa.Column('pr_url', sa.String(length=500), nullable=True),
        sa.Column('merge_status', sa.String(length=20), nullable=True),
        sa.Column('overall_score', sa.Float(), nullable=True),
        sa.Column('innovation_score', sa.Float(), nullable=True),
        sa.Column('efficiency_score', sa.Float(), nullable=True),
        sa.Column('safety_score', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('is_successful', sa.Boolean(), nullable=True),
        sa.Column('can_deploy', sa.Boolean(), nullable=False),
        sa.Column('sandbox_id', sa.String(length=100), nullable=True),
        sa.Column('container_image', sa.String(length=200), nullable=True),
        sa.Column('timeout_seconds', sa.Integer(), nullable=False),
        sa.Column('risk_level', sa.String(length=20), nullable=False),
        sa.Column('blocked_operations', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('timeout_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('tags', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_evolution_experiments_user_id'), 'evolution_experiments', ['user_id'], unique=False)
    op.create_index(op.f('ix_evolution_experiments_created_at'), 'evolution_experiments', ['created_at'], unique=False)


def downgrade() -> None:
    # Удаление таблиц в обратном порядке
    op.drop_table('evolution_experiments')
    op.drop_table('audit_logs')
    op.drop_table('quantum_jobs')
    op.drop_table('payments')
    op.drop_table('subscriptions')
    op.drop_table('tariffs')
    op.drop_table('transactions')
    op.drop_table('bank_accounts')
    op.drop_table('bank_connections')
    op.drop_table('agent_logs')
    op.drop_table('agent_tasks')
    op.drop_table('agents')
    op.drop_table('device_command_log')
    op.drop_table('devices')
    op.drop_table('memory_entries')
    op.drop_table('users')
    
    # Удаление расширения pgvector
    op.execute("DROP EXTENSION IF EXISTS vector")
