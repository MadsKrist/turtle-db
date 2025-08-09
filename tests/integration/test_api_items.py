"""
Integration tests for Items API endpoints.
"""
import pytest
from fastapi import status


class TestItemsAPI:
    """Test Items API endpoints with database integration."""
    
    @pytest.mark.asyncio
    async def test_get_items_empty_database(self, async_client):
        """Test getting items from empty database."""
        response = await async_client.get("/api/v1/items")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["success"] is True
        assert data["data"] == []
        assert data["pagination"]["total"] == 0
    
    @pytest.mark.asyncio
    async def test_get_items_pagination(self, async_client):
        """Test items endpoint pagination."""
        response = await async_client.get("/api/v1/items?page=1&limit=10")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "pagination" in data
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["limit"] == 10
    
    @pytest.mark.asyncio
    async def test_get_item_not_found(self, async_client):
        """Test getting non-existent item."""
        response = await async_client.get("/api/v1/items/999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        data = response.json()
        assert data["success"] is False
        assert "ITEM_NOT_FOUND" in data["error"]["code"]
    
    @pytest.mark.asyncio
    async def test_create_item_invalid_data(self, async_client):
        """Test creating item with invalid data."""
        invalid_item = {
            "name": "",  # Empty name should fail validation
            "quality": "invalid_quality"
        }
        
        response = await async_client.post("/api/v1/items", json=invalid_item)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
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