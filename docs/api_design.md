# API Design - World of Warcraft Items API

## Base URL Structure
```
/api/v1/
```

## Core CRUD Endpoints

### Items API
```
GET    /api/v1/items                    # List items with filtering
POST   /api/v1/items                    # Create new item
GET    /api/v1/items/{item_id}          # Get item by ID
PUT    /api/v1/items/{item_id}          # Update item
DELETE /api/v1/items/{item_id}          # Delete item

# Item filtering and grouping
GET    /api/v1/items?type={type_name}              # Filter by type
GET    /api/v1/items?subtype={subtype_name}        # Filter by subtype  
GET    /api/v1/items?slot={slot_name}              # Filter by slot
GET    /api/v1/items?quality={quality}             # Filter by quality
GET    /api/v1/items?level_min={min}&level_max={max} # Level range
GET    /api/v1/items?vendor_sellable=true          # Items sold by vendors
GET    /api/v1/items?craftable=true                # Craftable items
```

### Recipes API
```
GET    /api/v1/recipes                  # List all recipes
POST   /api/v1/recipes                  # Create new recipe
GET    /api/v1/recipes/{recipe_id}      # Get recipe by ID
PUT    /api/v1/recipes/{recipe_id}      # Update recipe
DELETE /api/v1/recipes/{recipe_id}      # Delete recipe

# Recipe filtering
GET    /api/v1/recipes?profession={profession_name}    # By profession
GET    /api/v1/recipes?creates_item={item_id}          # By created item
GET    /api/v1/recipes?skill_level_min={min}           # By skill requirement
GET    /api/v1/recipes?ingredient={item_id}            # Using specific ingredient
```

### Professions API
```
GET    /api/v1/professions             # List all professions
POST   /api/v1/professions             # Create new profession
GET    /api/v1/professions/{prof_id}   # Get profession by ID
PUT    /api/v1/professions/{prof_id}   # Update profession
DELETE /api/v1/professions/{prof_id}   # Delete profession

GET    /api/v1/professions/{prof_id}/recipes  # All recipes for profession
```

### Vendors API
```
GET    /api/v1/vendors                 # List all vendors
POST   /api/v1/vendors                 # Create new vendor
GET    /api/v1/vendors/{vendor_id}     # Get vendor by ID
PUT    /api/v1/vendors/{vendor_id}     # Update vendor
DELETE /api/v1/vendors/{vendor_id}     # Delete vendor

GET    /api/v1/vendors/{vendor_id}/items      # Items sold by vendor
POST   /api/v1/vendors/{vendor_id}/items      # Add item to vendor
DELETE /api/v1/vendors/{vendor_id}/items/{item_id}  # Remove item from vendor
```

### Reference Data APIs
```
GET    /api/v1/item-types              # List item types
GET    /api/v1/item-subtypes           # List item subtypes  
GET    /api/v1/item-slots              # List item slots
```

## Example Request/Response Payloads

### Create Item (Abyssal Inscribed Greaves)
```json
POST /api/v1/items
{
  "name": "Abyssal Inscribed Greaves",
  "description": "Heavy plate boots inscribed with abyssal runes",
  "type": "armor",
  "subtype": "plate", 
  "slot": "feet",
  "item_level": 65,
  "required_level": 60,
  "quality": "rare",
  "bind_type": "pickup"
}
```

### Create Recipe (Titanic Leggings)
```json
POST /api/v1/recipes
{
  "name": "Titanic Leggings",
  "profession": "blacksmithing",
  "creates_item": "Titanic Leggings",
  "required_skill_level": 300,
  "ingredients": [
    {"item_name": "Arcanite Bar", "quantity": 12},
    {"item_name": "Enchanted Thorium Bar", "quantity": 20},
    {"item_name": "Essence of Earth", "quantity": 10},
    {"item_name": "Flask of the Titans", "quantity": 2}
  ]
}
```

### Response Format
```json
{
  "success": true,
  "data": {
    "id": 123,
    "name": "Abyssal Inscribed Greaves",
    "type": {
      "id": 1,
      "name": "armor"
    },
    "subtype": {
      "id": 1, 
      "name": "plate"
    },
    "slot": {
      "id": 3,
      "name": "feet"
    },
    "pricing": {
      "vendor_price": {
        "gold": 12,
        "silver": 34,
        "copper": 56
      }
    },
    "crafting": null
  }
}
```

## Error Responses
```json
{
  "success": false,
  "error": {
    "code": "ITEM_NOT_FOUND",
    "message": "Item with ID 999 not found",
    "details": null
  }
}
```

## Advanced Features

### Search Endpoint
```
GET /api/v1/search?q={query}&type=items|recipes|vendors
```

### Bulk Operations
```
POST /api/v1/items/bulk          # Create multiple items
PUT  /api/v1/items/bulk          # Update multiple items  
```

### Recipe Calculations
```
GET /api/v1/recipes/{recipe_id}/cost    # Calculate material cost
GET /api/v1/recipes/{recipe_id}/tree    # Full ingredient dependency tree
```