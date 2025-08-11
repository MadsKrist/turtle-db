"""Database package with enhanced models and migration support."""

from .connection import get_async_session, create_tables, run_migrations
from .enhanced_models import (
    Base,
    ItemType,
    ItemSubtype, 
    ItemSlot,
    Profession,
    Item,
    Vendor,
    VendorItem,
    Recipe,
    RecipeIngredient,
    ItemSet,
    ItemSetPiece,
    ItemSetBonus
)
from .migrations import run_database_migration
from .enhanced_seed_data import seed_enhanced_database

__all__ = [
    # Connection utilities
    "get_async_session",
    "create_tables", 
    "run_migrations",
    
    # Models
    "Base",
    "ItemType",
    "ItemSubtype",
    "ItemSlot", 
    "Profession",
    "Item",
    "Vendor",
    "VendorItem",
    "Recipe",
    "RecipeIngredient",
    "ItemSet",
    "ItemSetPiece",
    "ItemSetBonus",
    
    # Migration and seeding
    "run_database_migration",
    "seed_enhanced_database"
]