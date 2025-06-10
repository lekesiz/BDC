_('cli_i18n_commands.message.cli_commands_for_international')
import json
import logging
import click
from flask import current_app
from flask.cli import with_appcontext
from app.extensions import db
from app.models.i18n import Language, MultilingualContent, UserLanguagePreference
from app.services.i18n.i18n_manager import I18nManager
from app.services.i18n.translation_service import TranslationService
from app.services.i18n.language_detection_service import LanguageDetectionService
from flask_babel import _, lazy_gettext as _l
logger = logging.getLogger(__name__)


@click.group()
def i18n():
    _('cli_i18n_commands.label.internationalization_managemen')
    pass


@i18n.command()
@with_appcontext
def init_languages():
    _('cli_i18n_commands.message.initialize_supported_languages')
    click.echo(_('cli_i18n_commands.message.initializing_supported_langu'))
    try:
        language_service = LanguageDetectionService()
        languages_data = [{'code': 'en', 'name': _(
            'i18n_language_detection_service.label.english_1'),
            'native_name': _(
            'i18n_language_detection_service.label.english_1'), 'direction':
            'ltr', 'region': _(
            'i18n_language_detection_service.message.en_us'), 'is_active': 
            True, 'is_default': True, 'flag_icon': '🇺🇸', 'sort_order': 0},
            {'code': 'tr', 'name': _(
            'i18n_language_detection_service.label.turkish'), 'native_name':
            _('i18n_language_detection_service.label.t_rk_e'), 'direction':
            'ltr', 'region': _(
            'i18n_language_detection_service.message.tr_tr'), 'is_active': 
            True, 'is_default': False, 'flag_icon': '🇹🇷', 'sort_order': 1},
            {'code': 'ar', 'name': _(
            'i18n_language_detection_service.label.arabic'), 'native_name':
            _('i18n_language_detection_service.message.'), 'direction':
            'rtl', 'region': _(
            'i18n_language_detection_service.message.ar_sa'), 'is_active': 
            True, 'is_default': False, 'flag_icon': '🇸🇦', 'sort_order': 2},
            {'code': 'es', 'name': _(
            'i18n_language_detection_service.label.spanish'), 'native_name':
            _('i18n_language_detection_service.label.espa_ol'), 'direction':
            'ltr', 'region': _(
            'i18n_language_detection_service.message.es_es'), 'is_active': 
            True, 'is_default': False, 'flag_icon': '🇪🇸', 'sort_order': 3},
            {'code': 'fr', 'name': _(
            'i18n_language_detection_service.label.french'), 'native_name':
            _('i18n_language_detection_service.label.fran_ais'),
            'direction': 'ltr', 'region': _(
            'i18n_language_detection_service.message.fr_fr'), 'is_active': 
            True, 'is_default': False, 'flag_icon': '🇫🇷', 'sort_order': 4},
            {'code': 'de', 'name': _(
            'i18n_language_detection_service.label.german'), 'native_name':
            _('i18n_language_detection_service.label.deutsch'), 'direction':
            'ltr', 'region': _(
            'i18n_language_detection_service.message.de_de'), 'is_active': 
            True, 'is_default': False, 'flag_icon': '🇩🇪', 'sort_order': 5},
            {'code': 'ru', 'name': _(
            'i18n_language_detection_service.label.russian'), 'native_name':
            _('i18n_language_detection_service.label.'), 'direction': 'ltr',
            'region': _('i18n_language_detection_service.message.ru_ru'),
            'is_active': True, 'is_default': False, 'flag_icon': '🇷🇺',
            'sort_order': 6}]
        created_count = 0
        updated_count = 0
        for lang_data in languages_data:
            existing = Language.query.filter_by(code=lang_data['code']).first()
            if existing:
                for key, value in lang_data.items():
                    setattr(existing, key, value)
                updated_count += 1
                click.echo(
                    f"  ✅ Updated language: {lang_data['native_name']} ({lang_data['code']})"
                    )
            else:
                language = Language(**lang_data)
                db.session.add(language)
                created_count += 1
                click.echo(
                    f"  ✨ Created language: {lang_data['native_name']} ({lang_data['code']})"
                    )
        db.session.commit()
        click.echo(f'\n🎉 Language initialization completed!')
        click.echo(f'   Created: {created_count} languages')
        click.echo(f'   Updated: {updated_count} languages')
    except Exception as e:
        logger.error(f'Error initializing languages: {e}')
        click.echo(f'❌ Error: {e}', err=True)
        db.session.rollback()


@i18n.command()
@click.option(_('cli_i18n_commands.message.language_2'), '-l', help=_(
    'cli_i18n_commands.message.language_code_to_check_e_g'))
@with_appcontext
def check_translations():
    _('cli_i18n_commands.message.check_translation_coverage_for')
    click.echo(_('cli_i18n_commands.message.checking_translation_coverag'))
    try:
        translation_service = TranslationService()
        languages = Language.query.filter_by(is_active=True).all()
        if not languages:
            click.echo(_(
                'cli_i18n_commands.message.no_languages_found_run_ini'))
            return
        reference_language = 'en'
        reference_translations = translation_service.get_translation_dict(
            reference_language)

        def count_keys(d):
            count = 0
            for value in d.values():
                if isinstance(value, dict):
                    count += count_keys(value)
                else:
                    count += 1
            return count
        total_keys = count_keys(reference_translations)
        click.echo(f'\n📊 Translation Coverage Report')
        click.echo(f'   Reference language: {reference_language}')
        click.echo(f'   Total translation keys: {total_keys}')
        click.echo('=' * 60)
        for language in languages:
            if language.code == reference_language:
                continue
            coverage = translation_service.get_translation_coverage(language
                .code, reference_language)
            missing_keys = translation_service.get_missing_translations(
                language.code, reference_language)
            status_icon = ('✅' if coverage > 0.9 else '⚠️' if coverage > 
                0.5 else '❌')
            click.echo(
                f'{status_icon} {language.native_name} ({language.code})')
            click.echo(f'   Coverage: {coverage:.1%}')
            click.echo(f'   Missing keys: {len(missing_keys)}')
            if missing_keys and len(missing_keys) <= 10:
                click.echo(f"   Sample missing: {', '.join(missing_keys[:5])}")
        click.echo('=' * 60)
    except Exception as e:
        logger.error(f'Error checking translations: {e}')
        click.echo(f'❌ Error: {e}', err=True)


@i18n.command()
@click.option(_('cli_i18n_commands.message.source'), '-s', default='en',
    help=_('cli_i18n_commands.label.source_language_code'))
@click.option(_('cli_i18n_commands.message.target'), '-t', required=True,
    help=_('cli_i18n_commands.label.target_language_code_1'))
@click.option(_('cli_i18n_commands.message.key'), '-k', help=
    'Specific translation key to update')
@click.option(_('cli_i18n_commands.message.value'), '-v', help=_(
    'cli_i18n_commands.label.translation_value'))
@with_appcontext
def update_translation():
    """Update a specific translation."""
    click.echo(f'🔄 Updating translation for {target}...')
    try:
        translation_service = TranslationService()
        if key and value:
            translation_service.update_translation(key, target, value,
                save_to_file=True)
            click.echo(f'✅ Updated translation: {key} = {value}')
        else:
            click.echo(_(
                'cli_i18n_commands.validation.both_key_and_value_are_r'))
            return
    except Exception as e:
        logger.error(f'Error updating translation: {e}')
        click.echo(f'❌ Error: {e}', err=True)


@i18n.command()
@click.option(_('cli_i18n_commands.message.language_2'), '-l', required=
    True, help=_('cli_i18n_commands.message.language_code_to_export'))
@click.option(_('cli_i18n_commands.message.output'), '-o', help=_(
    'cli_i18n_commands.label.output_file_path'))
@with_appcontext
def export_language():
    _('cli_i18n_commands.message.export_language_data_to_json_f')
    click.echo(f'📤 Exporting language data for {language}...')
    try:
        i18n_manager = I18nManager()
        export_data = i18n_manager.export_language_data(language)
        if 'error' in export_data:
            click.echo(f"❌ Error: {export_data['error']}", err=True)
            return
        if not output:
            output = (
                f"language_export_{language}_{export_data['export_timestamp'][:10]}.json"
                )
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        click.echo(f'✅ Language data exported to: {output}')
        click.echo(f"   UI translations: {export_data['total_ui_keys']} keys")
        click.echo(
            f"   Content items: {export_data['total_content_items']} items")
    except Exception as e:
        logger.error(f'Error exporting language: {e}')
        click.echo(f'❌ Error: {e}', err=True)


@i18n.command()
@click.option(_('cli_i18n_commands.message.file'), '-f', required=True,
    help=_('cli_i18n_commands.message.json_file_to_import'))
@click.option(_('cli_i18n_commands.message.language_2'), '-l', required=
    True, help=_('cli_i18n_commands.label.target_language_code_1'))
@with_appcontext
def import_language():
    """Import language data from JSON file."""
    click.echo(f'📥 Importing language data for {language}...')
    try:
        with open(file, 'r', encoding='utf-8') as f:
            import_data = json.load(f)
        translation_service = TranslationService()
        if 'ui_translations' in import_data:
            ui_translations = import_data['ui_translations']
            translation_service.bulk_update_translations({language:
                ui_translations})

            def count_keys(d):
                count = 0
                for value in d.values():
                    if isinstance(value, dict):
                        count += count_keys(value)
                    else:
                        count += 1
                return count
            imported_keys = count_keys(ui_translations)
            click.echo(f'✅ Imported {imported_keys} UI translation keys')
        click.echo(f'🎉 Language import completed for {language}')
    except FileNotFoundError:
        click.echo(f'❌ File not found: {file}', err=True)
    except json.JSONDecodeError:
        click.echo(f'❌ Invalid JSON file: {file}', err=True)
    except Exception as e:
        logger.error(f'Error importing language: {e}')
        click.echo(f'❌ Error: {e}', err=True)


@i18n.command()
@with_appcontext
def analytics():
    _('cli_i18n_commands.message.show_i18n_analytics_and_statis')
    click.echo(_('cli_i18n_commands.message.internationalization_analyti'))
    click.echo('=' * 50)
    try:
        i18n_manager = I18nManager()
        active_languages = Language.query.filter_by(is_active=True).count()
        total_content_items = MultilingualContent.query.filter_by(is_current
            =True).count()
        user_preferences = UserLanguagePreference.query.count()
        click.echo(f'📈 Overview:')
        click.echo(f'   Active languages: {active_languages}')
        click.echo(f'   Content items: {total_content_items}')
        click.echo(f'   User preferences: {user_preferences}')
        analytics_data = i18n_manager.get_translation_analytics(days=30)
        if analytics_data:
            click.echo(f'\n📅 Last 30 Days:')
            click.echo(
                f"   Recent translations: {analytics_data.get('recent_translations', 0)}"
                )
            if analytics_data.get('language_usage'):
                click.echo(f'\n🌐 Language Usage:')
                for lang, count in analytics_data['language_usage'].items():
                    click.echo(f'   {lang}: {count}')
            if analytics_data.get('translation_methods'):
                click.echo(f'\n🔧 Translation Methods:')
                for method, count in analytics_data['translation_methods'
                    ].items():
                    click.echo(f'   {method}: {count}')
            avg_quality = analytics_data.get('average_quality')
            if avg_quality:
                click.echo(f'\n⭐ Average Quality Score: {avg_quality:.2f}')
        coverage_report = i18n_manager.get_language_coverage_report()
        if coverage_report and 'summary' in coverage_report:
            summary = coverage_report['summary']
            click.echo(f'\n🎯 Language Coverage:')
            click.echo(f"   Total entities: {summary.get('total_entities', 0)}"
                )
            click.echo(
                f"   Complete entities: {summary.get('complete_entities', 0)}")
            click.echo(
                f"   Overall coverage: {summary.get('overall_coverage_percentage', 0):.1f}%"
                )
        click.echo('=' * 50)
    except Exception as e:
        logger.error(f'Error generating analytics: {e}')
        click.echo(f'❌ Error: {e}', err=True)


@i18n.command()
@click.option(_('cli_i18n_commands.message.days_1'), '-d', default=90, help
    =_('cli_i18n_commands.message.clean_translations_older_than'))
@click.confirmation_option(prompt=_(
    'cli_i18n_commands.message.are_you_sure_you_want_to_clean'))
@with_appcontext
def cleanup():
    _('i18n_i18n_manager.message.clean_up_old_translation_versi')
    click.echo(f'🧹 Cleaning up translations older than {days} days...')
    try:
        i18n_manager = I18nManager()
        result = i18n_manager.cleanup_old_translations(days_old=days)
        if 'error' in result:
            click.echo(f"❌ Error: {result['error']}", err=True)
            return
        click.echo(f'✅ Cleanup completed:')
        click.echo(f"   Removed versions: {result.get('removed_versions', 0)}")
        click.echo(
            f"   Removed TM entries: {result.get('removed_translation_memory', 0)}"
            )
        click.echo(f"   Cleanup date: {result.get('cleanup_date', 'Unknown')}")
    except Exception as e:
        logger.error(f'Error during cleanup: {e}')
        click.echo(f'❌ Error: {e}', err=True)


@i18n.command()
@click.option(_('cli_i18n_commands.message.entity_type'), '-t', required=
    True, help=_('cli_i18n_commands.message.entity_type_e_g_program'))
@click.option(_('cli_i18n_commands.message.entity_id'), '-i', required=True,
    help=_('cli_i18n_commands.label.entity_id'))
@click.option(_('cli_i18n_commands.message.source_lang'), '-s', default=
    'en', help=_('cli_i18n_commands.label.source_language'))
@click.option(_('cli_i18n_commands.message.target_langs'), '-l', required=
    True, help=_('cli_i18n_commands.label.target_languages_comma_separa'))
@with_appcontext
def translate_entity():
    _('cli_i18n_commands.message.translate_all_content_for_a_sp')
    target_languages = [lang.strip() for lang in target_langs.split(',')]
    click.echo(
        f"🔄 Translating {entity_type}:{entity_id} from {source_lang} to {', '.join(target_languages)}..."
        )
    try:
        i18n_manager = I18nManager()
        result = i18n_manager.translate_entity_content(entity_type=
            entity_type, entity_id=entity_id, source_language=source_lang,
            target_languages=target_languages)
        if 'error' in result:
            click.echo(f"❌ Error: {result['error']}", err=True)
            return
        click.echo(f'✅ Translation completed:')
        click.echo(f"   Success: {result.get('success_count', 0)}")
        click.echo(f"   Errors: {result.get('error_count', 0)}")
        if result.get('translations'):
            click.echo(f"   Created {len(result['translations'])} translations"
                )
    except Exception as e:
        logger.error(f'Error translating entity: {e}')
        click.echo(f'❌ Error: {e}', err=True)


@i18n.command()
@with_appcontext
def validate():
    _('cli_i18n_commands.validation.validate_i18n_configuration_an')
    click.echo(_('cli_i18n_commands.validation.validating_i18n_configuratio'))
    try:
        errors = []
        warnings = []
        try:
            Language.query.first()
            MultilingualContent.query.first()
            UserLanguagePreference.query.first()
        except Exception as e:
            errors.append(f'Database tables missing or corrupted: {e}')
        language_service = LanguageDetectionService()
        translation_service = TranslationService()
        for lang_code in language_service.SUPPORTED_LANGUAGES.keys():
            try:
                translations = translation_service.get_translation_dict(
                    lang_code)
                if not translations:
                    warnings.append(f'Empty translation file for {lang_code}')
            except Exception as e:
                errors.append(
                    f'Error loading translations for {lang_code}: {e}')
        db_languages = {lang.code for lang in Language.query.filter_by(
            is_active=True).all()}
        service_languages = set(language_service.SUPPORTED_LANGUAGES.keys())
        missing_in_db = service_languages - db_languages
        missing_in_service = db_languages - service_languages
        if missing_in_db:
            warnings.append(
                f'Languages in service but not in DB: {missing_in_db}')
        if missing_in_service:
            warnings.append(
                f'Languages in DB but not in service: {missing_in_service}')
        if errors:
            click.echo(_('cli_i18n_commands.error.validation_errors'))
            for error in errors:
                click.echo(f'   • {error}')
        if warnings:
            click.echo(_('cli_i18n_commands.validation.validation_warnings'))
            for warning in warnings:
                click.echo(f'   • {warning}')
        if not errors and not warnings:
            click.echo(_(
                'cli_i18n_commands.validation.all_i18n_validations_passed'))
        click.echo(f'\n📊 Validation Summary:')
        click.echo(f'   Errors: {len(errors)}')
        click.echo(f'   Warnings: {len(warnings)}')
    except Exception as e:
        logger.error(f'Error during validation: {e}')
        click.echo(f'❌ Validation failed: {e}', err=True)


def register_i18n_commands(app):
    _('cli_i18n_commands.message.register_i18n_cli_commands_wit')
    app.cli.add_command(i18n)
