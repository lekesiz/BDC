"""Enhanced CLI commands for the new architecture."""

import click
from flask.cli import with_appcontext
from typing import List


@click.command()
@click.option('--create-tables', is_flag=True, default=True, help='Create database tables')
@click.option('--with-test-data', is_flag=True, help='Create test users and data')
@with_appcontext
def init_db(create_tables, with_test_data):
    """Initialize the database with the new architecture."""
    from flask import current_app
    from app.core.database_manager import database_initializer
    
    click.echo('Initializing database with new architecture...')
    
    success = database_initializer.initialize_database(
        current_app, 
        create_tables=create_tables,
        create_test_data=with_test_data
    )
    
    if success:
        if with_test_data:
            click.echo('✅ Database initialized with test data.')
        else:
            click.echo('✅ Database initialized.')
    else:
        click.echo('❌ Database initialization failed. Check logs for details.')
        exit(1)


@click.command()
@with_appcontext
def create_test_data():
    """Create test users and data."""
    from flask import current_app
    from app.core.database_manager import database_initializer
    
    click.echo('Creating test data...')
    
    success = database_initializer.initialize_database(
        current_app,
        create_tables=False,
        create_test_data=True
    )
    
    if success:
        click.echo('✅ Test data created successfully.')
    else:
        click.echo('❌ Test data creation failed. Check logs for details.')
        exit(1)


@click.command()
@click.argument('migration_name', required=False)
@with_appcontext
def run_migration(migration_name):
    """Run database migrations."""
    from app.core.database_manager import migration_manager
    
    if migration_name:
        click.echo(f'Running migration: {migration_name}')
        result = migration_manager.run_migration(migration_name)
        
        if result.status.value == 'success':
            click.echo(f'✅ {result.message}')
        elif result.status.value == 'skipped':
            click.echo(f'⏭️  {result.message}')
        else:
            click.echo(f'❌ {result.message}')
            if result.error:
                click.echo(f'Error: {result.error}')
            exit(1)
    else:
        click.echo('Running all migrations...')
        results = migration_manager.run_all_migrations()
        
        successful = sum(1 for r in results if r.status.value == 'success')
        skipped = sum(1 for r in results if r.status.value == 'skipped')
        failed = sum(1 for r in results if r.status.value == 'failed')
        
        click.echo(f'Migration summary: {successful} successful, {skipped} skipped, {failed} failed')
        
        if failed > 0:
            click.echo('❌ Some migrations failed. Check logs for details.')
            exit(1)
        else:
            click.echo('✅ All migrations completed successfully.')


@click.command()
@with_appcontext
def list_migrations():
    """List available migrations."""
    from app.core.database_manager import migration_manager
    
    migrations = migration_manager.get_available_migrations()
    
    if migrations:
        click.echo('Available migrations:')
        for migration in migrations:
            click.echo(f'  - {migration}')
    else:
        click.echo('No migrations available.')


@click.command()
@with_appcontext
def validate_config():
    """Validate application configuration."""
    from flask import current_app
    from app.core.config_manager import config_manager
    
    click.echo('Validating application configuration...')
    
    # Re-validate current configuration
    result = config_manager._validate_configuration(current_app.config)
    
    if result.is_valid:
        click.echo('✅ Configuration is valid.')
        
        if result.warnings:
            click.echo('\nWarnings:')
            for warning in result.warnings:
                click.echo(f'  ⚠️  {warning}')
    else:
        click.echo('❌ Configuration validation failed.')
        
        if result.errors:
            click.echo('\nErrors:')
            for error in result.errors:
                click.echo(f'  ❌ {error}')
        
        if result.warnings:
            click.echo('\nWarnings:')
            for warning in result.warnings:
                click.echo(f'  ⚠️  {warning}')
        
        exit(1)


@click.command()
@with_appcontext
def check_extensions():
    """Check extension initialization status."""
    from app.core.extension_manager import extension_manager
    
    click.echo('Checking extension status...')
    
    initialized_extensions = extension_manager.get_initialized_extensions()
    
    if initialized_extensions:
        click.echo('✅ Initialized extensions:')
        for ext in initialized_extensions:
            click.echo(f'  - {ext}')
    else:
        click.echo('❌ No extensions initialized.')


@click.command()
@with_appcontext
def check_services():
    """Check dependency injection services."""
    from app.core.lazy_container import lazy_container
    
    click.echo('Checking DI container services...')
    
    # List of key services to check
    service_checks = [
        ('app.services.interfaces.auth_service_interface.IAuthService', 'Auth Service'),
        ('app.services.interfaces.user_repository_interface.IUserRepository', 'User Repository'),
        ('app.services.interfaces.document_service_interface.IDocumentService', 'Document Service'),
        ('app.services.interfaces.evaluation_service_interface.IEvaluationService', 'Evaluation Service'),
    ]
    
    all_available = True
    
    for service_path, service_name in service_checks:
        try:
            # Dynamic import to check service availability
            module_path, class_name = service_path.rsplit('.', 1)
            module = __import__(module_path, fromlist=[class_name])
            service_class = getattr(module, class_name)
            
            if lazy_container.is_registered(service_class):
                click.echo(f'✅ {service_name} - registered')
            else:
                click.echo(f'❌ {service_name} - not registered')
                all_available = False
                
        except Exception as e:
            click.echo(f'❌ {service_name} - error: {e}')
            all_available = False
    
    if all_available:
        click.echo('\n✅ All key services are available.')
    else:
        click.echo('\n❌ Some services are missing or misconfigured.')


def register_cli_commands(app):
    """Register enhanced CLI commands with the app."""
    app.cli.add_command(init_db)
    app.cli.add_command(create_test_data)
    app.cli.add_command(run_migration)
    app.cli.add_command(list_migrations)
    app.cli.add_command(validate_config)
    app.cli.add_command(check_extensions)
    app.cli.add_command(check_services)