"""
CLI commands for turtle-db database management.
"""
import asyncio
import click
import logging
from typing import Optional

from turtle_db.database.connection import create_tables, run_migrations
from turtle_db.database.migrations import run_database_migration
from turtle_db.database.enhanced_seed_data import seed_enhanced_database
from turtle_db.database.seed_data import seed_database

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@click.group()
def cli():
    """turtle-db database management CLI."""
    pass


@cli.command()
@click.option('--drop', is_flag=True, help='Drop existing tables before creating new ones')
def init_db(drop: bool):
    """Initialize database with enhanced schema."""
    async def _init():
        try:
            logger.info("Initializing database...")
            
            if drop:
                logger.warning("Dropping existing tables...")
                from turtle_db.database.enhanced_models import Base
                from turtle_db.database.connection import engine
                async with engine.begin() as conn:
                    await conn.run_sync(Base.metadata.drop_all)
                logger.info("Existing tables dropped")
            
            await create_tables()
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise click.ClickException(f"Database initialization failed: {e}")
    
    asyncio.run(_init())


@cli.command()
def migrate():
    """Run database migrations to upgrade schema."""
    async def _migrate():
        try:
            logger.info("Running database migrations...")
            await run_database_migration()
            logger.info("Database migrations completed successfully")
            
        except Exception as e:
            logger.error(f"Database migration failed: {e}")
            raise click.ClickException(f"Database migration failed: {e}")
    
    asyncio.run(_migrate())


@cli.command()
@click.option('--enhanced', is_flag=True, help='Use enhanced comprehensive WoW data')
@click.option('--force', is_flag=True, help='Force re-seeding (may duplicate data)')
def seed(enhanced: bool, force: bool):
    """Seed database with reference data."""
    async def _seed():
        try:
            if enhanced:
                logger.info("Seeding database with comprehensive WoW data...")
                await seed_enhanced_database()
                logger.info("Enhanced database seeding completed successfully")
            else:
                logger.info("Seeding database with basic data...")
                await seed_database()
                logger.info("Basic database seeding completed successfully")
                
        except Exception as e:
            logger.error(f"Database seeding failed: {e}")
            raise click.ClickException(f"Database seeding failed: {e}")
    
    asyncio.run(_seed())


@cli.command()
@click.option('--enhanced', is_flag=True, help='Use enhanced schema and comprehensive data')
def setup(enhanced: bool):
    """Complete database setup: initialize, migrate, and seed."""
    async def _setup():
        try:
            logger.info("Starting complete database setup...")
            
            # Initialize database
            logger.info("Step 1/3: Initializing database...")
            await create_tables()
            
            # Run migrations
            logger.info("Step 2/3: Running migrations...")
            await run_database_migration()
            
            # Seed data
            logger.info("Step 3/3: Seeding data...")
            if enhanced:
                await seed_enhanced_database()
                logger.info("Setup completed with enhanced WoW data")
            else:
                await seed_database()
                logger.info("Setup completed with basic data")
            
            logger.info("✅ Complete database setup finished successfully!")
            
        except Exception as e:
            logger.error(f"Database setup failed: {e}")
            raise click.ClickException(f"Database setup failed: {e}")
    
    asyncio.run(_setup())


@cli.command()
@click.option('--table', help='Check specific table')
def check_db(table: Optional[str]):
    """Check database status and statistics."""
    async def _check():
        try:
            from turtle_db.database.connection import AsyncSessionLocal
            from turtle_db.database.enhanced_models import ItemType, ItemSubtype, ItemSlot, Profession, Item
            from sqlalchemy import select, func
            
            async with AsyncSessionLocal() as db:
                logger.info("Checking database status...")
                
                # Check each table
                tables_to_check = [
                    ("item_types", ItemType),
                    ("item_subtypes", ItemSubtype),
                    ("item_slots", ItemSlot),
                    ("professions", Profession),
                    ("items", Item)
                ]
                
                if table:
                    # Filter to specific table
                    tables_to_check = [(t, m) for t, m in tables_to_check if t == table]
                
                for table_name, model in tables_to_check:
                    try:
                        result = await db.execute(select(func.count()).select_from(model))
                        count = result.scalar()
                        logger.info(f"📊 {table_name}: {count} records")
                    except Exception as e:
                        logger.error(f"❌ {table_name}: Error - {e}")
                
                logger.info("Database check completed")
                
        except Exception as e:
            logger.error(f"Database check failed: {e}")
            raise click.ClickException(f"Database check failed: {e}")
    
    asyncio.run(_check())


@cli.command()
def version():
    """Show database schema version and migration status."""
    async def _version():
        try:
            from turtle_db.database.connection import AsyncSessionLocal
            from sqlalchemy import text
            
            async with AsyncSessionLocal() as db:
                try:
                    # Check if migration table exists
                    result = await db.execute(text("""
                        SELECT name FROM sqlite_master 
                        WHERE type='table' AND name='schema_migrations'
                    """))
                    if result.fetchone():
                        # Get migration status
                        result = await db.execute(text("""
                            SELECT migration_name, completed_at 
                            FROM schema_migrations 
                            ORDER BY completed_at DESC
                        """))
                        migrations = result.fetchall()
                        
                        if migrations:
                            logger.info("📋 Completed migrations:")
                            for migration_name, completed_at in migrations:
                                logger.info(f"  ✅ {migration_name} - {completed_at}")
                        else:
                            logger.info("📋 No migrations completed yet")
                    else:
                        logger.info("📋 No migration tracking table found")
                        
                except Exception as e:
                    logger.error(f"Error checking migrations: {e}")
                
        except Exception as e:
            logger.error(f"Version check failed: {e}")
            raise click.ClickException(f"Version check failed: {e}")
    
    asyncio.run(_version())


if __name__ == '__main__':
    cli()