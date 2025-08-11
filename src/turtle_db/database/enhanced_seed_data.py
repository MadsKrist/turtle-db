"""
Enhanced seed data for the comprehensive WoW Items API database.
Populates all item types, subtypes, slots, and professions from the planning document.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from turtle_db.database.enhanced_models import (
    ItemType, ItemSubtype, ItemSlot, Profession, 
    Item, Recipe, RecipeIngredient
)
from turtle_db.database.connection import AsyncSessionLocal

logger = logging.getLogger(__name__)


async def create_comprehensive_reference_data(db: AsyncSession):
    """Create comprehensive reference data based on WoW classification system."""
    
    # Item Types (12 major categories)
    item_types_data = [
        {"name": "weapon", "description": "Combat equipment for dealing damage", "sort_order": 1},
        {"name": "armor", "description": "Protective equipment worn by characters", "sort_order": 2},
        {"name": "container", "description": "Bags and storage items", "sort_order": 3},
        {"name": "consumable", "description": "Items that can be used and consumed", "sort_order": 4},
        {"name": "trade_goods", "description": "Materials used in professions and trading", "sort_order": 5},
        {"name": "projectile", "description": "Ammunition for ranged weapons", "sort_order": 6},
        {"name": "quiver", "description": "Containers for ammunition", "sort_order": 7},
        {"name": "recipe", "description": "Plans and patterns for crafting", "sort_order": 8},
        {"name": "miscellaneous", "description": "Various utility and special items", "sort_order": 9},
        {"name": "currency", "description": "Alternative currency items", "sort_order": 10},
        {"name": "quest", "description": "Quest-related items", "sort_order": 11},
        {"name": "key", "description": "Keys and lockpicks", "sort_order": 12}
    ]
    
    item_types = {}
    for type_data in item_types_data:
        result = await db.execute(select(ItemType).where(ItemType.name == type_data["name"]))
        existing = result.scalar_one_or_none()
        
        if not existing:
            item_type = ItemType(**type_data)
            db.add(item_type)
            await db.flush()
            item_types[type_data["name"]] = item_type
        else:
            item_types[type_data["name"]] = existing
    
    # Weapon Subtypes
    weapon_subtypes = [
        # One-Handed Weapons
        {"name": "dagger", "description": "Fast, lightweight stabbing weapons", "sort_order": 1},
        {"name": "fist_weapon", "description": "Martial arts weapons worn on hands", "sort_order": 2},
        {"name": "one_handed_axe", "description": "Single-handed chopping weapons", "sort_order": 3},
        {"name": "one_handed_mace", "description": "Single-handed blunt weapons", "sort_order": 4},
        {"name": "one_handed_sword", "description": "Single-handed slashing weapons", "sort_order": 5},
        
        # Two-Handed Weapons
        {"name": "polearm", "description": "Long-reach two-handed weapons", "sort_order": 6},
        {"name": "staff", "description": "Two-handed magical focusing weapons", "sort_order": 7},
        {"name": "two_handed_axe", "description": "Large two-handed chopping weapons", "sort_order": 8},
        {"name": "two_handed_mace", "description": "Large two-handed blunt weapons", "sort_order": 9},
        {"name": "two_handed_sword", "description": "Large two-handed slashing weapons", "sort_order": 10},
        
        # Ranged Weapons
        {"name": "bow", "description": "Ranged weapons using arrows", "sort_order": 11},
        {"name": "crossbow", "description": "Mechanical ranged weapons using bolts", "sort_order": 12},
        {"name": "gun", "description": "Gunpowder ranged weapons using bullets", "sort_order": 13},
        {"name": "wand", "description": "Magical ranged weapons", "sort_order": 14},
        {"name": "thrown", "description": "Thrown ranged weapons", "sort_order": 15},
        
        # Other Weapons
        {"name": "fishing_pole", "description": "Tools for fishing profession", "sort_order": 16},
        {"name": "miscellaneous_weapon", "description": "Various other weapon types", "sort_order": 17}
    ]
    
    # Armor Subtypes
    armor_subtypes = [
        {"name": "cloth", "description": "Light fabric armor for casters", "sort_order": 1},
        {"name": "leather", "description": "Medium armor for rogues and hunters", "sort_order": 2},
        {"name": "mail", "description": "Chain armor for hunters and shamans", "sort_order": 3},
        {"name": "plate", "description": "Heavy metal armor for warriors and paladins", "sort_order": 4},
        {"name": "shield", "description": "Defensive equipment for off-hand", "sort_order": 5},
        {"name": "libram", "description": "Paladin-specific relics", "sort_order": 6},
        {"name": "idol", "description": "Druid-specific relics", "sort_order": 7},
        {"name": "totem", "description": "Shaman-specific relics", "sort_order": 8},
        {"name": "sigil", "description": "Death Knight-specific relics", "sort_order": 9},
        {"name": "miscellaneous_armor", "description": "Various other armor types", "sort_order": 10}
    ]
    
    # Container Subtypes
    container_subtypes = [
        {"name": "bag", "description": "General storage containers", "sort_order": 1},
        {"name": "soul_bag", "description": "Containers for soul shards", "sort_order": 2},
        {"name": "herb_bag", "description": "Containers for herbalism materials", "sort_order": 3},
        {"name": "enchanting_bag", "description": "Containers for enchanting materials", "sort_order": 4},
        {"name": "engineering_bag", "description": "Containers for engineering materials", "sort_order": 5},
        {"name": "gem_bag", "description": "Containers for gems and jewelcrafting", "sort_order": 6},
        {"name": "mining_bag", "description": "Containers for mining materials", "sort_order": 7},
        {"name": "leatherworking_bag", "description": "Containers for leatherworking materials", "sort_order": 8},
        {"name": "inscription_bag", "description": "Containers for inscription materials", "sort_order": 9},
        {"name": "tackle_box", "description": "Containers for fishing supplies", "sort_order": 10}
    ]
    
    # Consumable Subtypes
    consumable_subtypes = [
        # Food & Drink
        {"name": "food", "description": "Consumable items that restore health", "sort_order": 1},
        {"name": "drink", "description": "Consumable items that restore mana", "sort_order": 2},
        {"name": "consumable_enhancement", "description": "Temporary enhancement consumables", "sort_order": 3},
        {"name": "alcohol", "description": "Alcoholic beverages", "sort_order": 4},
        
        # Potions & Elixirs
        {"name": "potion", "description": "Alchemical consumables with instant effects", "sort_order": 5},
        {"name": "elixir", "description": "Alchemical consumables with lasting effects", "sort_order": 6},
        {"name": "flask", "description": "Powerful alchemical consumables", "sort_order": 7},
        {"name": "bandage", "description": "First aid healing items", "sort_order": 8},
        {"name": "item_enhancement_temporary", "description": "Temporary item enhancements", "sort_order": 9},
        {"name": "scroll", "description": "Magical scrolls with spell effects", "sort_order": 10},
        {"name": "other_consumable", "description": "Various other consumable types", "sort_order": 11},
        
        # Combat Items
        {"name": "explosives_devices", "description": "Explosives and mechanical devices", "sort_order": 12}
    ]
    
    # Trade Goods Subtypes
    trade_goods_subtypes = [
        # Crafting Materials
        {"name": "elemental", "description": "Elemental essences and materials", "sort_order": 1},
        {"name": "cloth_material", "description": "Fabric materials for tailoring", "sort_order": 2},
        {"name": "leather_material", "description": "Hide and leather materials", "sort_order": 3},
        {"name": "metal_stone", "description": "Metals and stone materials", "sort_order": 4},
        {"name": "cooking_material", "description": "Ingredients for cooking", "sort_order": 5},
        {"name": "herb", "description": "Plants and herbs for alchemy", "sort_order": 6},
        {"name": "enchanting_material", "description": "Magical essences for enchanting", "sort_order": 7},
        {"name": "jewelcrafting_material", "description": "Gems and precious materials", "sort_order": 8},
        {"name": "parts", "description": "Mechanical parts for engineering", "sort_order": 9},
        {"name": "devices", "description": "Crafted mechanical devices", "sort_order": 10},
        {"name": "explosives", "description": "Explosive materials and items", "sort_order": 11},
        {"name": "inscription_material", "description": "Materials for inscription", "sort_order": 12},
        {"name": "other_trade_goods", "description": "Various other crafting materials", "sort_order": 13},
        
        # Armor & Weapon Enhancement
        {"name": "armor_enhancement", "description": "Permanent armor enhancements", "sort_order": 14},
        {"name": "weapon_enhancement", "description": "Permanent weapon enhancements", "sort_order": 15}
    ]
    
    # Other subtypes for remaining categories
    other_subtypes = [
        # Projectiles
        {"name": "arrow", "description": "Ammunition for bows", "sort_order": 1, "type": "projectile"},
        {"name": "bullet", "description": "Ammunition for guns", "sort_order": 2, "type": "projectile"},
        
        # Quivers
        {"name": "quiver", "description": "Containers for arrows", "sort_order": 1, "type": "quiver"},
        {"name": "ammo_pouch", "description": "Containers for bullets", "sort_order": 2, "type": "quiver"},
        
        # Recipe Types
        {"name": "leatherworking_pattern", "description": "Patterns for leatherworking", "sort_order": 1, "type": "recipe"},
        {"name": "tailoring_pattern", "description": "Patterns for tailoring", "sort_order": 2, "type": "recipe"},
        {"name": "engineering_schematic", "description": "Schematics for engineering", "sort_order": 3, "type": "recipe"},
        {"name": "blacksmithing_plan", "description": "Plans for blacksmithing", "sort_order": 4, "type": "recipe"},
        {"name": "cooking_recipe", "description": "Recipes for cooking", "sort_order": 5, "type": "recipe"},
        {"name": "alchemy_formula", "description": "Formulas for alchemy", "sort_order": 6, "type": "recipe"},
        {"name": "first_aid_manual", "description": "Manuals for first aid", "sort_order": 7, "type": "recipe"},
        {"name": "enchanting_formula", "description": "Formulas for enchanting", "sort_order": 8, "type": "recipe"},
        {"name": "fishing_book", "description": "Books for fishing", "sort_order": 9, "type": "recipe"},
        {"name": "jewelcrafting_design", "description": "Designs for jewelcrafting", "sort_order": 10, "type": "recipe"},
        {"name": "inscription_technique", "description": "Techniques for inscription", "sort_order": 11, "type": "recipe"},
        {"name": "runeforging_pattern", "description": "Patterns for runeforging", "sort_order": 12, "type": "recipe"},
        
        # Miscellaneous
        {"name": "junk", "description": "Vendor trash items", "sort_order": 1, "type": "miscellaneous"},
        {"name": "reagent", "description": "Spell components and reagents", "sort_order": 2, "type": "miscellaneous"},
        {"name": "pet", "description": "Companion pets and mounts", "sort_order": 3, "type": "miscellaneous"},
        {"name": "holiday", "description": "Holiday and seasonal items", "sort_order": 4, "type": "miscellaneous"},
        {"name": "other_misc", "description": "Various miscellaneous items", "sort_order": 5, "type": "miscellaneous"},
        {"name": "mount", "description": "Rideable mounts and vehicles", "sort_order": 6, "type": "miscellaneous"}
    ]
    
    # Create all subtypes
    all_subtypes = [
        *[{**st, "type": "weapon"} for st in weapon_subtypes],
        *[{**st, "type": "armor"} for st in armor_subtypes],
        *[{**st, "type": "container"} for st in container_subtypes],
        *[{**st, "type": "consumable"} for st in consumable_subtypes],
        *[{**st, "type": "trade_goods"} for st in trade_goods_subtypes],
        *other_subtypes
    ]
    
    item_subtypes = {}
    for subtype_data in all_subtypes:
        result = await db.execute(
            select(ItemSubtype).where(ItemSubtype.name == subtype_data["name"])
        )
        existing = result.scalar_one_or_none()
        
        if not existing:
            item_subtype = ItemSubtype(
                name=subtype_data["name"],
                description=subtype_data["description"],
                type_id=item_types[subtype_data["type"]].id,
                sort_order=subtype_data["sort_order"]
            )
            db.add(item_subtype)
            await db.flush()
            item_subtypes[subtype_data["name"]] = item_subtype
        else:
            item_subtypes[subtype_data["name"]] = existing
    
    # Equipment Slots (comprehensive slot system)
    item_slots_data = [
        # Worn Equipment Slots
        {"name": "head", "description": "Helmet, hat, or headpiece slot", "slot_type": "equipment", "sort_order": 1},
        {"name": "neck", "description": "Necklace or amulet slot", "slot_type": "equipment", "sort_order": 2},
        {"name": "shoulder", "description": "Shoulder pads or pauldrons slot", "slot_type": "equipment", "sort_order": 3},
        {"name": "back", "description": "Cloak or cape slot", "slot_type": "equipment", "sort_order": 4},
        {"name": "chest", "description": "Chest armor or robe slot", "slot_type": "equipment", "sort_order": 5},
        {"name": "shirt", "description": "Cosmetic shirt slot", "slot_type": "equipment", "sort_order": 6},
        {"name": "tabard", "description": "Guild or faction tabard slot", "slot_type": "equipment", "sort_order": 7},
        {"name": "wrist", "description": "Bracers or wristguards slot", "slot_type": "equipment", "sort_order": 8},
        {"name": "hands", "description": "Gloves or gauntlets slot", "slot_type": "equipment", "sort_order": 9},
        {"name": "waist", "description": "Belt or girdle slot", "slot_type": "equipment", "sort_order": 10},
        {"name": "legs", "description": "Pants or leggings slot", "slot_type": "equipment", "sort_order": 11},
        {"name": "feet", "description": "Boots or shoes slot", "slot_type": "equipment", "sort_order": 12},
        {"name": "finger", "description": "Ring slot (two available)", "slot_type": "equipment", "sort_order": 13},
        {"name": "trinket", "description": "Trinket slot (two available)", "slot_type": "equipment", "sort_order": 14},
        {"name": "held_in_off_hand", "description": "Off-hand held items slot", "slot_type": "equipment", "sort_order": 15},
        
        # Weapon Slots
        {"name": "main_hand", "description": "Primary weapon slot", "slot_type": "equipment", "sort_order": 16},
        {"name": "off_hand", "description": "Secondary weapon or shield slot", "slot_type": "equipment", "sort_order": 17},
        {"name": "two_hand", "description": "Two-handed weapon slot", "slot_type": "equipment", "sort_order": 18},
        {"name": "ranged", "description": "Ranged weapon slot", "slot_type": "equipment", "sort_order": 19},
        {"name": "ammo", "description": "Ammunition slot", "slot_type": "equipment", "sort_order": 20},
        {"name": "relic", "description": "Class-specific relic slot", "slot_type": "equipment", "sort_order": 21},
        
        # Bag Slots
        {"name": "bag_1", "description": "Primary bag slot", "slot_type": "bag", "sort_order": 22},
        {"name": "bag_2", "description": "Secondary bag slot", "slot_type": "bag", "sort_order": 23},
        {"name": "bag_3", "description": "Third bag slot", "slot_type": "bag", "sort_order": 24},
        {"name": "bag_4", "description": "Fourth bag slot", "slot_type": "bag", "sort_order": 25},
        
        # Non-Equipment
        {"name": "consumable", "description": "Consumable items (not equipped)", "slot_type": "consumable", "sort_order": 26},
        {"name": "non_equippable", "description": "Items that cannot be equipped", "slot_type": "none", "sort_order": 27}
    ]
    
    item_slots = {}
    for slot_data in item_slots_data:
        result = await db.execute(select(ItemSlot).where(ItemSlot.name == slot_data["name"]))
        existing = result.scalar_one_or_none()
        
        if not existing:
            item_slot = ItemSlot(**slot_data)
            db.add(item_slot)
            await db.flush()
            item_slots[slot_data["name"]] = item_slot
        else:
            item_slots[slot_data["name"]] = existing
    
    # Professions (all WoW professions)
    professions_data = [
        # Primary Professions
        {"name": "alchemy", "description": "Brewing potions, elixirs, and flasks", "profession_type": "primary", "max_skill_level": 375},
        {"name": "blacksmithing", "description": "Crafting metal weapons and armor", "profession_type": "primary", "max_skill_level": 375},
        {"name": "enchanting", "description": "Enhancing equipment with magical properties", "profession_type": "primary", "max_skill_level": 375},
        {"name": "engineering", "description": "Creating mechanical devices and gadgets", "profession_type": "primary", "max_skill_level": 375},
        {"name": "herbalism", "description": "Gathering herbs and plants", "profession_type": "primary", "max_skill_level": 375},
        {"name": "inscription", "description": "Creating glyphs, scrolls, and books", "profession_type": "primary", "max_skill_level": 375},
        {"name": "jewelcrafting", "description": "Crafting gems and jewelry", "profession_type": "primary", "max_skill_level": 375},
        {"name": "leatherworking", "description": "Creating leather and mail armor", "profession_type": "primary", "max_skill_level": 375},
        {"name": "mining", "description": "Gathering metals and stone", "profession_type": "primary", "max_skill_level": 375},
        {"name": "skinning", "description": "Gathering leather and hides", "profession_type": "primary", "max_skill_level": 375},
        {"name": "tailoring", "description": "Creating cloth armor and bags", "profession_type": "primary", "max_skill_level": 375},
        
        # Secondary Professions
        {"name": "archaeology", "description": "Discovering ancient artifacts", "profession_type": "secondary", "max_skill_level": 525},
        {"name": "cooking", "description": "Preparing food and beverages", "profession_type": "secondary", "max_skill_level": 375},
        {"name": "first_aid", "description": "Creating healing bandages", "profession_type": "secondary", "max_skill_level": 375},
        {"name": "fishing", "description": "Catching fish and aquatic creatures", "profession_type": "secondary", "max_skill_level": 375},
        
        # Special Professions
        {"name": "runeforging", "description": "Death Knight weapon enhancement", "profession_type": "special", "max_skill_level": 100},
        {"name": "poisons", "description": "Rogue poison creation", "profession_type": "special", "max_skill_level": 300}
    ]
    
    professions = {}
    for prof_data in professions_data:
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


async def seed_enhanced_database():
    """Seed the database with comprehensive WoW reference data."""
    async with AsyncSessionLocal() as db:
        try:
            logger.info("Seeding comprehensive reference data...")
            await create_comprehensive_reference_data(db)
            
            logger.info("Enhanced database seeding completed successfully")
            
        except Exception as e:
            logger.error(f"Error seeding enhanced database: {str(e)}")
            await db.rollback()
            raise


if __name__ == "__main__":
    import asyncio
    asyncio.run(seed_enhanced_database())