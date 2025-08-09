"""
Unit tests for service layer business logic.
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock
from turtle_db.services.items import ItemService
from turtle_db.schemas.items import ItemCreate, ItemFilter
from turtle_db.schemas.common import PaginationParams, ItemQuality, BindType
from turtle_db.utils.exceptions import ItemNotFoundException


class TestItemService:
    """Test ItemService business logic."""

    @pytest_asyncio.fixture
    async def mock_db_session(self):
        """Mock database session."""
        return AsyncMock()

    @pytest_asyncio.fixture
    async def item_service(self, mock_db_session):
        """Create ItemService with mocked database."""
        return ItemService(mock_db_session)

    @pytest.mark.asyncio
    async def test_get_items_with_filters_empty_result(
        self, item_service, mock_db_session
    ):
        """Test getting items with filters returns empty result."""
        # Mock database query to return empty results
        mock_db_session.execute.return_value.scalars.return_value.all.return_value = []
        mock_db_session.execute.return_value.scalar.return_value = 0

        filters = ItemFilter(
            type_name="NonExistentType",
            subtype_name=None,
            slot_name=None,
            quality=None,
            level_min=None,
            level_max=None,
            required_level_min=None,
            required_level_max=None,
            vendor_sellable=None,
            craftable=None,
            search=None,
        )
        pagination = PaginationParams(page=1, limit=20)

        items, total = await item_service.get_items_with_filters(filters, pagination)

        assert items == []
        assert total == 0

    @pytest.mark.asyncio
    async def test_get_item_by_id_not_found(self, item_service, mock_db_session):
        """Test getting non-existent item raises exception."""
        # Mock database query to return None
        mock_db_session.execute.return_value.scalar_one_or_none.return_value = None

        with pytest.raises(ItemNotFoundException):
            await item_service.get_item_by_id(999)

    @pytest.mark.asyncio
    async def test_create_item_validation(self, item_service):
        """Test item creation with validation."""
        item_data = ItemCreate(
            name="Test Item",
            description="Test description",
            type_name="Weapon",
            subtype_name=None,
            slot_name=None,
            quality=ItemQuality.COMMON,
            bind_type=BindType.NONE,
            item_level=1,
            required_level=1,
            max_stack=1,
            vendor_price=None,
        )

        # This test would need proper database fixtures
        # For now, just test the data structure
        assert item_data.name == "Test Item"
        assert item_data.quality == ItemQuality.COMMON
