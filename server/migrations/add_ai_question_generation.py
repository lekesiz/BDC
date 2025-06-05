"""Add AI Question Generation models

This migration creates all the necessary tables for the AI-powered question generation system.

Revision ID: ai_question_generation_001
Revises: latest
Create Date: 2024-01-01 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'ai_question_generation_001'
down_revision = 'latest'  # Replace with actual latest revision
branch_labels = None
depends_on = None


def upgrade():
    """Create AI Question Generation tables."""
    
    # Create content_types table
    op.create_table('content_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('supported_formats', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Create source_content table
    op.create_table('source_content',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('creator_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('content_type_id', sa.Integer(), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=True),
        sa.Column('url', sa.String(length=1000), nullable=True),
        sa.Column('text_content', sa.Text(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('processing_status', sa.String(length=20), nullable=True),
        sa.Column('processing_error', sa.Text(), nullable=True),
        sa.Column('extracted_text', sa.Text(), nullable=True),
        sa.Column('keywords', sa.JSON(), nullable=True),
        sa.Column('topics', sa.JSON(), nullable=True),
        sa.Column('difficulty_level', sa.Float(), nullable=True),
        sa.Column('readability_score', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['content_type_id'], ['content_types.id'], ),
        sa.ForeignKeyConstraint(['creator_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create question_types table
    op.create_table('question_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('display_name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('generation_prompt_template', sa.Text(), nullable=True),
        sa.Column('validation_rules', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Create blooms_taxonomy table
    op.create_table('blooms_taxonomy',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('level', sa.String(length=20), nullable=False),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('keywords', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('level')
    )
    
    # Create learning_objectives table
    op.create_table('learning_objectives',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('creator_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('blooms_level_id', sa.Integer(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['blooms_level_id'], ['blooms_taxonomy.id'], ),
        sa.ForeignKeyConstraint(['creator_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create question_generation_requests table
    op.create_table('question_generation_requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('request_id', sa.String(length=36), nullable=True),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('creator_id', sa.Integer(), nullable=False),
        sa.Column('source_content_id', sa.Integer(), nullable=False),
        sa.Column('question_count', sa.Integer(), nullable=True),
        sa.Column('question_types', sa.JSON(), nullable=True),
        sa.Column('difficulty_range', sa.JSON(), nullable=True),
        sa.Column('blooms_levels', sa.JSON(), nullable=True),
        sa.Column('learning_objectives', sa.JSON(), nullable=True),
        sa.Column('language', sa.String(length=10), nullable=True),
        sa.Column('topic_focus', sa.JSON(), nullable=True),
        sa.Column('avoid_topics', sa.JSON(), nullable=True),
        sa.Column('custom_instructions', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('progress', sa.Float(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('ai_model', sa.String(length=50), nullable=True),
        sa.Column('model_parameters', sa.JSON(), nullable=True),
        sa.Column('total_tokens_used', sa.Integer(), nullable=True),
        sa.Column('cost_estimate', sa.Float(), nullable=True),
        sa.Column('questions_generated', sa.Integer(), nullable=True),
        sa.Column('questions_approved', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['creator_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['source_content_id'], ['source_content.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('request_id')
    )
    
    # Create generated_questions table
    op.create_table('generated_questions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('generation_request_id', sa.Integer(), nullable=False),
        sa.Column('question_type_id', sa.Integer(), nullable=False),
        sa.Column('question_text', sa.Text(), nullable=False),
        sa.Column('question_options', sa.JSON(), nullable=True),
        sa.Column('correct_answer', sa.JSON(), nullable=True),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.Column('difficulty_level', sa.Float(), nullable=False),
        sa.Column('blooms_level_id', sa.Integer(), nullable=True),
        sa.Column('learning_objective_id', sa.Integer(), nullable=True),
        sa.Column('keywords', sa.JSON(), nullable=True),
        sa.Column('topics', sa.JSON(), nullable=True),
        sa.Column('quality_score', sa.Float(), nullable=True),
        sa.Column('clarity_score', sa.Float(), nullable=True),
        sa.Column('relevance_score', sa.Float(), nullable=True),
        sa.Column('uniqueness_score', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('reviewed_by', sa.Integer(), nullable=True),
        sa.Column('review_notes', sa.Text(), nullable=True),
        sa.Column('review_date', sa.DateTime(), nullable=True),
        sa.Column('times_used', sa.Integer(), nullable=True),
        sa.Column('performance_data', sa.JSON(), nullable=True),
        sa.Column('generation_prompt', sa.Text(), nullable=True),
        sa.Column('ai_confidence', sa.Float(), nullable=True),
        sa.Column('tokens_used', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['blooms_level_id'], ['blooms_taxonomy.id'], ),
        sa.ForeignKeyConstraint(['generation_request_id'], ['question_generation_requests.id'], ),
        sa.ForeignKeyConstraint(['learning_objective_id'], ['learning_objectives.id'], ),
        sa.ForeignKeyConstraint(['question_type_id'], ['question_types.id'], ),
        sa.ForeignKeyConstraint(['reviewed_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create question_duplicates table
    op.create_table('question_duplicates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('question1_id', sa.Integer(), nullable=False),
        sa.Column('question2_id', sa.Integer(), nullable=False),
        sa.Column('similarity_score', sa.Float(), nullable=False),
        sa.Column('similarity_type', sa.String(length=20), nullable=False),
        sa.Column('detection_method', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('reviewed_by', sa.Integer(), nullable=True),
        sa.Column('resolution_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['question1_id'], ['generated_questions.id'], ),
        sa.ForeignKeyConstraint(['question2_id'], ['generated_questions.id'], ),
        sa.ForeignKeyConstraint(['reviewed_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('question1_id', 'question2_id', name='unique_question_pair')
    )
    
    # Create question_banks table
    op.create_table('question_banks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('creator_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('auto_add_criteria', sa.JSON(), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('total_questions', sa.Integer(), nullable=True),
        sa.Column('approved_questions', sa.Integer(), nullable=True),
        sa.Column('avg_difficulty', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['creator_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create question_bank_questions table
    op.create_table('question_bank_questions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('question_bank_id', sa.Integer(), nullable=False),
        sa.Column('generated_question_id', sa.Integer(), nullable=False),
        sa.Column('added_by', sa.Integer(), nullable=False),
        sa.Column('order', sa.Integer(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['added_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['generated_question_id'], ['generated_questions.id'], ),
        sa.ForeignKeyConstraint(['question_bank_id'], ['question_banks.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('question_bank_id', 'generated_question_id', name='unique_bank_question')
    )
    
    # Create generation_analytics table
    op.create_table('generation_analytics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('requests_created', sa.Integer(), nullable=True),
        sa.Column('requests_completed', sa.Integer(), nullable=True),
        sa.Column('requests_failed', sa.Integer(), nullable=True),
        sa.Column('questions_generated', sa.Integer(), nullable=True),
        sa.Column('questions_approved', sa.Integer(), nullable=True),
        sa.Column('questions_rejected', sa.Integer(), nullable=True),
        sa.Column('avg_quality_score', sa.Float(), nullable=True),
        sa.Column('avg_ai_confidence', sa.Float(), nullable=True),
        sa.Column('duplicate_rate', sa.Float(), nullable=True),
        sa.Column('avg_generation_time', sa.Float(), nullable=True),
        sa.Column('total_tokens_used', sa.Integer(), nullable=True),
        sa.Column('total_cost', sa.Float(), nullable=True),
        sa.Column('questions_used_in_tests', sa.Integer(), nullable=True),
        sa.Column('avg_question_performance', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'date', name='unique_tenant_date')
    )
    
    # Create indexes for performance
    op.create_index('idx_generated_questions_status', 'generated_questions', ['status'])
    op.create_index('idx_generated_questions_difficulty', 'generated_questions', ['difficulty_level'])
    op.create_index('idx_generated_questions_quality', 'generated_questions', ['quality_score'])
    op.create_index('idx_generated_questions_request', 'generated_questions', ['generation_request_id'])
    op.create_index('idx_question_duplicates_similarity', 'question_duplicates', ['similarity_score'])
    op.create_index('idx_question_duplicates_status', 'question_duplicates', ['status'])
    op.create_index('idx_question_bank_questions_order', 'question_bank_questions', ['order'])
    op.create_index('idx_generation_analytics_date', 'generation_analytics', ['date'])


def downgrade():
    """Drop AI Question Generation tables."""
    
    # Drop indexes
    op.drop_index('idx_generation_analytics_date', table_name='generation_analytics')
    op.drop_index('idx_question_bank_questions_order', table_name='question_bank_questions')
    op.drop_index('idx_question_duplicates_status', table_name='question_duplicates')
    op.drop_index('idx_question_duplicates_similarity', table_name='question_duplicates')
    op.drop_index('idx_generated_questions_request', table_name='generated_questions')
    op.drop_index('idx_generated_questions_quality', table_name='generated_questions')
    op.drop_index('idx_generated_questions_difficulty', table_name='generated_questions')
    op.drop_index('idx_generated_questions_status', table_name='generated_questions')
    
    # Drop tables in reverse order (respecting foreign key constraints)
    op.drop_table('generation_analytics')
    op.drop_table('question_bank_questions')
    op.drop_table('question_banks')
    op.drop_table('question_duplicates')
    op.drop_table('generated_questions')
    op.drop_table('question_generation_requests')
    op.drop_table('learning_objectives')
    op.drop_table('blooms_taxonomy')
    op.drop_table('question_types')
    op.drop_table('source_content')
    op.drop_table('content_types')