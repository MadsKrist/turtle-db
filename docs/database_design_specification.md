# Database Design Specification

## Overview
This document provides a comprehensive specification for the enhanced World of Warcraft Items database, designed to support the complete WoW item classification system as outlined in the planning document.

## Design Philosophy

### Hierarchical Classification
The database uses a three-tier hierarchy for item classification:
- **Type** → **Subtype** → **Slot**
- Example: `armor` → `plate` → `chest`
- Example: `weapon` → `one_handed_sword` → `main_hand`

### Flexible Attribute System
- Core attributes stored as columns for performance
- Extended attributes stored as JSON for flexibility
- Support for future expansion without schema changes

### External System Integration
- Support for multiple external data sources
- External ID tracking for import/sync operations
- Source attribution for data provenance

## Database Schema Design

### Core Entity-Relationship Model

```
ItemType (1) ──── (M) ItemSubtype (1) ──── (M) Item
    │                                        │
    │                                        │ (M)
    │                                        │
    │                                   ItemSlot (1)
    │
    └──── (M) Item ──── (M) VendorItem ──── (M) Vendor
              │
              │ (M)
              │
         RecipeIngredient ──── (M) Recipe ──── (M) Profession
              │                     │
              │                     │
         Item (ingredient)     Item (creates)
```

### Item Sets Architecture

```
ItemSet (1) ──── (M) ItemSetPiece ──── (M) Item
   │
   │ (1)
   │
ItemSetBonus (M)
```

## Table Specifications

### Reference Tables

#### item_types
Master list of item categories (12 types total)
- **Primary Key**: `id`
- **Business Key**: `name` (unique)
- **Attributes**: `description`, `sort_order`, `created_at`
- **Examples**: weapon, armor, consumable, trade_goods, container, recipe

#### item_subtypes  
Detailed classification within each type (80+ subtypes)
- **Primary Key**: `id`
- **Foreign Key**: `type_id` → `item_types.id`
- **Business Key**: `(type_id, name)` (unique composite)
- **Examples**: 
  - weapon → dagger, one_handed_sword, two_handed_axe, bow
  - armor → cloth, leather, mail, plate, shield

#### item_slots
Equipment slots for wearable/usable items (27 slots)
- **Primary Key**: `id`
- **Business Key**: `name` (unique)
- **Attributes**: `slot_type` (equipment/bag/ammo), `sort_order`
- **Examples**: head, chest, main_hand, off_hand, finger, trinket

#### professions
Crafting disciplines (17 professions)
- **Primary Key**: `id`
- **Business Key**: `name` (unique)
- **Attributes**: `profession_type` (primary/secondary/special), `max_skill_level`
- **Examples**: blacksmithing, tailoring, alchemy, cooking, fishing

### Core Data Tables

#### items
Central item repository with comprehensive attributes
- **Primary Key**: `id`
- **Foreign Keys**: `type_id`, `subtype_id`, `slot_id`
- **Classification**: Hierarchical type/subtype/slot system
- **Requirements**: level, class, race restrictions
- **Behavior**: bind_type, unique_equipped, stack_size
- **Stats**: JSON storage for flexible attribute system
- **External**: tracking for import system integration

#### vendors
NPC merchants and their locations
- **Primary Key**: `id`
- **Attributes**: Enhanced location data (zone, subzone, coordinates)
- **Behavior**: faction alignment, vendor type classification

#### vendor_items
Item availability and pricing
- **Composite Key**: `(vendor_id, item_id)`
- **Pricing**: copper-based currency system
- **Requirements**: reputation, faction, level gates
- **Availability**: date-based seasonal items

#### recipes
Crafting instructions and requirements
- **Primary Key**: `id`
- **Foreign Keys**: `profession_id`, `creates_item_id`
- **Learning**: recipe acquisition methods and requirements
- **Difficulty**: skill-based difficulty classification
- **External**: import system integration

#### recipe_ingredients
Recipe component requirements
- **Composite Key**: `(recipe_id, ingredient_item_id)`
- **Flexibility**: optional reagents, ingredient groups
- **Quantity**: variable ingredient amounts

### Advanced Features

#### item_sets
Equipment set definitions (Tier gear, dungeon sets)
- **Primary Key**: `id`
- **Business Key**: `name` (unique)
- **Classification**: set_type, tier_level

#### item_set_pieces
Set membership relationships
- **Composite Key**: `(set_id, item_id)`
- **Ordering**: sort_order for set piece display

#### item_set_bonuses
Multi-piece set bonuses
- **Composite Key**: `(set_id, pieces_required)`
- **Effects**: JSON storage for bonus stats

## Data Types and Constraints

### Primary Keys
All tables use auto-incrementing INTEGER primary keys for performance and simplicity.

### Business Keys
Natural keys enforced with UNIQUE constraints:
- `item_types.name`
- `item_slots.name` 
- `professions.name`
- `item_sets.name`
- `(item_subtypes.type_id, item_subtypes.name)`
- `(vendor_items.vendor_id, vendor_items.item_id)`

### Foreign Key Integrity
All foreign keys include proper referential integrity constraints with appropriate cascade behavior.

### JSON Storage
Flexible attribute storage for:
- `items.stats` - Item statistics and bonuses
- `item_set_bonuses.bonus_stats` - Set bonus effects

### Enumerated Values
String-based enumerations for:
- `items.quality`: poor, common, uncommon, rare, epic, legendary, artifact, heirloom
- `items.bind_type`: none, pickup, equip, use, quest, account
- `vendors.faction`: alliance, horde, neutral
- `recipes.recipe_type`: learned, taught, discovered, quest
- `recipes.recipe_difficulty`: trivial, green, yellow, orange, red

## Performance Optimization

### Index Strategy
**Primary Indexes** (automatic):
- All primary key columns
- All unique constraint columns

**Query Optimization Indexes**:
- `idx_items_type_subtype` - Item classification queries
- `idx_items_quality` - Quality-based filtering
- `idx_items_level` - Level range queries
- `idx_items_name` - Text searches
- `idx_vendor_items_vendor` - Vendor inventory queries
- `idx_recipes_profession` - Profession-based recipe lookups

**External Integration Indexes**:
- `idx_items_external` - Import system lookups
- `idx_recipes_external` - Recipe import tracking

### Query Patterns
**Common Access Patterns**:
1. Items by type/subtype hierarchy
2. Items by equipment slot
3. Items by level range and quality
4. Vendor inventories with pricing
5. Recipe lookups by profession
6. Set piece collections

**Optimization Considerations**:
- Type/subtype queries benefit from composite indexing
- JSON stats queries may require specialized indexing in future
- Full-text search on item names may be needed for large datasets

## Data Volume Estimates

### Reference Data (mostly static)
- Item Types: ~12 records
- Item Subtypes: ~80 records  
- Item Slots: ~27 records
- Professions: ~17 records

### Core Data (grows over time)
- Items: 10,000-50,000+ records (depends on data source coverage)
- Vendors: 1,000-5,000 records
- Vendor Items: 50,000-250,000+ records (many-to-many explosion)
- Recipes: 5,000-15,000 records
- Recipe Ingredients: 15,000-50,000+ records

### Advanced Features
- Item Sets: 100-500 records
- Set Pieces: 500-2,500 records
- Set Bonuses: 200-1,000 records

### Storage Projections
- **Minimum Configuration**: ~100MB (core WoW items)
- **Full Coverage**: 500MB-2GB (comprehensive database)
- **With Images/Media**: 5GB+ (if item icons stored)

## Data Quality and Validation

### Referential Integrity
- All foreign key relationships enforced at database level
- Cascade deletions configured appropriately
- Orphan record prevention

### Business Rules
- Items must have valid type (required)
- If subtype specified, must belong to item's type
- Recipe ingredients must be valid items
- Set pieces must reference existing items and sets

### Data Consistency
- Currency stored consistently in copper units
- Timestamps in UTC
- String enumeration values validated
- JSON fields validated for parseable structure

## Migration and Evolution Strategy

### Backward Compatibility
Current schema can be extended non-destructively:
- New columns added with defaults
- New tables added without affecting existing queries
- Existing relationships preserved

### Version Management
- Schema versioning through migration scripts
- Data transformation procedures documented
- Rollback procedures tested and validated

### Future Expansion
Design accommodates:
- Additional item types/subtypes through reference table expansion
- New item attributes through JSON stats extension
- Additional external data sources
- Enhanced recipe complexity (spell effects, multiple outputs)

## Security Considerations

### Data Access
- No sensitive personal data stored
- Game data publicly available in source systems
- Standard database user permission model sufficient

### Import System Integration
- External ID validation prevents injection
- Source attribution for data audit trails
- Import conflict resolution procedures

### API Security
- Standard web API security practices
- Rate limiting for resource-intensive queries
- Input validation for all parameters

This database design provides a robust, scalable foundation for the comprehensive World of Warcraft Items API while maintaining flexibility for future enhancements and integrations.