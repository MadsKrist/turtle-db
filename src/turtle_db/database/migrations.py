"""
Database migration utilities for upgrading to enhanced schema.
"""
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
import logging

from turtle_db.database.connection import AsyncSessionLocal, engine

logger = logging.getLogger(__name__)

class DatabaseMigration:
    """Handles database schema migrations."""
    
    def __init__(self):
        self.migrations = [
            self._migration_001_add_item_columns,
            self._migration_002_add_vendor_columns, 
            self._migration_003_add_recipe_columns,
            self._migration_004_add_reference_table_columns,
            self._migration_005_create_item_sets_tables,
            self._migration_006_create_indexes,
            self._migration_007_populate_reference_data
        ]
    
    async def run_migrations(self) -> None:
        """Run all pending migrations."""
        async with AsyncSessionLocal() as db:
            try:
                # Create migration tracking table if it doesn't exist
                await self._create_migration_table(db)
                
                # Get completed migrations
                completed = await self._get_completed_migrations(db)
                
                # Run pending migrations
                for i, migration in enumerate(self.migrations, 1):
                    migration_name = f"migration_{i:03d}"
                    
                    if migration_name not in completed:
                        logger.info(f"Running {migration_name}...")
                        await migration(db)
                        await self._mark_migration_complete(db, migration_name)
                        logger.info(f"Completed {migration_name}")
                    else:
                        logger.info(f"Skipping {migration_name} (already completed)")
                
                await db.commit()
                logger.info("All migrations completed successfully")
                
            except Exception as e:
                logger.error(f"Migration failed: {str(e)}")
                await db.rollback()
                raise
    
    async def _create_migration_table(self, db: AsyncSession) -> None:
        """Create table to track completed migrations."""
        await db.execute(text("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                migration_name VARCHAR(255) NOT NULL UNIQUE,
                completed_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """))
        await db.commit()
    
    async def _get_completed_migrations(self, db: AsyncSession) -> List[str]:
        """Get list of completed migration names."""
        result = await db.execute(text("SELECT migration_name FROM schema_migrations"))
        return [row[0] for row in result.fetchall()]
    
    async def _mark_migration_complete(self, db: AsyncSession, migration_name: str) -> None:
        """Mark a migration as completed."""
        await db.execute(text("""
            INSERT INTO schema_migrations (migration_name) VALUES (:name)
        """), {"name": migration_name})
    
    async def _migration_001_add_item_columns(self, db: AsyncSession) -> None:
        """Add enhanced columns to items table."""
        
        # Check if columns already exist before adding
        columns_to_add = [
            ("required_class", "VARCHAR(100)"),
            ("required_race", "VARCHAR(100)"), 
            ("unique_equipped", "BOOLEAN DEFAULT FALSE"),
            ("stats", "TEXT"),
            ("durability", "INTEGER"),
            ("charges", "INTEGER"),
            ("cooldown_seconds", "INTEGER"),
            ("external_id", "INTEGER"),
            ("external_source", "VARCHAR(50)")
        ]
        
        for column_name, column_def in columns_to_add:
            try:
                await db.execute(text(f"""
                    ALTER TABLE items ADD COLUMN {column_name} {column_def}
                """))
            except Exception as e:
                # Column might already exist, check if it's a duplicate column error
                if "duplicate column" in str(e).lower():
                    logger.info(f"Column {column_name} already exists, skipping")
                else:
                    raise
    
    async def _migration_002_add_vendor_columns(self, db: AsyncSession) -> None:
        """Add enhanced columns to vendors and vendor_items tables."""
        
        # Vendors table columns
        vendor_columns = [
            ("zone", "VARCHAR(50)"),
            ("subzone", "VARCHAR(50)"),
            ("vendor_type", "VARCHAR(30)"),
            ("coordinates", "VARCHAR(20)")
        ]
        
        for column_name, column_def in vendor_columns:
            try:
                await db.execute(text(f"""
                    ALTER TABLE vendors ADD COLUMN {column_name} {column_def}
                """))
            except Exception as e:
                if "duplicate column" in str(e).lower():
                    logger.info(f"Column {column_name} already exists, skipping")
                else:
                    raise
        
        # Vendor items table columns
        vendor_item_columns = [
            ("required_faction", "VARCHAR(20)"),
            ("required_level", "INTEGER"),
            ("available_start_date", "DATE"),
            ("available_end_date", "DATE")
        ]
        
        for column_name, column_def in vendor_item_columns:
            try:
                await db.execute(text(f"""
                    ALTER TABLE vendor_items ADD COLUMN {column_name} {column_def}
                """))
            except Exception as e:
                if "duplicate column" in str(e).lower():
                    logger.info(f"Column {column_name} already exists, skipping")
                else:
                    raise
    
    async def _migration_003_add_recipe_columns(self, db: AsyncSession) -> None:
        """Add enhanced columns to recipes and recipe_ingredients tables."""
        
        # Recipes table columns
        recipe_columns = [
            ("creates_quantity", "INTEGER DEFAULT 1"),
            ("recipe_difficulty", "VARCHAR(20) DEFAULT 'yellow'"),
            ("teaches_spell_id", "INTEGER"),
            ("required_reputation", "VARCHAR(50)"),
            ("required_faction", "VARCHAR(20)"),
            ("required_level", "INTEGER"),
            ("external_id", "INTEGER"),
            ("external_source", "VARCHAR(50)")
        ]
        
        for column_name, column_def in recipe_columns:
            try:
                await db.execute(text(f"""
                    ALTER TABLE recipes ADD COLUMN {column_name} {column_def}
                """))
            except Exception as e:
                if "duplicate column" in str(e).lower():
                    logger.info(f"Column {column_name} already exists, skipping")
                else:
                    raise
        
        # Recipe ingredients table columns
        ingredient_columns = [
            ("is_optional", "BOOLEAN DEFAULT FALSE"),
            ("ingredient_group", "INTEGER DEFAULT 1")
        ]
        
        for column_name, column_def in ingredient_columns:
            try:
                await db.execute(text(f"""
                    ALTER TABLE recipe_ingredients ADD COLUMN {column_name} {column_def}
                """))
            except Exception as e:
                if "duplicate column" in str(e).lower():
                    logger.info(f"Column {column_name} already exists, skipping")
                else:
                    raise
        
        # Add created_at if it doesn't exist (SQLite compatible)
        try:
            await db.execute(text("""
                ALTER TABLE recipe_ingredients ADD COLUMN created_at DATETIME
            """))
            # Update existing rows with current timestamp
            await db.execute(text("""
                UPDATE recipe_ingredients SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL
            """))
        except Exception as e:
            if "duplicate column" in str(e).lower():
                logger.info("Column created_at already exists in recipe_ingredients, skipping")
            else:
                raise
    
    async def _migration_004_add_reference_table_columns(self, db: AsyncSession) -> None:
        """Add enhanced columns to reference tables."""
        
        # Add columns to existing reference tables
        reference_tables = [
            ("item_types", [("sort_order", "INTEGER DEFAULT 0"), ("created_at", "DATETIME")]),
            ("item_subtypes", [("sort_order", "INTEGER DEFAULT 0"), ("created_at", "DATETIME")]),
            ("item_slots", [("slot_type", "VARCHAR(20)"), ("sort_order", "INTEGER DEFAULT 0"), ("created_at", "DATETIME")]),
            ("professions", [("profession_type", "VARCHAR(20) DEFAULT 'primary'"), ("created_at", "DATETIME")])
        ]
        
        for table_name, columns in reference_tables:
            for column_name, column_def in columns:
                try:
                    await db.execute(text(f"""
                        ALTER TABLE {table_name} ADD COLUMN {column_name} {column_def}
                    """))
                    # Update timestamps for created_at columns
                    if column_name == "created_at":
                        await db.execute(text(f"""
                            UPDATE {table_name} SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL
                        """))
                except Exception as e:
                    if "duplicate column" in str(e).lower():
                        logger.info(f"Column {column_name} already exists in {table_name}, skipping")
                    else:
                        raise
    
    async def _migration_005_create_item_sets_tables(self, db: AsyncSession) -> None:
        """Create item sets related tables."""
        
        # Create item_sets table
        await db.execute(text("""
            CREATE TABLE IF NOT EXISTS item_sets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL UNIQUE,
                description TEXT,
                set_type VARCHAR(30),
                tier_level VARCHAR(10),
                created_at DATETIME
            )
        """))
        
        # Create item_set_pieces table  
        await db.execute(text("""
            CREATE TABLE IF NOT EXISTS item_set_pieces (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                set_id INTEGER NOT NULL,
                item_id INTEGER NOT NULL,
                piece_name VARCHAR(50),
                sort_order INTEGER DEFAULT 0,
                created_at DATETIME,
                FOREIGN KEY (set_id) REFERENCES item_sets(id),
                FOREIGN KEY (item_id) REFERENCES items(id),
                UNIQUE(set_id, item_id)
            )
        """))
        
        # Create item_set_bonuses table
        await db.execute(text("""
            CREATE TABLE IF NOT EXISTS item_set_bonuses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                set_id INTEGER NOT NULL,
                pieces_required INTEGER NOT NULL,
                bonus_description TEXT NOT NULL,
                bonus_stats TEXT,
                created_at DATETIME,
                FOREIGN KEY (set_id) REFERENCES item_sets(id),
                UNIQUE(set_id, pieces_required)
            )
        """))
    
    async def _migration_006_create_indexes(self, db: AsyncSession) -> None:
        """Create performance indexes for enhanced schema."""
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_items_external ON items(external_source, external_id)",
            "CREATE INDEX IF NOT EXISTS idx_items_name ON items(name)",
            "CREATE INDEX IF NOT EXISTS idx_items_bind_type ON items(bind_type)",
            "CREATE INDEX IF NOT EXISTS idx_vendor_items_faction ON vendor_items(required_faction)",
            "CREATE INDEX IF NOT EXISTS idx_recipes_skill ON recipes(required_skill_level)", 
            "CREATE INDEX IF NOT EXISTS idx_recipes_external ON recipes(external_source, external_id)",
            "CREATE INDEX IF NOT EXISTS idx_item_set_pieces_set ON item_set_pieces(set_id)",
            "CREATE INDEX IF NOT EXISTS idx_item_set_pieces_item ON item_set_pieces(item_id)"
        ]
        
        for index_sql in indexes:
            await db.execute(text(index_sql))
    
    async def _migration_007_populate_reference_data(self, db: AsyncSession) -> None:
        """Populate reference tables with comprehensive WoW data."""
        
        # This will be handled by the enhanced seed data script
        # Just ensure the migration completes
        pass


async def run_database_migration():
    """Entry point for running database migrations."""
    migration = DatabaseMigration()
    await migration.run_migrations()


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_database_migration())