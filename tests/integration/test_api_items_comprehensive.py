"""
Comprehensive integration tests for Items API endpoints.
"""
import pytest
from fastapi import status


class TestItemsAPICRUD:
    """Test Items API CRUD operations with database integration."""
    
    @pytest.mark.asyncio
    async def test_get_items_empty_database(self, async_client, reference_data):
        """Test getting items from database with only reference data."""
        response = await async_client.get("/api/v1/items")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["success"] is True
        assert data["data"] == []
        assert data["pagination"]["total"] == 0
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["limit"] == 20
    
    @pytest.mark.asyncio
    async def test_get_items_with_data(self, async_client, sample_items):
        """Test getting items with sample data."""
        response = await async_client.get("/api/v1/items")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 3
        assert data["pagination"]["total"] == 3
        
        # Verify item names are present
        item_names = {item["name"] for item in data["data"]}
        expected_names = {"Iron Sword", "Steel Chestplate", "Minor Health Potion"}
        assert item_names == expected_names
    
    @pytest.mark.asyncio
    async def test_get_item_by_id_success(self, async_client, sample_items):
        """Test getting specific item by ID."""
        items = sample_items
        item_id = items["iron_sword"].id
        
        response = await async_client.get(f"/api/v1/items/{item_id}")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == "Iron Sword"
        assert data["data"]["type"]["name"] == "Weapon"
        assert data["data"]["subtype"]["name"] == "One-Hand Swords"
        assert data["data"]["slot"]["name"] == "Main Hand"
        assert data["data"]["quality"] == "common"
    
    @pytest.mark.asyncio
    async def test_get_item_by_id_not_found(self, async_client, reference_data):
        """Test getting non-existent item."""
        response = await async_client.get("/api/v1/items/99999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "ITEM_NOT_FOUND"
    
    @pytest.mark.asyncio
    async def test_create_item_success(self, async_client, reference_data):
        """Test successful item creation."""
        item_data = {
            "name": "Test Mace",
            "description": "A testing mace",
            "type_name": "Weapon",
            "subtype_name": "One-Hand Swords",
            "slot_name": "Main Hand",
            "quality": "uncommon",
            "bind_type": "equip",
            "item_level": 25,
            "required_level": 20,
            "max_stack": 1,
            "vendor_price": {
                "gold": 5,
                "silver": 25,
                "copper": 50
            }
        }
        
        response = await async_client.post("/api/v1/items", json=item_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == "Test Mace"
        assert data["data"]["quality"] == "uncommon"
        assert data["data"]["bind_type"] == "equip"
        assert data["data"]["pricing"]["vendor_price"]["total_copper"] == 52550
        assert data["message"] == "Item created successfully"
    
    @pytest.mark.asyncio
    async def test_create_item_minimal_data(self, async_client, reference_data):
        """Test item creation with minimal required data."""
        item_data = {
            "name": "Minimal Potion",
            "type_name": "Consumable",
            "quality": "common",
            "bind_type": "none",
            "item_level": 1,
            "required_level": 1,
            "max_stack": 5
        }
        
        response = await async_client.post("/api/v1/items", json=item_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == "Minimal Potion"
        assert data["data"]["description"] is None
        assert data["data"]["subtype"] is None
        assert data["data"]["slot"] is None
    
    @pytest.mark.asyncio
    async def test_create_item_invalid_type(self, async_client, reference_data):
        """Test item creation with invalid type."""
        item_data = {
            "name": "Invalid Item",
            "type_name": "InvalidType",
            "quality": "common",
            "bind_type": "none",
            "item_level": 1,
            "required_level": 1,
            "max_stack": 1
        }
        
        response = await async_client.post("/api/v1/items", json=item_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        data = response.json()
        assert data["success"] is False
        assert "ITEM_TYPE_NOT_FOUND" in data["error"]["code"]
    
    @pytest.mark.asyncio
    async def test_create_item_validation_error(self, async_client, reference_data):
        """Test item creation with validation errors."""
        item_data = {
            "name": "",  # Empty name should fail
            "type_name": "Weapon"
        }
        
        response = await async_client.post("/api/v1/items", json=item_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.asyncio
    async def test_update_item_success(self, async_client, sample_items):
        """Test successful item update."""
        items = sample_items
        item_id = items["health_potion"].id
        
        update_data = {
            "name": "Greater Health Potion",
            "description": "Restores 250 health",
            "item_level": 5
        }
        
        response = await async_client.put(f"/api/v1/items/{item_id}", json=update_data)
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == "Greater Health Potion"
        assert data["data"]["description"] == "Restores 250 health"
        assert data["data"]["item_level"] == 5
        # Unchanged fields should remain
        assert data["data"]["type"]["name"] == "Consumable"
        assert data["data"]["quality"] == "common"
    
    @pytest.mark.asyncio
    async def test_update_item_not_found(self, async_client, reference_data):
        """Test updating non-existent item."""
        update_data = {"name": "Non-existent"}
        
        response = await async_client.put("/api/v1/items/99999", json=update_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "ITEM_NOT_FOUND"
    
    @pytest.mark.asyncio
    async def test_delete_item_success(self, async_client, sample_items):
        """Test successful item deletion."""
        items = sample_items
        item_id = items["steel_chestplate"].id
        
        response = await async_client.delete(f"/api/v1/items/{item_id}")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "Item deleted successfully"
        
        # Verify item is deleted
        response = await async_client.get(f"/api/v1/items/{item_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.asyncio
    async def test_delete_item_not_found(self, async_client, reference_data):
        """Test deleting non-existent item."""
        response = await async_client.delete("/api/v1/items/99999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "ITEM_NOT_FOUND"


class TestItemsAPIFiltering:
    """Test Items API filtering and pagination."""
    
    @pytest.mark.asyncio
    async def test_filter_by_type(self, async_client, sample_items):
        """Test filtering items by type."""
        response = await async_client.get("/api/v1/items?type_name=Weapon")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 1
        assert data["data"][0]["name"] == "Iron Sword"
        assert data["pagination"]["total"] == 1
    
    @pytest.mark.asyncio
    async def test_filter_by_quality(self, async_client, sample_items):
        """Test filtering items by quality."""
        response = await async_client.get("/api/v1/items?quality=uncommon")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 1
        assert data["data"][0]["name"] == "Steel Chestplate"
        assert data["data"][0]["quality"] == "uncommon"
    
    @pytest.mark.asyncio
    async def test_filter_invalid_quality(self, async_client, sample_items):
        """Test filtering with invalid quality."""
        response = await async_client.get("/api/v1/items?quality=invalid")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "INVALID_QUALITY"
    
    @pytest.mark.asyncio
    async def test_filter_by_level_range(self, async_client, sample_items):
        """Test filtering items by level range."""
        response = await async_client.get("/api/v1/items?level_min=10&level_max=15")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 2  # Iron Sword (10) and Steel Chestplate (15)
        
        item_names = {item["name"] for item in data["data"]}
        assert "Iron Sword" in item_names
        assert "Steel Chestplate" in item_names
    
    @pytest.mark.asyncio
    async def test_search_items(self, async_client, sample_items):
        """Test searching items by name."""
        response = await async_client.get("/api/v1/items?search=sword")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 1
        assert data["data"][0]["name"] == "Iron Sword"
    
    @pytest.mark.asyncio
    async def test_pagination(self, async_client, sample_items):
        """Test pagination functionality."""
        # First page with limit 2
        response = await async_client.get("/api/v1/items?page=1&limit=2")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 2
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["limit"] == 2
        assert data["pagination"]["total"] == 3
        assert data["pagination"]["pages"] == 2
        assert data["pagination"]["has_next"] is True
        assert data["pagination"]["has_previous"] is False
        
        # Second page
        response = await async_client.get("/api/v1/items?page=2&limit=2")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 1  # Only 1 item on page 2
        assert data["pagination"]["page"] == 2
        assert data["pagination"]["has_next"] is False
        assert data["pagination"]["has_previous"] is True
    
    @pytest.mark.asyncio
    async def test_combined_filters(self, async_client, sample_items):
        """Test combining multiple filters."""
        response = await async_client.get("/api/v1/items?type_name=Armor&quality=uncommon")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["success"] is True
        assert len(data["data"]) == 1
        assert data["data"][0]["name"] == "Steel Chestplate"


class TestItemsAPIGeneral:
    """Test general API functionality."""
    
    @pytest.mark.asyncio
    async def test_health_check(self, async_client):
        """Test health check endpoint."""
        response = await async_client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "turtle-db"
    
    @pytest.mark.asyncio
    async def test_root_endpoint(self, async_client):
        """Test root endpoint."""
        response = await async_client.get("/")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["name"] == "World of Warcraft Items API"
        assert data["version"] == "0.1.0"
        assert data["docs"] == "/docs"
        assert data["api_base"] == "/api/v1"
    
    @pytest.mark.asyncio
    async def test_api_documentation_access(self, async_client):
        """Test API documentation endpoints are accessible."""
        # OpenAPI JSON
        response = await async_client.get("/openapi.json")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["info"]["title"] == "World of Warcraft Items API"
        assert data["info"]["version"] == "0.1.0"