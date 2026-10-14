"""Initial schema with all tables

Revision ID: 001
Revises:
Create Date: 2025-12-01 00:00:00

"""
from alembic import op

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')

    op.create_index('idx_trips_creator', 'trips', ['creator_id'])
    op.create_index('idx_trips_status', 'trips', ['status'])
    op.create_index('idx_participants_email', 'participants', ['email'])
    op.create_index('idx_participants_trip', 'participants', ['trip_id'])
    op.create_index('idx_activities_title', 'activities', ['title'], postgresql_using='gin', postgresql_ops={'title': 'gin_trgm_ops'})
    op.create_index('idx_expenses_date', 'expenses', ['date'])
    op.create_index('idx_polls_active', 'polls', ['is_active'])

    op.execute('''
        CREATE INDEX idx_activities_embedding ON activities
        USING hnsw (embedding vector_cosine_ops)
    ''')

    op.execute('''
        CREATE INDEX idx_recommendations_embedding ON recommendations
        USING hnsw (embedding vector_cosine_ops)
    ''')

def downgrade() -> None:
    op.drop_index('idx_recommendations_embedding', 'recommendations')
    op.drop_index('idx_activities_embedding', 'activities')
    op.drop_index('idx_polls_active', 'polls')
    op.drop_index('idx_expenses_date', 'expenses')
    op.drop_index('idx_activities_title', 'activities')
    op.drop_index('idx_participants_trip', 'participants')
    op.drop_index('idx_participants_email', 'participants')
    op.drop_index('idx_trips_status', 'trips')
    op.drop_index('idx_trips_creator', 'trips')
