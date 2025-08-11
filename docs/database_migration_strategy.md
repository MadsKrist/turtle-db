# Database Migration Strategy

## Overview
This document outlines the migration strategy from the current basic schema to the comprehensive WoW item classification system.

## Current vs Enhanced Schema Comparison

### Current Limitations
- Only 4 basic item types (armor, weapon, consumable, trade_goods)
- Limited subtypes (6 total: plate, cloth, leather, mail, sword, staff)
- Basic slot system (6 slots: head, chest, feet, legs, main_hand, off_hand)
- Simple professions (3 total: blacksmithing, tailoring, alchemy)

### Enhanced Capabilities
- 12 comprehensive item types covering all WoW categories
- 80+ subtypes with proper hierarchical organization
- 27 equipment slots including bags, rings, trinkets, relics
- 17 professions including primary, secondary, and special types
- Item sets and set bonuses support
- Enhanced item attributes (stats, durability, charges, cooldowns)
- External data source tracking for imports

## Migration Steps

### Phase 1: Schema Extension (Non-Breaking)
Add new tables and columns without modifying existing structure.

**New Tables to Add:**
- `item_sets` - Equipment set definitions
- `item_set_pieces` - Items belonging to sets
- `item_set_bonuses` - Set bonus effects

**Columns to Add to Existing Tables:**
```sql
-- Add to items table
ALTER TABLE items ADD COLUMN required_class VARCHAR(100);
ALTER TABLE items ADD COLUMN required_race VARCHAR(100);
ALTER TABLE items ADD COLUMN unique_equipped BOOLEAN DEFAULT FALSE;
ALTER TABLE items ADD COLUMN stats TEXT; -- JSON stats
ALTER TABLE items ADD COLUMN durability INTEGER;
ALTER TABLE items ADD COLUMN charges INTEGER;
ALTER TABLE items ADD COLUMN cooldown_seconds INTEGER;
ALTER TABLE items ADD COLUMN external_id INTEGER;
ALTER TABLE items ADD COLUMN external_source VARCHAR(50);

-- Add to vendors table
ALTER TABLE vendors ADD COLUMN zone VARCHAR(50);
ALTER TABLE vendors ADD COLUMN subzone VARCHAR(50);
ALTER TABLE vendors ADD COLUMN vendor_type VARCHAR(30);
ALTER TABLE vendors ADD COLUMN coordinates VARCHAR(20);

-- Add to vendor_items table
ALTER TABLE vendor_items ADD COLUMN required_faction VARCHAR(20);
ALTER TABLE vendor_items ADD COLUMN required_level INTEGER;
ALTER TABLE vendor_items ADD COLUMN available_start_date DATE;
ALTER TABLE vendor_items ADD COLUMN available_end_date DATE;

-- Add to recipes table
ALTER TABLE recipes ADD COLUMN creates_quantity INTEGER DEFAULT 1;
ALTER TABLE recipes ADD COLUMN recipe_difficulty VARCHAR(20) DEFAULT 'yellow';
ALTER TABLE recipes ADD COLUMN teaches_spell_id INTEGER;
ALTER TABLE recipes ADD COLUMN required_reputation VARCHAR(50);
ALTER TABLE recipes ADD COLUMN required_faction VARCHAR(20);
ALTER TABLE recipes ADD COLUMN required_level INTEGER;
ALTER TABLE recipes ADD COLUMN external_id INTEGER;
ALTER TABLE recipes ADD COLUMN external_source VARCHAR(50);

-- Add to recipe_ingredients table
ALTER TABLE recipe_ingredients ADD COLUMN is_optional BOOLEAN DEFAULT FALSE;
ALTER TABLE recipe_ingredients ADD COLUMN ingredient_group INTEGER DEFAULT 1;
ALTER TABLE recipe_ingredients ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP;

-- Add to existing reference tables
ALTER TABLE item_types ADD COLUMN sort_order INTEGER DEFAULT 0;
ALTER TABLE item_types ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE item_subtypes ADD COLUMN sort_order INTEGER DEFAULT 0;
ALTER TABLE item_subtypes ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE item_slots ADD COLUMN slot_type VARCHAR(20);
ALTER TABLE item_slots ADD COLUMN sort_order INTEGER DEFAULT 0;
ALTER TABLE item_slots ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE professions ADD COLUMN profession_type VARCHAR(20) DEFAULT 'primary';
ALTER TABLE professions ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP;
```

### Phase 2: Data Population
Populate the reference tables with comprehensive WoW data.

**Item Types Expansion:**
```sql
INSERT INTO item_types (name, description, sort_order) VALUES 
    ('container', 'Bags and storage items', 3),
    ('projectile', 'Ammunition for ranged weapons', 6),
    ('quiver', 'Containers for ammunition', 7),
    ('recipe', 'Plans and patterns for crafting', 8),
    ('miscellaneous', 'Various utility and special items', 9),
    ('currency', 'Alternative currency items', 10),
    ('quest', 'Quest-related items', 11),
    ('key', 'Keys and lockpicks', 12);
```

**Item Subtypes Expansion:**
- Add all 80+ subtypes from enhanced schema
- Maintain backward compatibility with existing 6 subtypes

**Equipment Slots Expansion:**
- Add 21 new equipment slots
- Set appropriate slot_type values for existing slots

**Professions Expansion:**
- Add 14 new professions
- Set profession_type for existing professions

### Phase 3: Data Migration and Validation
Migrate existing data to use new structure where applicable.

**Validation Queries:**
```sql
-- Check data integrity after migration
SELECT 
    it.name as type_name,
    ist.name as subtype_name,
    COUNT(*) as item_count
FROM items i
JOIN item_types it ON i.type_id = it.id
LEFT JOIN item_subtypes ist ON i.subtype_id = ist.id
GROUP BY it.name, ist.name
ORDER BY it.sort_order, ist.sort_order;

-- Verify all items have valid type/subtype combinations
SELECT i.* FROM items i
LEFT JOIN item_subtypes ist ON i.subtype_id = ist.id
WHERE i.subtype_id IS NOT NULL AND ist.type_id != i.type_id;
```

### Phase 4: Index Optimization
Add performance indexes for the new structure.

```sql
-- Additional indexes for enhanced schema
CREATE INDEX idx_items_external ON items(external_source, external_id);
CREATE INDEX idx_items_name ON items(name);
CREATE INDEX idx_items_bind_type ON items(bind_type);
CREATE INDEX idx_vendor_items_faction ON vendor_items(required_faction);
CREATE INDEX idx_recipes_skill ON recipes(required_skill_level);
CREATE INDEX idx_recipes_external ON recipes(external_source, external_id);
```

### Phase 5: Application Code Updates
Update SQLAlchemy models and API endpoints to support new features.

**Model Updates Required:**
- Enhanced `Item` model with new attributes
- New `ItemSet`, `ItemSetPiece`, `ItemSetBonus` models
- Updated relationships and validation
- JSON stats parsing and serialization

**API Endpoint Updates:**
- Enhanced filtering options for items
- Set-based queries and endpoints
- External ID lookups for import system
- Expanded vendor and recipe functionality

## Rollback Strategy

### Immediate Rollback (Phase 1-2)
- New tables can be dropped without affecting existing functionality
- New columns can be ignored by existing code
- No data loss risk

### Post-Migration Rollback (Phase 3+)
- Backup database before migration
- Document all schema changes for reversal
- Test rollback procedure in staging environment

## Testing Strategy

### Unit Tests
- Model validation with new attributes
- Relationship integrity tests
- JSON stats serialization tests

### Integration Tests
- API endpoint compatibility
- Import system with enhanced schema
- Query performance with expanded data

### Data Quality Tests
- Item type/subtype hierarchy validation
- Equipment slot compatibility checks
- Recipe ingredient relationship verification

## Performance Considerations

### Expected Impact
- Moderate increase in storage (estimated 15-20% due to new attributes)
- Improved query performance with better indexing
- Enhanced filtering capabilities

### Monitoring
- Query execution time before/after migration
- Database size growth tracking
- Index usage statistics

## Timeline Estimate
- **Phase 1**: 2-3 hours (schema extension)
- **Phase 2**: 4-6 hours (data population and validation)
- **Phase 3**: 2-3 hours (data migration)
- **Phase 4**: 1 hour (index creation)
- **Phase 5**: 8-12 hours (application code updates)

**Total: 17-25 hours** (2-3 days for complete migration)

## Risk Assessment

### Low Risk
- Schema extension is non-breaking
- Existing functionality remains intact
- Comprehensive data validation

### Medium Risk
- Large data population may impact performance temporarily
- Application code updates require thorough testing

### Mitigation Strategies
- Staged rollout with feature flags
- Comprehensive backup before migration
- Performance monitoring throughout process
- Rollback procedures tested and documented