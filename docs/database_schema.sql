-- World of Warcraft Items API Database Schema
-- SQLite Database Design

-- Core reference tables
CREATE TABLE item_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE, -- armor, weapon, consumable, etc.
    description TEXT
);

CREATE TABLE item_subtypes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type_id INTEGER NOT NULL,
    name VARCHAR(50) NOT NULL, -- plate, cloth, sword, staff, etc.
    description TEXT,
    FOREIGN KEY (type_id) REFERENCES item_types(id)
);

CREATE TABLE item_slots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(30) NOT NULL UNIQUE, -- head, chest, feet, main_hand, etc.
    description TEXT
);

CREATE TABLE professions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE, -- blacksmithing, tailoring, etc.
    description TEXT,
    max_skill_level INTEGER DEFAULT 375
);

-- Main items table
CREATE TABLE items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    type_id INTEGER NOT NULL,
    subtype_id INTEGER,
    slot_id INTEGER,
    item_level INTEGER,
    required_level INTEGER DEFAULT 1,
    quality VARCHAR(20) DEFAULT 'common', -- poor, common, uncommon, rare, epic, legendary
    bind_type VARCHAR(20) DEFAULT 'none', -- none, pickup, equip, use
    max_stack INTEGER DEFAULT 1,
    vendor_price_copper INTEGER DEFAULT 0, -- total price in copper (100 copper = 1 silver, 10000 copper = 1 gold)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (type_id) REFERENCES item_types(id),
    FOREIGN KEY (subtype_id) REFERENCES item_subtypes(id),
    FOREIGN KEY (slot_id) REFERENCES item_slots(id)
);

-- Vendors and their item prices
CREATE TABLE vendors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(100),
    faction VARCHAR(20), -- alliance, horde, neutral
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE vendor_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vendor_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    price_copper INTEGER NOT NULL,
    stock_quantity INTEGER DEFAULT -1, -- -1 for unlimited
    required_reputation VARCHAR(50), -- neutral, friendly, honored, revered, exalted
    FOREIGN KEY (vendor_id) REFERENCES vendors(id),
    FOREIGN KEY (item_id) REFERENCES items(id),
    UNIQUE(vendor_id, item_id)
);

-- Crafting recipes
CREATE TABLE recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    profession_id INTEGER NOT NULL,
    creates_item_id INTEGER NOT NULL,
    required_skill_level INTEGER DEFAULT 1,
    recipe_type VARCHAR(20) DEFAULT 'learned', -- learned, taught, discovered
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (profession_id) REFERENCES professions(id),
    FOREIGN KEY (creates_item_id) REFERENCES items(id)
);

-- Recipe ingredients/reagents
CREATE TABLE recipe_ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id INTEGER NOT NULL,
    ingredient_item_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id),
    FOREIGN KEY (ingredient_item_id) REFERENCES items(id),
    UNIQUE(recipe_id, ingredient_item_id)
);

-- Indexes for better query performance
CREATE INDEX idx_items_type_subtype ON items(type_id, subtype_id);
CREATE INDEX idx_items_slot ON items(slot_id);
CREATE INDEX idx_items_quality ON items(quality);
CREATE INDEX idx_items_level ON items(item_level);
CREATE INDEX idx_vendor_items_vendor ON vendor_items(vendor_id);
CREATE INDEX idx_vendor_items_item ON vendor_items(item_id);
CREATE INDEX idx_recipes_profession ON recipes(profession_id);
CREATE INDEX idx_recipes_creates ON recipes(creates_item_id);
CREATE INDEX idx_recipe_ingredients_recipe ON recipe_ingredients(recipe_id);

-- Sample data inserts
INSERT INTO item_types (name, description) VALUES 
    ('armor', 'Protective equipment worn by characters'),
    ('weapon', 'Combat equipment for dealing damage'),
    ('consumable', 'Items that can be used and consumed'),
    ('trade_goods', 'Materials used in professions and trading');

INSERT INTO item_subtypes (type_id, name, description) VALUES 
    (1, 'plate', 'Heavy metal armor for warriors and paladins'),
    (1, 'cloth', 'Light fabric armor for casters'),
    (1, 'leather', 'Medium armor for rogues and hunters'),
    (1, 'mail', 'Chain armor for hunters and shamans'),
    (2, 'sword', 'Bladed melee weapons'),
    (2, 'staff', 'Two-handed casting weapons');

INSERT INTO item_slots (name, description) VALUES 
    ('head', 'Helmet or hat slot'),
    ('chest', 'Chest armor slot'),
    ('feet', 'Boot or shoe slot'),
    ('legs', 'Pants or leggings slot'),
    ('main_hand', 'Primary weapon slot'),
    ('off_hand', 'Secondary weapon or shield slot');

INSERT INTO professions (name, description, max_skill_level) VALUES 
    ('blacksmithing', 'Crafting metal weapons and armor', 375),
    ('tailoring', 'Creating cloth armor and bags', 375),
    ('alchemy', 'Brewing potions and elixirs', 375);