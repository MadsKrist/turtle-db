"""
Seed data for the WoW Items API database.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from turtle_db.database.models import (
    ItemType, ItemSubtype, ItemSlot, Profession, 
    Item, Recipe, RecipeIngredient
)
from turtle_db.database.connection import AsyncSessionLocal

logger = logging.getLogger(__name__)


async def create_reference_data(db: AsyncSession):
    """Create reference data (types, subtypes, slots, professions)."""
    
    # Item Types
    item_types_data = [
        {"name": "armor", "description": "Protective equipment worn by characters"},
        {"name": "weapon", "description": "Combat equipment for dealing damage"},
        {"name": "consumable", "description": "Items that can be used and consumed"},
        {"name": "trade_goods", "description": "Materials used in professions and trading"},
    ]
    
    item_types = {}
    for type_data in item_types_data:
        # Check if exists
        result = await db.execute(select(ItemType).where(ItemType.name == type_data["name"]))
        existing = result.scalar_one_or_none()
        
        if not existing:
            item_type = ItemType(**type_data)
            db.add(item_type)
            await db.flush()
            item_types[type_data["name"]] = item_type
        else:
            item_types[type_data["name"]] = existing
    
    # Item Subtypes
    item_subtypes_data = [
        {"name": "plate", "description": "Heavy metal armor for warriors and paladins", "type": "armor"},
        {"name": "cloth", "description": "Light fabric armor for casters", "type": "armor"},
        {"name": "leather", "description": "Medium armor for rogues and hunters", "type": "armor"},
        {"name": "mail", "description": "Chain armor for hunters and shamans", "type": "armor"},
        {"name": "sword", "description": "Bladed melee weapons", "type": "weapon"},
        {"name": "staff", "description": "Two-handed casting weapons", "type": "weapon"},
        {"name": "mace", "description": "Blunt melee weapons", "type": "weapon"},
    ]
    
    item_subtypes = {}
    for subtype_data in item_subtypes_data:
        # Check if exists
        result = await db.execute(
            select(ItemSubtype).where(ItemSubtype.name == subtype_data["name"])
        )
        existing = result.scalar_one_or_none()
        
        if not existing:
            item_subtype = ItemSubtype(
                name=subtype_data["name"],
                description=subtype_data["description"],
                type_id=item_types[subtype_data["type"]].id
            )
            db.add(item_subtype)
            await db.flush()
            item_subtypes[subtype_data["name"]] = item_subtype
        else:
            item_subtypes[subtype_data["name"]] = existing
    
    # Item Slots
    item_slots_data = [
        {"name": "head", "description": "Helmet or hat slot"},
        {"name": "chest", "description": "Chest armor slot"},
        {"name": "feet", "description": "Boot or shoe slot"},
        {"name": "legs", "description": "Pants or leggings slot"},
        {"name": "main_hand", "description": "Primary weapon slot"},
        {"name": "off_hand", "description": "Secondary weapon or shield slot"},
        {"name": "hands", "description": "Gloves or gauntlets slot"},
        {"name": "waist", "description": "Belt slot"},
    ]
    
    item_slots = {}
    for slot_data in item_slots_data:
        # Check if exists
        result = await db.execute(select(ItemSlot).where(ItemSlot.name == slot_data["name"]))
        existing = result.scalar_one_or_none()
        
        if not existing:
            item_slot = ItemSlot(**slot_data)
            db.add(item_slot)
            await db.flush()
            item_slots[slot_data["name"]] = item_slot
        else:
            item_slots[slot_data["name"]] = existing
    
    # Professions
    professions_data = [
        {"name": "blacksmithing", "description": "Crafting metal weapons and armor", "max_skill_level": 375},
        {"name": "tailoring", "description": "Creating cloth armor and bags", "max_skill_level": 375},
        {"name": "alchemy", "description": "Brewing potions and elixirs", "max_skill_level": 375},
        {"name": "leatherworking", "description": "Crafting leather armor and accessories", "max_skill_level": 375},
    ]
    
    professions = {}
    for prof_data in professions_data:
        # Check if exists
        result = await db.execute(select(Profession).where(Profession.name == prof_data["name"]))
        existing = result.scalar_one_or_none()
        
        if not existing:
            profession = Profession(**prof_data)
            db.add(profession)
            await db.flush()
            professions[prof_data["name"]] = profession
        else:
            professions[prof_data["name"]] = existing
    
    await db.commit()
    return item_types, item_subtypes, item_slots, professions


async def create_sample_items(db: AsyncSession):
    """Create sample items based on the reference data."""
    
    # Get reference data
    item_types = {}
    result = await db.execute(select(ItemType))
    for item_type in result.scalars().all():
        item_types[item_type.name] = item_type
    
    item_subtypes = {}
    result = await db.execute(select(ItemSubtype))
    for subtype in result.scalars().all():
        item_subtypes[subtype.name] = subtype
    
    item_slots = {}
    result = await db.execute(select(ItemSlot))
    for slot in result.scalars().all():
        item_slots[slot.name] = slot
    
    # Sample items
    sample_items = [
        {
            "name": "Abyssal Inscribed Greaves",
            "description": "Heavy plate boots inscribed with abyssal runes",
            "type": "armor",
            "subtype": "plate",
            "slot": "feet",
            "item_level": 65,
            "required_level": 60,
            "quality": "rare",
            "bind_type": "pickup",
            "vendor_price_copper": 123456  # 12g 34s 56c
        },
        {
            "name": "Titanic Leggings",
            "description": "Massive plate pants forged with titanic strength",
            "type": "armor",
            "subtype": "plate",
            "slot": "legs",
            "item_level": 70,
            "required_level": 65,
            "quality": "epic",
            "bind_type": "pickup",
            "vendor_price_copper": 0  # Craftable only
        },
        {
            "name": "Arcanite Bar",
            "description": "A bar of refined arcanite, used in advanced smithing",
            "type": "trade_goods",
            "subtype": None,
            "slot": None,
            "item_level": None,
            "required_level": 1,
            "quality": "uncommon",
            "bind_type": "none",
            "max_stack": 20,
            "vendor_price_copper": 50000  # 5g
        },
        {
            "name": "Enchanted Thorium Bar",
            "description": "Thorium infused with magical energy",
            "type": "trade_goods",
            "subtype": None,
            "slot": None,
            "item_level": None,
            "required_level": 1,
            "quality": "uncommon",
            "bind_type": "none",
            "max_stack": 20,
            "vendor_price_copper": 30000  # 3g
        },
    ]
    
    items = {}
    for item_data in sample_items:
        # Check if exists
        result = await db.execute(select(Item).where(Item.name == item_data["name"]))
        existing = result.scalar_one_or_none()
        
        if not existing:
            item = Item(
                name=item_data["name"],
                description=item_data["description"],
                type_id=item_types[item_data["type"]].id,
                subtype_id=item_subtypes[item_data["subtype"]].id if item_data["subtype"] else None,
                slot_id=item_slots[item_data["slot"]].id if item_data["slot"] else None,
                item_level=item_data["item_level"],
                required_level=item_data["required_level"],
                quality=item_data["quality"],
                bind_type=item_data["bind_type"],
                max_stack=item_data.get("max_stack", 1),
                vendor_price_copper=item_data["vendor_price_copper"]
            )
            db.add(item)
            await db.flush()
            items[item_data["name"]] = item
        else:
            items[item_data["name"]] = existing
    
    await db.commit()
    return items


async def create_sample_recipes(db: AsyncSession):
    """Create sample recipes."""
    
    # Get reference data
    professions = {}
    result = await db.execute(select(Profession))
    for profession in result.scalars().all():
        professions[profession.name] = profession
    
    items = {}
    result = await db.execute(select(Item))
    for item in result.scalars().all():
        items[item.name] = item
    
    # Sample recipe: Titanic Leggings
    recipe_data = {
        "name": "Titanic Leggings",
        "profession": "blacksmithing",
        "creates_item": "Titanic Leggings",
        "required_skill_level": 300,
        "ingredients": [
            {"item": "Arcanite Bar", "quantity": 12},
            {"item": "Enchanted Thorium Bar", "quantity": 20},
        ]
    }
    
    # Check if recipe exists
    result = await db.execute(select(Recipe).where(Recipe.name == recipe_data["name"]))
    existing_recipe = result.scalar_one_or_none()
    
    if not existing_recipe:
        recipe = Recipe(
            name=recipe_data["name"],
            profession_id=professions[recipe_data["profession"]].id,
            creates_item_id=items[recipe_data["creates_item"]].id,
            required_skill_level=recipe_data["required_skill_level"]
        )
        db.add(recipe)
        await db.flush()
        
        # Add ingredients
        for ingredient_data in recipe_data["ingredients"]:
            ingredient = RecipeIngredient(
                recipe_id=recipe.id,
                ingredient_item_id=items[ingredient_data["item"]].id,
                quantity=ingredient_data["quantity"]
            )
            db.add(ingredient)
    
    await db.commit()


async def seed_database():
    """Seed the database with initial data."""
    async with AsyncSessionLocal() as db:
        try:
            logger.info("Seeding reference data...")
            await create_reference_data(db)
            
            logger.info("Creating sample items...")
            await create_sample_items(db)
            
            logger.info("Creating sample recipes...")
            await create_sample_recipes(db)
            
            logger.info("Database seeding completed successfully")
            
        except Exception as e:
            logger.error(f"Error seeding database: {str(e)}")
            await db.rollback()
            raise


if __name__ == "__main__":
    import asyncio
    asyncio.run(seed_database())