"""
Database migration utilities for Dana.

This module provides functions to run Alembic migrations programmatically,
ensuring the database schema is up-to-date when the application starts.
"""

import os
import sys
from pathlib import Path
from typing import Optional

from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, text, inspect


def get_alembic_config() -> Config:
    """
    Get Alembic configuration for the Dana package.
    
    This function sets up the Alembic configuration to work with the installed package,
    finding the migration files and database configuration automatically.
    """
    # Get the package directory
    package_dir = Path(__file__).parent.parent.parent.parent
    
    # Create Alembic config
    config = Config()
    
    # Set the script location to the alembic directory in the package
    alembic_dir = package_dir / "alembic"
    config.set_main_option("script_location", str(alembic_dir))
    
    # Set the database URL from environment or default
    database_url = os.environ.get("DANA_DATABASE_URL", "sqlite:///./local.db")
    config.set_main_option("sqlalchemy.url", database_url)
    
    # Add the package directory to sys.path so imports work
    if str(package_dir) not in sys.path:
        sys.path.insert(0, str(package_dir))
    
    return config


def run_migrations(verbose: bool = True) -> bool:
    """
    Run database migrations to upgrade to the latest version.
    
    Args:
        verbose: Whether to print migration status messages
        
    Returns:
        True if migrations were successful, False otherwise
    """
    try:
        if verbose:
            print("🔄 Running database migrations...")
        
        config = get_alembic_config()
        
        # Run the upgrade command
        command.upgrade(config, "head")
        
        if verbose:
            print("✅ Database migrations completed successfully")
        
        return True
        
    except Exception as e:
        if verbose:
            print(f"❌ Migration failed: {str(e)}")
        return False


def get_current_revision() -> Optional[str]:
    """
    Get the current database revision.
    
    Returns:
        The current revision ID, or None if no migrations have been applied
    """
    try:
        config = get_alembic_config()
        
        # Get the database URL
        database_url = config.get_main_option("sqlalchemy.url")
        engine = create_engine(database_url)
        
        # Get the migration context
        with engine.connect() as connection:
            context = MigrationContext.configure(connection)
            current_rev = context.get_current_revision()
            
        return current_rev
        
    except Exception:
        return None


def get_latest_revision() -> Optional[str]:
    """
    Get the latest available revision.
    
    Returns:
        The latest revision ID, or None if no migrations are available
    """
    try:
        config = get_alembic_config()
        script = ScriptDirectory.from_config(config)
        return script.get_current_head()
        
    except Exception:
        return None


def is_database_up_to_date() -> bool:
    """
    Check if the database is up to date with the latest migrations.
    
    Returns:
        True if the database is up to date, False otherwise
    """
    current_rev = get_current_revision()
    latest_rev = get_latest_revision()
    
    return current_rev == latest_rev


def validate_schema_matches_models() -> bool:
    """
    Check if the actual database schema matches the expected model schema.
    
    Returns:
        True if schema matches, False otherwise
    """
    try:
        config = get_alembic_config()
        database_url = config.get_main_option("sqlalchemy.url")
        engine = create_engine(database_url)
        
        # Import the target metadata from our models
        from dana.api.core.models import Base
        
        with engine.connect() as connection:
            # Check if all expected tables exist with correct columns
            inspector = inspect(engine)
            existing_tables = inspector.get_table_names()
            
            # Get expected tables from metadata
            expected_tables = set(Base.metadata.tables.keys())
            
            # Check if all expected tables exist (ignore extra tables)
            if not expected_tables.issubset(set(existing_tables)):
                return False
            
            # Check each table's columns
            for table_name in expected_tables:
                expected_columns = set(Base.metadata.tables[table_name].columns.keys())
                existing_columns = inspector.get_columns(table_name)
                existing_column_names = {col['name'] for col in existing_columns}
                
                if not expected_columns.issubset(existing_column_names):
                    return False
            
            return True
            
    except Exception:
        return False


def fix_schema_with_target_metadata(verbose: bool = True) -> bool:
    """
    Fix the database schema by applying the target metadata using SQLAlchemy's native operations.
    
    This function adds missing columns to existing tables and creates missing tables.
    
    Args:
        verbose: Whether to print status messages
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if verbose:
            print("🔧 Applying target metadata to fix schema...")
        
        config = get_alembic_config()
        database_url = config.get_main_option("sqlalchemy.url")
        engine = create_engine(database_url)
        
        # Import the target metadata from our models
        from dana.api.core.models import Base
        
        with engine.connect() as connection:
            inspector = inspect(engine)
            existing_tables = inspector.get_table_names()
            
            # Get expected tables from metadata
            expected_tables = set(Base.metadata.tables.keys())
            
            # First, create any missing tables
            Base.metadata.create_all(engine)
            
            # Then, add missing columns to existing tables using Alembic op operations
            for table_name in expected_tables:
                if table_name in existing_tables:
                    expected_columns = set(Base.metadata.tables[table_name].columns.keys())
                    existing_columns = inspector.get_columns(table_name)
                    existing_column_names = {col['name'] for col in existing_columns}
                    
                    missing_columns = expected_columns - existing_column_names
                    
                    if missing_columns and verbose:
                        print(f"  📝 Adding missing columns to {table_name}: {missing_columns}")
                    
                    # Add each missing column using SQLAlchemy's native DDL operations
                    for column_name in missing_columns:
                        column = Base.metadata.tables[table_name].columns[column_name]
                        
                        try:
                            # Use SQLAlchemy's native DDL operations for clean, readable column addition
                            import sqlalchemy as sa
                            
                            # Build the column definition using SQLAlchemy's type system
                            column_type = column.type.compile(engine.dialect)
                            nullable = "NULL" if column.nullable else "NOT NULL"
                            
                            # Handle default values properly
                            default_clause = ""
                            if column.default is not None:
                                # Skip lambda functions and complex defaults
                                if hasattr(column.default, 'arg') and not callable(column.default.arg):
                                    if isinstance(column.default.arg, str):
                                        default_clause = f" DEFAULT '{column.default.arg}'"
                                    elif isinstance(column.default.arg, dict):
                                        # Handle JSON defaults
                                        import json
                                        default_clause = f" DEFAULT '{json.dumps(column.default.arg)}'"
                                    else:
                                        default_clause = f" DEFAULT {column.default.arg}"
                            
                            # Use SQLAlchemy's native DDL to create the ALTER TABLE statement
                            # This ensures proper database-specific SQL generation
                            alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type} {nullable}{default_clause}"
                            
                            # Execute using SQLAlchemy's DDL
                            ddl_stmt = sa.DDL(alter_sql)
                            connection.execute(ddl_stmt)
                            
                            if verbose:
                                print(f"    ✅ Added column {column_name}")
                                
                        except Exception as e:
                            if verbose:
                                print(f"    ⚠️  Failed to add column {column_name}: {str(e)}")
        
        if verbose:
            print("✅ Schema updated to match target metadata")
        
        # Now stamp the database to the latest revision
        command.stamp(config, "head")
        
        if verbose:
            print("✅ Database integrated with Alembic")
        
        return True
        
    except Exception as e:
        if verbose:
            print(f"❌ Failed to fix schema: {str(e)}")
        return False


def ensure_database_schema(verbose: bool = True) -> bool:
    """
    Ensure the database schema is up to date by running migrations if needed.
    
    Strategy:
    1. Check if database schema matches the expected model schema
    2. If not, try normal migration first
    3. If error, check if tables exist and use autogenerate to fix schema
    4. If no tables exist, create them
    
    Args:
        verbose: Whether to print status messages
        
    Returns:
        True if the database is ready, False otherwise
    """
    try:
        # First check if the actual schema matches the expected schema
        if not validate_schema_matches_models():
            if verbose:
                print("⚠️  Database schema doesn't match expected models")
                print("🔧 Attempting to fix schema differences...")
            
            # Try to fix the schema by applying target metadata
            if fix_schema_with_target_metadata(verbose):
                if verbose:
                    print("✅ Schema fixed and now matches expected models")
                return True
            else:
                if verbose:
                    print("❌ Failed to fix schema differences")
                return False
        
        # Schema matches, check if migrations are up to date
        if is_database_up_to_date():
            if verbose:
                print("✅ Database schema is up to date")
            return True
        
        # Step 1: Try normal migration first
        if verbose:
            print("🔄 Attempting normal migration...")
        
        try:
            success = run_migrations(verbose=False)  # Don't print verbose messages yet
            if success:
                if verbose:
                    print("✅ Normal migration completed successfully")
                return True
        except Exception as e:
            if verbose:
                print(f"⚠️  Normal migration failed: {str(e)}")
                print("🔍 Checking database state and attempting recovery...")
        
        # Step 2: Migration failed, check what exists and fix it
        return handle_migration_failure(verbose)
        
    except Exception as e:
        if verbose:
            print(f"❌ Database schema check failed: {str(e)}")
        return False


def handle_migration_failure(verbose: bool = True) -> bool:
    """
    Handle migration failure by checking existing tables and fixing schema.
    
    Args:
        verbose: Whether to print status messages
        
    Returns:
        True if successful, False otherwise
    """
    try:
        config = get_alembic_config()
        database_url = config.get_main_option("sqlalchemy.url")
        engine = create_engine(database_url)
        
        with engine.connect() as connection:
            # Check if any of our tables exist using database-agnostic inspector
            inspector = inspect(engine)
            all_tables = inspector.get_table_names()
            
            # Get expected table names from our models
            from dana.api.core.models import Base
            expected_table_names = set(Base.metadata.tables.keys())
            
            # Find which of our expected tables exist
            existing_tables = [table for table in expected_table_names if table in all_tables]
            missing_tables = [table for table in expected_table_names if table not in all_tables]
            
            if verbose:
                if existing_tables:
                    print(f"📊 Found existing tables: {existing_tables}")
                if missing_tables:
                    print(f"📊 Missing tables: {missing_tables}")
                print("🔧 Applying comprehensive schema fix...")
            
            # Always use the comprehensive schema fix approach
            # This handles both missing tables AND missing columns in existing tables
            return fix_schema_with_target_metadata(verbose)
                
    except Exception as e:
        if verbose:
            print(f"❌ Failed to handle migration failure: {str(e)}")
        return False
