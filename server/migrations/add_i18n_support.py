"""Add internationalization support tables and extend user preferences.

This migration creates the comprehensive internationalization infrastructure
including languages, multilingual content, translation memory, and user preferences.
"""

from alembic import op
import sqlalchemy as sa
from datetime import datetime


def upgrade():
    """Add internationalization support."""
    
    # Create languages table
    op.create_table(
        'languages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=10), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('native_name', sa.String(length=100), nullable=False),
        sa.Column('direction', sa.String(length=3), nullable=True, default='ltr'),
        sa.Column('region', sa.String(length=10), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('is_default', sa.Boolean(), nullable=True, default=False),
        sa.Column('flag_icon', sa.String(length=255), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=True, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    
    # Create multilingual_content table
    op.create_table(
        'multilingual_content',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('entity_id', sa.String(length=255), nullable=False),
        sa.Column('field_name', sa.String(length=100), nullable=False),
        sa.Column('language_code', sa.String(length=10), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('content_type', sa.String(length=20), nullable=True, default='text'),
        sa.Column('is_original', sa.Boolean(), nullable=True, default=False),
        sa.Column('translation_status', sa.String(length=20), nullable=True, default='draft'),
        sa.Column('translation_method', sa.String(length=20), nullable=True),
        sa.Column('quality_score', sa.Float(), nullable=True),
        sa.Column('version', sa.Integer(), nullable=True, default=1),
        sa.Column('is_current', sa.Boolean(), nullable=True, default=True),
        sa.Column('parent_version_id', sa.Integer(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.Column('translated_by', sa.Integer(), nullable=True),
        sa.Column('reviewed_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.Column('translated_at', sa.DateTime(), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(), nullable=True),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['translated_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['reviewed_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['parent_version_id'], ['multilingual_content.id'], )
    )
    
    # Create indexes for multilingual_content
    op.create_index(
        'idx_entity_field_lang', 
        'multilingual_content', 
        ['entity_type', 'entity_id', 'field_name', 'language_code']
    )
    op.create_index(
        'idx_entity_current', 
        'multilingual_content', 
        ['entity_type', 'entity_id', 'is_current']
    )
    op.create_index(
        'idx_translation_status', 
        'multilingual_content', 
        ['translation_status']
    )
    
    # Create content_translations table (from content_translation_service)
    op.create_table(
        'content_translations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('content_id', sa.String(length=255), nullable=False),
        sa.Column('content_type', sa.String(length=50), nullable=False),
        sa.Column('field_name', sa.String(length=100), nullable=False),
        sa.Column('source_language', sa.String(length=10), nullable=False),
        sa.Column('target_language', sa.String(length=10), nullable=False),
        sa.Column('source_content', sa.Text(), nullable=False),
        sa.Column('translated_content', sa.Text(), nullable=False),
        sa.Column('translation_method', sa.String(length=20), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('quality_score', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True, default='pending'),
        sa.Column('is_approved', sa.Boolean(), nullable=True, default=False),
        sa.Column('needs_review', sa.Boolean(), nullable=True, default=True),
        sa.Column('translator_id', sa.Integer(), nullable=True),
        sa.Column('reviewer_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.Column('translated_at', sa.DateTime(), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(), nullable=True),
        sa.Column('metadata', sa.Text(), nullable=True),
        sa.Column('version', sa.Integer(), nullable=True, default=1),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['translator_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['reviewer_id'], ['users.id'], )
    )
    
    # Create index for content_translations
    op.create_index('idx_content_translations', 'content_translations', ['content_id'])
    
    # Create translation_memory table
    op.create_table(
        'translation_memory',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('source_text_hash', sa.String(length=64), nullable=False),
        sa.Column('source_language', sa.String(length=10), nullable=False),
        sa.Column('target_language', sa.String(length=10), nullable=False),
        sa.Column('source_text', sa.Text(), nullable=False),
        sa.Column('target_text', sa.Text(), nullable=False),
        sa.Column('domain', sa.String(length=100), nullable=True),
        sa.Column('context', sa.String(length=255), nullable=True),
        sa.Column('quality_score', sa.Float(), nullable=True, default=1.0),
        sa.Column('usage_count', sa.Integer(), nullable=True, default=0),
        sa.Column('last_used', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], )
    )
    
    # Create index for translation_memory
    op.create_index('idx_source_text_hash', 'translation_memory', ['source_text_hash'])
    
    # Create translation_projects table
    op.create_table(
        'translation_projects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('source_language', sa.String(length=10), nullable=False),
        sa.Column('target_languages', sa.Text(), nullable=False),
        sa.Column('entity_types', sa.Text(), nullable=True),
        sa.Column('entity_ids', sa.Text(), nullable=True),
        sa.Column('field_names', sa.Text(), nullable=True),
        sa.Column('require_review', sa.Boolean(), nullable=True, default=True),
        sa.Column('auto_approve_ai', sa.Boolean(), nullable=True, default=False),
        sa.Column('quality_threshold', sa.Float(), nullable=True, default=0.8),
        sa.Column('status', sa.String(length=20), nullable=True, default='draft'),
        sa.Column('total_items', sa.Integer(), nullable=True, default=0),
        sa.Column('completed_items', sa.Integer(), nullable=True, default=0),
        sa.Column('progress_percentage', sa.Float(), nullable=True, default=0.0),
        sa.Column('start_date', sa.DateTime(), nullable=True),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('completed_date', sa.DateTime(), nullable=True),
        sa.Column('project_manager_id', sa.Integer(), nullable=True),
        sa.Column('assigned_translators', sa.Text(), nullable=True),
        sa.Column('assigned_reviewers', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['project_manager_id'], ['users.id'], )
    )
    
    # Create translation_workflows table
    op.create_table(
        'translation_workflows',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('content_id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=True),
        sa.Column('current_state', sa.String(length=30), nullable=True, default='pending_translation'),
        sa.Column('previous_state', sa.String(length=30), nullable=True),
        sa.Column('assigned_translator', sa.Integer(), nullable=True),
        sa.Column('assigned_reviewer', sa.Integer(), nullable=True),
        sa.Column('translation_deadline', sa.DateTime(), nullable=True),
        sa.Column('review_deadline', sa.DateTime(), nullable=True),
        sa.Column('translation_started_at', sa.DateTime(), nullable=True),
        sa.Column('translation_completed_at', sa.DateTime(), nullable=True),
        sa.Column('review_started_at', sa.DateTime(), nullable=True),
        sa.Column('review_completed_at', sa.DateTime(), nullable=True),
        sa.Column('translation_quality', sa.Float(), nullable=True),
        sa.Column('review_quality', sa.Float(), nullable=True),
        sa.Column('translator_notes', sa.Text(), nullable=True),
        sa.Column('reviewer_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['content_id'], ['multilingual_content.id'], ),
        sa.ForeignKeyConstraint(['project_id'], ['translation_projects.id'], ),
        sa.ForeignKeyConstraint(['assigned_translator'], ['users.id'], ),
        sa.ForeignKeyConstraint(['assigned_reviewer'], ['users.id'], )
    )
    
    # Create user_language_preferences table
    op.create_table(
        'user_language_preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('primary_language', sa.String(length=10), nullable=False, default='en'),
        sa.Column('secondary_languages', sa.Text(), nullable=True),
        sa.Column('enable_auto_detection', sa.Boolean(), nullable=True, default=True),
        sa.Column('detect_from_browser', sa.Boolean(), nullable=True, default=True),
        sa.Column('detect_from_content', sa.Boolean(), nullable=True, default=False),
        sa.Column('detect_from_location', sa.Boolean(), nullable=True, default=False),
        sa.Column('fallback_language', sa.String(length=10), nullable=True, default='en'),
        sa.Column('show_original_content', sa.Boolean(), nullable=True, default=False),
        sa.Column('auto_translate_content', sa.Boolean(), nullable=True, default=True),
        sa.Column('translation_specialties', sa.Text(), nullable=True),
        sa.Column('available_for_translation', sa.Boolean(), nullable=True, default=False),
        sa.Column('translation_language_pairs', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.UniqueConstraint('user_id')
    )
    
    # Insert default languages
    languages_data = [
        ('en', 'English', 'English', 'ltr', 'en-US', True, True, '🇺🇸', 0),
        ('tr', 'Turkish', 'Türkçe', 'ltr', 'tr-TR', True, False, '🇹🇷', 1),
        ('ar', 'Arabic', 'العربية', 'rtl', 'ar-SA', True, False, '🇸🇦', 2),
        ('es', 'Spanish', 'Español', 'ltr', 'es-ES', True, False, '🇪🇸', 3),
        ('fr', 'French', 'Français', 'ltr', 'fr-FR', True, False, '🇫🇷', 4),
        ('de', 'German', 'Deutsch', 'ltr', 'de-DE', True, False, '🇩🇪', 5),
        ('ru', 'Russian', 'Русский', 'ltr', 'ru-RU', True, False, '🇷🇺', 6)
    ]
    
    languages_table = sa.table(
        'languages',
        sa.column('code', sa.String),
        sa.column('name', sa.String),
        sa.column('native_name', sa.String),
        sa.column('direction', sa.String),
        sa.column('region', sa.String),
        sa.column('is_active', sa.Boolean),
        sa.column('is_default', sa.Boolean),
        sa.column('flag_icon', sa.String),
        sa.column('sort_order', sa.Integer),
        sa.column('created_at', sa.DateTime),
        sa.column('updated_at', sa.DateTime)
    )
    
    for lang_data in languages_data:
        op.bulk_insert(languages_table, [{
            'code': lang_data[0],
            'name': lang_data[1],
            'native_name': lang_data[2],
            'direction': lang_data[3],
            'region': lang_data[4],
            'is_active': lang_data[5],
            'is_default': lang_data[6],
            'flag_icon': lang_data[7],
            'sort_order': lang_data[8],
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }])


def downgrade():
    """Remove internationalization support."""
    
    # Drop tables in reverse order of creation
    op.drop_table('user_language_preferences')
    op.drop_table('translation_workflows')
    op.drop_table('translation_projects')
    op.drop_table('translation_memory')
    op.drop_table('content_translations')
    op.drop_table('multilingual_content')
    op.drop_table('languages')
    
    # Drop indexes
    op.drop_index('idx_content_translations')
    op.drop_index('idx_source_text_hash')
    op.drop_index('idx_translation_status')
    op.drop_index('idx_entity_current')
    op.drop_index('idx_entity_field_lang')