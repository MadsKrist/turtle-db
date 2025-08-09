"""
Data mapping service for converting scraped data to database models.
"""

import logging
from typing import Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from turtle_db.database.models import (
    Profession, ItemType, ItemSubtype, ItemSlot
)
from turtle_db.scrapers.models import ScrapedItem, ScrapedRecipe
from turtle_db.utils.exceptions import TurtleDBException

logger = logging.getLogger(__name__)


class DataMappingError(TurtleDBException):
    """Error mapping scraped data to database models."""
    def __init__(self, field: str, value: str):
        super().__init__("IMPORT_MAPPING_ERROR", f"Cannot map {field}: {value}")


class DataMapper:
    """Maps scraped data to database models."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def map_item(self, scraped_item: ScrapedItem) -> Dict[str, Any]:
        """Map scraped item to database item creation data."""
        logger.info(f"Mapping item: {scraped_item.name}")
        
        # Map item type
        item_type = await self._get_or_create_item_type(scraped_item.item_type)
        
        # Map subtype if present
        subtype = None
        if scraped_item.subtype:
            subtype = await self._get_or_create_item_subtype(
                scraped_item.subtype, item_type.id
            )
        
        # Map slot if present
        slot = None
        if scraped_item.slot:
            slot = await self._get_or_create_item_slot(scraped_item.slot)
        
        # Map quality
        quality = self._normalize_quality(scraped_item.quality)
        
        # Map bind type
        bind_type = self._normalize_bind_type(scraped_item.bind_type)
        
        return {
            'name': scraped_item.name,
            'description': scraped_item.description,
            'type_id': item_type.id,
            'subtype_id': subtype.id if subtype else None,
            'slot_id': slot.id if slot else None,
            'item_level': scraped_item.item_level,
            'required_level': scraped_item.required_level,
            'quality': quality,
            'bind_type': bind_type,
            'max_stack': scraped_item.max_stack,
            'vendor_price_copper': scraped_item.vendor_price_copper
        }
    
    async def map_recipe(self, scraped_recipe: ScrapedRecipe, item_id: int) -> Dict[str, Any]:
        """Map scraped recipe to database recipe creation data."""
        logger.info(f"Mapping recipe: {scraped_recipe.name}")
        
        # Get or create profession
        profession = await self._get_or_create_profession(scraped_recipe.profession)
        
        return {
            'name': scraped_recipe.name,
            'profession_id': profession.id,
            'creates_item_id': item_id,
            'required_skill_level': scraped_recipe.required_skill,
            'recipe_type': scraped_recipe.recipe_type
        }
    
    async def _get_or_create_item_type(self, type_name: str) -> ItemType:
        """Get existing item type or create new one."""
        normalized_name = type_name.lower().strip()
        
        # Try to find existing type
        result = await self.db.execute(
            select(ItemType).where(ItemType.name == normalized_name)
        )
        existing_type = result.scalar_one_or_none()
        
        if existing_type:
            logger.debug(f"Found existing item type: {normalized_name}")
            return existing_type
        
        # Create new type
        logger.info(f"Creating new item type: {normalized_name}")
        new_type = ItemType(
            name=normalized_name,
            description=f"Auto-created item type: {normalized_name}"
        )
        self.db.add(new_type)
        await self.db.flush()
        return new_type
    
    async def _get_or_create_item_subtype(self, subtype_name: str, type_id: int) -> ItemSubtype:
        """Get existing item subtype or create new one."""
        normalized_name = subtype_name.lower().strip()
        
        # Try to find existing subtype
        result = await self.db.execute(
            select(ItemSubtype).where(
                ItemSubtype.name == normalized_name,
                ItemSubtype.type_id == type_id
            )
        )
        existing_subtype = result.scalar_one_or_none()
        
        if existing_subtype:
            logger.debug(f"Found existing item subtype: {normalized_name}")
            return existing_subtype
        
        # Create new subtype
        logger.info(f"Creating new item subtype: {normalized_name}")
        new_subtype = ItemSubtype(
            name=normalized_name,
            type_id=type_id,
            description=f"Auto-created item subtype: {normalized_name}"
        )
        self.db.add(new_subtype)
        await self.db.flush()
        return new_subtype
    
    async def _get_or_create_item_slot(self, slot_name: str) -> ItemSlot:
        """Get existing item slot or create new one."""
        normalized_name = slot_name.lower().strip()
        
        # Try to find existing slot
        result = await self.db.execute(
            select(ItemSlot).where(ItemSlot.name == normalized_name)
        )
        existing_slot = result.scalar_one_or_none()
        
        if existing_slot:
            logger.debug(f"Found existing item slot: {normalized_name}")
            return existing_slot
        
        # Create new slot
        logger.info(f"Creating new item slot: {normalized_name}")
        new_slot = ItemSlot(
            name=normalized_name,
            description=f"Auto-created item slot: {normalized_name}"
        )
        self.db.add(new_slot)
        await self.db.flush()
        return new_slot
    
    async def _get_or_create_profession(self, profession_name: str) -> Profession:
        """Get existing profession or create new one."""
        normalized_name = profession_name.lower().strip()
        
        # Map common profession name variations
        profession_mappings = {
            'blacksmith': 'blacksmithing',
            'tailor': 'tailoring',
            'leatherwork': 'leatherworking',
            'engineer': 'engineering',
            'alchemist': 'alchemy',
            'enchanter': 'enchanting',
            'cook': 'cooking'
        }
        
        normalized_name = profession_mappings.get(normalized_name, normalized_name)
        
        # Try to find existing profession
        result = await self.db.execute(
            select(Profession).where(Profession.name == normalized_name)
        )
        existing_profession = result.scalar_one_or_none()
        
        if existing_profession:
            logger.debug(f"Found existing profession: {normalized_name}")
            return existing_profession
        
        # Create new profession
        logger.info(f"Creating new profession: {normalized_name}")
        new_profession = Profession(
            name=normalized_name,
            description=f"Auto-created profession: {normalized_name}",
            max_skill_level=375  # Default WoW skill cap
        )
        self.db.add(new_profession)
        await self.db.flush()
        return new_profession
    
    def _normalize_quality(self, quality: str) -> str:
        """Normalize quality strings to standard values."""
        if not quality:
            return 'common'
            
        quality_map = {
            'poor': 'poor',
            'common': 'common', 
            'uncommon': 'uncommon',
            'rare': 'rare',
            'epic': 'epic',
            'legendary': 'legendary',
            'artifact': 'artifact',
            # Handle alternative names
            'white': 'common',
            'gray': 'poor',
            'grey': 'poor',
            'green': 'uncommon',
            'blue': 'rare',
            'purple': 'epic',
            'orange': 'legendary'
        }
        
        normalized = quality.lower().strip()
        mapped_quality = quality_map.get(normalized, 'common')
        
        if mapped_quality == 'common' and normalized not in quality_map:
            logger.warning(f"Unknown quality '{quality}', defaulting to 'common'")
        
        return mapped_quality
    
    def _normalize_bind_type(self, bind_type: str) -> str:
        """Normalize bind type strings to standard values."""
        if not bind_type:
            return 'none'
            
        bind_map = {
            'none': 'none',
            'pickup': 'pickup',
            'equip': 'equip',
            'use': 'use',
            'account': 'account',
            # Handle alternative names
            'bop': 'pickup',  # Bind on Pickup
            'boe': 'equip',   # Bind on Equip
            'bou': 'use',     # Bind on Use
            'boa': 'account'  # Bind on Account
        }
        
        normalized = bind_type.lower().strip()
        mapped_bind = bind_map.get(normalized, 'none')
        
        if mapped_bind == 'none' and normalized not in bind_map:
            logger.warning(f"Unknown bind type '{bind_type}', defaulting to 'none'")
        
        return mapped_bind