-- Enhanced World of Warcraft Items Database Schema
-- Based on comprehensive WoW item classification system
-- SQLite Database Design with full item category support

-- Core reference tables for item classification hierarchy

-- Top-level item types (15 major categories from WoW)
CREATE TABLE item_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    sort_order INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Item subtypes (granular classification within each type)
CREATE TABLE item_subtypes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type_id INTEGER NOT NULL,
    name VARCHAR(50) NOT NULL,
    description TEXT,
    sort_order INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (type_id) REFERENCES item_types(id),
    UNIQUE(type_id, name)
);

-- Equipment slots for wearable/usable items
CREATE TABLE item_slots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(30) NOT NULL UNIQUE,
    description TEXT,
    slot_type VARCHAR(20), -- equipment, bag, ammo, etc.
    sort_order INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Professions for crafting system
CREATE TABLE professions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    profession_type VARCHAR(20) DEFAULT 'primary', -- primary, secondary
    max_skill_level INTEGER DEFAULT 375,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Main items table with comprehensive attributes
CREATE TABLE items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    
    -- Classification
    type_id INTEGER NOT NULL,
    subtype_id INTEGER,
    slot_id INTEGER,
    
    -- Level and requirements
    item_level INTEGER,
    required_level INTEGER DEFAULT 1,
    required_class VARCHAR(100), -- comma-separated class names
    required_race VARCHAR(100),  -- comma-separated race names
    
    -- Quality and rarity
    quality VARCHAR(20) DEFAULT 'common', -- poor, common, uncommon, rare, epic, legendary, artifact, heirloom
    
    -- Item behavior
    bind_type VARCHAR(20) DEFAULT 'none', -- none, pickup, equip, use, quest, account
    unique_equipped BOOLEAN DEFAULT FALSE,
    max_stack INTEGER DEFAULT 1,
    
    -- Pricing
    vendor_price_copper INTEGER DEFAULT 0,
    
    -- Item stats (stored as JSON for flexibility)
    stats TEXT, -- JSON object with stat bonuses
    
    -- Special properties
    durability INTEGER,
    charges INTEGER,
    cooldown_seconds INTEGER,
    
    -- External references
    external_id INTEGER, -- ID from source database (e.g., Turtle-WoW)
    external_source VARCHAR(50), -- source identifier
    
    -- Metadata
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (type_id) REFERENCES item_types(id),
    FOREIGN KEY (subtype_id) REFERENCES item_subtypes(id),
    FOREIGN KEY (slot_id) REFERENCES item_slots(id)
);

-- Vendors and their locations
CREATE TABLE vendors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(100),
    zone VARCHAR(50),
    subzone VARCHAR(50),
    faction VARCHAR(20), -- alliance, horde, neutral
    vendor_type VARCHAR(30), -- npc, guild, pvp, etc.
    coordinates VARCHAR(20), -- x,y coordinates
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Items sold by vendors with pricing and requirements
CREATE TABLE vendor_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vendor_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    price_copper INTEGER NOT NULL,
    stock_quantity INTEGER DEFAULT -1, -- -1 for unlimited
    required_reputation VARCHAR(50), -- neutral, friendly, honored, revered, exalted
    required_faction VARCHAR(20), -- alliance, horde
    required_level INTEGER,
    available_start_date DATE,
    available_end_date DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vendor_id) REFERENCES vendors(id),
    FOREIGN KEY (item_id) REFERENCES items(id),
    UNIQUE(vendor_id, item_id)
);

-- Crafting recipes with detailed requirements
CREATE TABLE recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    profession_id INTEGER NOT NULL,
    creates_item_id INTEGER NOT NULL,
    creates_quantity INTEGER DEFAULT 1,
    required_skill_level INTEGER DEFAULT 1,
    recipe_type VARCHAR(20) DEFAULT 'learned', -- learned, taught, discovered, quest
    recipe_difficulty VARCHAR(20) DEFAULT 'yellow', -- trivial, green, yellow, orange, red
    
    -- Learning requirements
    teaches_spell_id INTEGER, -- for spells that teach the recipe
    required_reputation VARCHAR(50),
    required_faction VARCHAR(20),
    required_level INTEGER,
    
    -- External references
    external_id INTEGER, -- ID from source database
    external_source VARCHAR(50),
    
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (profession_id) REFERENCES professions(id),
    FOREIGN KEY (creates_item_id) REFERENCES items(id)
);

-- Recipe ingredients with quantities and alternatives
CREATE TABLE recipe_ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id INTEGER NOT NULL,
    ingredient_item_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    is_optional BOOLEAN DEFAULT FALSE, -- for optional reagents
    ingredient_group INTEGER DEFAULT 1, -- for alternative ingredients
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id),
    FOREIGN KEY (ingredient_item_id) REFERENCES items(id),
    UNIQUE(recipe_id, ingredient_item_id)
);

-- Item sets (for equipment sets like Tier gear)
CREATE TABLE item_sets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    set_type VARCHAR(30), -- tier, dungeon, pvp, crafted, etc.
    tier_level VARCHAR(10), -- T1, T2, T3, etc.
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Items that belong to sets
CREATE TABLE item_set_pieces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    set_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    piece_name VARCHAR(50), -- descriptive name like "Helmet", "Chestpiece"
    sort_order INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (set_id) REFERENCES item_sets(id),
    FOREIGN KEY (item_id) REFERENCES items(id),
    UNIQUE(set_id, item_id)
);

-- Set bonuses for wearing multiple pieces
CREATE TABLE item_set_bonuses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    set_id INTEGER NOT NULL,
    pieces_required INTEGER NOT NULL,
    bonus_description TEXT NOT NULL,
    bonus_stats TEXT, -- JSON object with bonus stats
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (set_id) REFERENCES item_sets(id),
    UNIQUE(set_id, pieces_required)
);

-- Performance indexes
CREATE INDEX idx_items_type_subtype ON items(type_id, subtype_id);
CREATE INDEX idx_items_slot ON items(slot_id);
CREATE INDEX idx_items_quality ON items(quality);
CREATE INDEX idx_items_level ON items(item_level, required_level);
CREATE INDEX idx_items_bind_type ON items(bind_type);
CREATE INDEX idx_items_external ON items(external_source, external_id);
CREATE INDEX idx_items_name ON items(name);

CREATE INDEX idx_vendor_items_vendor ON vendor_items(vendor_id);
CREATE INDEX idx_vendor_items_item ON vendor_items(item_id);
CREATE INDEX idx_vendor_items_faction ON vendor_items(required_faction);

CREATE INDEX idx_recipes_profession ON recipes(profession_id);
CREATE INDEX idx_recipes_creates ON recipes(creates_item_id);
CREATE INDEX idx_recipes_skill ON recipes(required_skill_level);
CREATE INDEX idx_recipes_external ON recipes(external_source, external_id);

CREATE INDEX idx_recipe_ingredients_recipe ON recipe_ingredients(recipe_id);
CREATE INDEX idx_recipe_ingredients_item ON recipe_ingredients(ingredient_item_id);

CREATE INDEX idx_item_set_pieces_set ON item_set_pieces(set_id);
CREATE INDEX idx_item_set_pieces_item ON item_set_pieces(item_id);

-- Comprehensive data population based on WoW classification system

-- Item Types (15 major categories)
INSERT INTO item_types (name, description, sort_order) VALUES 
    ('weapon', 'Combat equipment for dealing damage', 1),
    ('armor', 'Protective equipment worn by characters', 2),
    ('container', 'Bags and storage items', 3),
    ('consumable', 'Items that can be used and consumed', 4),
    ('trade_goods', 'Materials used in professions and trading', 5),
    ('projectile', 'Ammunition for ranged weapons', 6),
    ('quiver', 'Containers for ammunition', 7),
    ('recipe', 'Plans and patterns for crafting', 8),
    ('miscellaneous', 'Various utility and special items', 9),
    ('currency', 'Alternative currency items', 10),
    ('quest', 'Quest-related items', 11),
    ('key', 'Keys and lockpicks', 12);

-- Weapon Subtypes
INSERT INTO item_subtypes (type_id, name, description, sort_order) VALUES 
    -- One-Handed Weapons
    (1, 'dagger', 'Fast, lightweight stabbing weapons', 1),
    (1, 'fist_weapon', 'Martial arts weapons worn on hands', 2),
    (1, 'one_handed_axe', 'Single-handed chopping weapons', 3),
    (1, 'one_handed_mace', 'Single-handed blunt weapons', 4),
    (1, 'one_handed_sword', 'Single-handed slashing weapons', 5),
    
    -- Two-Handed Weapons
    (1, 'polearm', 'Long-reach two-handed weapons', 6),
    (1, 'staff', 'Two-handed magical focusing weapons', 7),
    (1, 'two_handed_axe', 'Large two-handed chopping weapons', 8),
    (1, 'two_handed_mace', 'Large two-handed blunt weapons', 9),
    (1, 'two_handed_sword', 'Large two-handed slashing weapons', 10),
    
    -- Ranged Weapons
    (1, 'bow', 'Ranged weapons using arrows', 11),
    (1, 'crossbow', 'Mechanical ranged weapons using bolts', 12),
    (1, 'gun', 'Gunpowder ranged weapons using bullets', 13),
    (1, 'wand', 'Magical ranged weapons', 14),
    (1, 'thrown', 'Thrown ranged weapons', 15),
    
    -- Other Weapons
    (1, 'fishing_pole', 'Tools for fishing profession', 16),
    (1, 'miscellaneous_weapon', 'Various other weapon types', 17);

-- Armor Subtypes (by material and type)
INSERT INTO item_subtypes (type_id, name, description, sort_order) VALUES 
    -- By Material Type
    (2, 'cloth', 'Light fabric armor for casters', 1),
    (2, 'leather', 'Medium armor for rogues and hunters', 2),
    (2, 'mail', 'Chain armor for hunters and shamans', 3),
    (2, 'plate', 'Heavy metal armor for warriors and paladins', 4),
    (2, 'shield', 'Defensive equipment for off-hand', 5),
    (2, 'libram', 'Paladin-specific relics', 6),
    (2, 'idol', 'Druid-specific relics', 7),
    (2, 'totem', 'Shaman-specific relics', 8),
    (2, 'sigil', 'Death Knight-specific relics', 9),
    (2, 'miscellaneous_armor', 'Various other armor types', 10);

-- Container Subtypes
INSERT INTO item_subtypes (type_id, name, description, sort_order) VALUES 
    (3, 'bag', 'General storage containers', 1),
    (3, 'soul_bag', 'Containers for soul shards', 2),
    (3, 'herb_bag', 'Containers for herbalism materials', 3),
    (3, 'enchanting_bag', 'Containers for enchanting materials', 4),
    (3, 'engineering_bag', 'Containers for engineering materials', 5),
    (3, 'gem_bag', 'Containers for gems and jewelcrafting', 6),
    (3, 'mining_bag', 'Containers for mining materials', 7),
    (3, 'leatherworking_bag', 'Containers for leatherworking materials', 8),
    (3, 'inscription_bag', 'Containers for inscription materials', 9),
    (3, 'tackle_box', 'Containers for fishing supplies', 10);

-- Consumable Subtypes
INSERT INTO item_subtypes (type_id, name, description, sort_order) VALUES 
    -- Food & Drink
    (4, 'food', 'Consumable items that restore health', 1),
    (4, 'drink', 'Consumable items that restore mana', 2),
    (4, 'consumable_enhancement', 'Temporary enhancement consumables', 3),
    (4, 'alcohol', 'Alcoholic beverages', 4),
    
    -- Potions & Elixirs
    (4, 'potion', 'Alchemical consumables with instant effects', 5),
    (4, 'elixir', 'Alchemical consumables with lasting effects', 6),
    (4, 'flask', 'Powerful alchemical consumables', 7),
    (4, 'bandage', 'First aid healing items', 8),
    (4, 'item_enhancement_temporary', 'Temporary item enhancements', 9),
    (4, 'scroll', 'Magical scrolls with spell effects', 10),
    (4, 'other_consumable', 'Various other consumable types', 11),
    
    -- Combat Items
    (4, 'explosives_devices', 'Explosives and mechanical devices', 12);

-- Trade Goods Subtypes
INSERT INTO item_subtypes (type_id, name, description, sort_order) VALUES 
    -- Crafting Materials
    (5, 'elemental', 'Elemental essences and materials', 1),
    (5, 'cloth_material', 'Fabric materials for tailoring', 2),
    (5, 'leather_material', 'Hide and leather materials', 3),
    (5, 'metal_stone', 'Metals and stone materials', 4),
    (5, 'cooking_material', 'Ingredients for cooking', 5),
    (5, 'herb', 'Plants and herbs for alchemy', 6),
    (5, 'enchanting_material', 'Magical essences for enchanting', 7),
    (5, 'jewelcrafting_material', 'Gems and precious materials', 8),
    (5, 'parts', 'Mechanical parts for engineering', 9),
    (5, 'devices', 'Crafted mechanical devices', 10),
    (5, 'explosives', 'Explosive materials and items', 11),
    (5, 'inscription_material', 'Materials for inscription', 12),
    (5, 'other_trade_goods', 'Various other crafting materials', 13),
    
    -- Armor & Weapon Enhancement
    (5, 'armor_enhancement', 'Permanent armor enhancements', 14),
    (5, 'weapon_enhancement', 'Permanent weapon enhancements', 15);

-- Other Item Type Subtypes
INSERT INTO item_subtypes (type_id, name, description, sort_order) VALUES 
    -- Projectiles
    (6, 'arrow', 'Ammunition for bows', 1),
    (6, 'bullet', 'Ammunition for guns', 2),
    
    -- Quivers
    (7, 'quiver', 'Containers for arrows', 1),
    (7, 'ammo_pouch', 'Containers for bullets', 2),
    
    -- Recipe Types
    (8, 'leatherworking_pattern', 'Patterns for leatherworking', 1),
    (8, 'tailoring_pattern', 'Patterns for tailoring', 2),
    (8, 'engineering_schematic', 'Schematics for engineering', 3),
    (8, 'blacksmithing_plan', 'Plans for blacksmithing', 4),
    (8, 'cooking_recipe', 'Recipes for cooking', 5),
    (8, 'alchemy_formula', 'Formulas for alchemy', 6),
    (8, 'first_aid_manual', 'Manuals for first aid', 7),
    (8, 'enchanting_formula', 'Formulas for enchanting', 8),
    (8, 'fishing_book', 'Books for fishing', 9),
    (8, 'jewelcrafting_design', 'Designs for jewelcrafting', 10),
    (8, 'inscription_technique', 'Techniques for inscription', 11),
    (8, 'runeforging_pattern', 'Patterns for runeforging', 12),
    
    -- Miscellaneous
    (9, 'junk', 'Vendor trash items', 1),
    (9, 'reagent', 'Spell components and reagents', 2),
    (9, 'pet', 'Companion pets and mounts', 3),
    (9, 'holiday', 'Holiday and seasonal items', 4),
    (9, 'other_misc', 'Various miscellaneous items', 5),
    (9, 'mount', 'Rideable mounts and vehicles', 6);

-- Equipment Slots (comprehensive slot system)
INSERT INTO item_slots (name, description, slot_type, sort_order) VALUES 
    -- Worn Equipment Slots
    ('head', 'Helmet, hat, or headpiece slot', 'equipment', 1),
    ('neck', 'Necklace or amulet slot', 'equipment', 2),
    ('shoulder', 'Shoulder pads or pauldrons slot', 'equipment', 3),
    ('back', 'Cloak or cape slot', 'equipment', 4),
    ('chest', 'Chest armor or robe slot', 'equipment', 5),
    ('shirt', 'Cosmetic shirt slot', 'equipment', 6),
    ('tabard', 'Guild or faction tabard slot', 'equipment', 7),
    ('wrist', 'Bracers or wristguards slot', 'equipment', 8),
    ('hands', 'Gloves or gauntlets slot', 'equipment', 9),
    ('waist', 'Belt or girdle slot', 'equipment', 10),
    ('legs', 'Pants or leggings slot', 'equipment', 11),
    ('feet', 'Boots or shoes slot', 'equipment', 12),
    ('finger', 'Ring slot (two available)', 'equipment', 13),
    ('trinket', 'Trinket slot (two available)', 'equipment', 14),
    ('held_in_off_hand', 'Off-hand held items slot', 'equipment', 15),
    
    -- Weapon Slots
    ('main_hand', 'Primary weapon slot', 'equipment', 16),
    ('off_hand', 'Secondary weapon or shield slot', 'equipment', 17),
    ('two_hand', 'Two-handed weapon slot', 'equipment', 18),
    ('ranged', 'Ranged weapon slot', 'equipment', 19),
    ('ammo', 'Ammunition slot', 'equipment', 20),
    ('relic', 'Class-specific relic slot', 'equipment', 21),
    
    -- Bag Slots
    ('bag_1', 'Primary bag slot', 'bag', 22),
    ('bag_2', 'Secondary bag slot', 'bag', 23),
    ('bag_3', 'Third bag slot', 'bag', 24),
    ('bag_4', 'Fourth bag slot', 'bag', 25),
    
    -- Non-Equipment
    ('consumable', 'Consumable items (not equipped)', 'consumable', 26),
    ('non_equippable', 'Items that cannot be equipped', 'none', 27);

-- Professions (all WoW professions)
INSERT INTO professions (name, description, profession_type, max_skill_level) VALUES 
    -- Primary Professions
    ('alchemy', 'Brewing potions, elixirs, and flasks', 'primary', 375),
    ('blacksmithing', 'Crafting metal weapons and armor', 'primary', 375),
    ('enchanting', 'Enhancing equipment with magical properties', 'primary', 375),
    ('engineering', 'Creating mechanical devices and gadgets', 'primary', 375),
    ('herbalism', 'Gathering herbs and plants', 'primary', 375),
    ('inscription', 'Creating glyphs, scrolls, and books', 'primary', 375),
    ('jewelcrafting', 'Crafting gems and jewelry', 'primary', 375),
    ('leatherworking', 'Creating leather and mail armor', 'primary', 375),
    ('mining', 'Gathering metals and stone', 'primary', 375),
    ('skinning', 'Gathering leather and hides', 'primary', 375),
    ('tailoring', 'Creating cloth armor and bags', 'primary', 375),
    
    -- Secondary Professions
    ('archaeology', 'Discovering ancient artifacts', 'secondary', 525),
    ('cooking', 'Preparing food and beverages', 'secondary', 375),
    ('first_aid', 'Creating healing bandages', 'secondary', 375),
    ('fishing', 'Catching fish and aquatic creatures', 'secondary', 375),
    
    -- Special Professions
    ('runeforging', 'Death Knight weapon enhancement', 'special', 100),
    ('poisons', 'Rogue poison creation', 'special', 300);