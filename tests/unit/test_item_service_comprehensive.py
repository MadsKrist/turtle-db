"""
Comprehensive unit tests for ItemService business logic.
"""
import pytest
from turtle_db.services.items import ItemService
from turtle_db.schemas.items import ItemCreate, ItemUpdate, ItemFilter
from turtle_db.schemas.common import PaginationParams, ItemQuality, BindType, Currency
from turtle_db.utils.exceptions import ItemNotFoundException, ReferenceDataNotFoundException


def create_item_filter(**kwargs):
    """Helper function to create ItemFilter with default None values."""
    defaults = {
        'type_name': None,
        'subtype_name': None,
        'slot_name': None,
        'quality': None,
        'level_min': None,
        'level_max': None,
        'required_level_min': None,
        'required_level_max': None,
        'vendor_sellable': None,
        'craftable': None,
        'search': None
    }
    defaults.update(kwargs)
    return ItemFilter(**defaults)


class TestItemServiceCRUD:
    """Test ItemService CRUD operations with real database."""
    
    @pytest.mark.asyncio
    async def test_create_item_success(self, db_session, reference_data):
        """Test successful item creation with all fields."""
        service = ItemService(db_session)
        ref = reference_data
        
        item_data = ItemCreate(
            name="Test Sword",
            description="A test sword for unit testing",
            type_name="Weapon",
            subtype_name="One-Hand Swords",
            slot_name="Main Hand",
            quality=ItemQuality.UNCOMMON,
            bind_type=BindType.EQUIP,
            item_level=20,
            required_level=18,
            max_stack=1,
            vendor_price=Currency(gold=2, silver=50, copper=0)
        )
        
        created_item = await service.create_item(item_data)
        
        assert created_item.name == "Test Sword"
        assert created_item.description == "A test sword for unit testing"
        assert created_item.type_id == ref["item_types"]["weapon"].id
        assert created_item.subtype_id == ref["item_subtypes"]["sword"].id
        assert created_item.slot_id == ref["item_slots"]["main_hand"].id
        assert created_item.quality == "uncommon"
        assert created_item.bind_type == "equip"
        assert created_item.item_level == 20
        assert created_item.required_level == 18
        assert created_item.vendor_price_copper == 25000  # 2g 50s
        assert created_item.id is not None
    
    @pytest.mark.asyncio
    async def test_create_item_minimal_fields(self, db_session, reference_data):
        """Test item creation with only required fields."""
        service = ItemService(db_session)
        
        item_data = ItemCreate(
            name="Minimal Item",
            description=None,
            type_name="Consumable",
            subtype_name=None,
            slot_name=None,
            quality=ItemQuality.COMMON,
            bind_type=BindType.NONE,
            item_level=1,
            required_level=1,
            max_stack=20,
            vendor_price=None
        )
        
        created_item = await service.create_item(item_data)
        
        assert created_item.name == "Minimal Item"
        assert created_item.description is None
        assert created_item.subtype_id is None
        assert created_item.slot_id is None
        assert created_item.vendor_price_copper == 0
    
    @pytest.mark.asyncio 
    async def test_create_item_invalid_type(self, db_session):
        """Test item creation fails with invalid type."""
        service = ItemService(db_session)
        
        item_data = ItemCreate(
            name="Invalid Item",
            description=None,
            type_name="NonExistentType",
            subtype_name=None,
            slot_name=None,
            quality=ItemQuality.COMMON,
            bind_type=BindType.NONE,
            item_level=1,
            required_level=1,
            max_stack=1,
            vendor_price=None
        )
        
        with pytest.raises(ReferenceDataNotFoundException) as exc_info:
            await service.create_item(item_data)
        
        assert "ITEM_TYPE_NOT_FOUND" in str(exc_info.value.code)
    
    @pytest.mark.asyncio
    async def test_get_item_by_id_success(self, db_session, sample_items):
        """Test retrieving item by ID."""
        service = ItemService(db_session)
        items = sample_items
        
        retrieved_item = await service.get_item_by_id(items["iron_sword"].id)
        
        assert retrieved_item.id == items["iron_sword"].id
        assert retrieved_item.name == "Iron Sword"
        # Check relationships exist and have expected values
        assert retrieved_item.type is not None
        if retrieved_item.subtype:
            assert retrieved_item.subtype.name is not None
        if retrieved_item.slot:
            assert retrieved_item.slot.name is not None
    
    @pytest.mark.asyncio
    async def test_get_item_by_id_not_found(self, db_session):
        """Test item not found raises exception."""
        service = ItemService(db_session)
        
        with pytest.raises(ItemNotFoundException) as exc_info:
            await service.get_item_by_id(99999)
        
        assert exc_info.value.code == "ITEM_NOT_FOUND"
    
    @pytest.mark.asyncio
    async def test_update_item_success(self, db_session, sample_items):
        """Test successful item update."""
        service = ItemService(db_session)
        items = sample_items
        
        update_data = ItemUpdate(
            name="Updated Iron Sword",
            description="An updated description",
            item_level=15,
            required_level=None,
            quality=None,
            bind_type=None,
            max_stack=None,
            vendor_price=Currency(gold=1, silver=0, copper=0)
        )
        
        updated_item = await service.update_item(items["iron_sword"].id, update_data)
        
        assert updated_item.name == "Updated Iron Sword"
        assert updated_item.description == "An updated description"
        assert updated_item.item_level == 15
        assert updated_item.vendor_price_copper == 10000  # 1 gold
        # Unchanged fields should remain the same
        assert updated_item.type.name == "Weapon"
        assert updated_item.quality == "common"
    
    @pytest.mark.asyncio
    async def test_delete_item_success(self, db_session, sample_items):
        """Test successful item deletion."""
        service = ItemService(db_session)
        items = sample_items
        
        await service.delete_item(items["health_potion"].id)
        
        # Verify item is deleted
        with pytest.raises(ItemNotFoundException):
            await service.get_item_by_id(items["health_potion"].id)
    
    @pytest.mark.asyncio
    async def test_delete_item_not_found(self, db_session):
        """Test deleting non-existent item raises exception."""
        service = ItemService(db_session)
        
        with pytest.raises(ItemNotFoundException):
            await service.delete_item(99999)


class TestItemServiceFiltering:
    """Test ItemService filtering and pagination."""
    
    @pytest.mark.asyncio
    async def test_get_items_no_filters(self, db_session, sample_items):
        """Test getting all items without filters."""
        service = ItemService(db_session)
        pagination = PaginationParams(page=1, limit=10)
        filters = create_item_filter()
        
        items, total = await service.get_items_with_filters(filters, pagination)
        
        assert total == 3  # iron_sword, steel_chestplate, health_potion
        assert len(items) == 3
        
        # Verify all items are returned
        item_names = {item.name for item in items}
        expected_names = {"Iron Sword", "Steel Chestplate", "Minor Health Potion"}
        assert item_names == expected_names
    
    @pytest.mark.asyncio
    async def test_filter_by_type_name(self, db_session, sample_items):
        """Test filtering items by type name."""
        service = ItemService(db_session)
        pagination = PaginationParams(page=1, limit=10)
        filters = create_item_filter(type_name="Weapon")
        
        items, total = await service.get_items_with_filters(filters, pagination)
        
        assert total == 1
        assert len(items) == 1
        assert items[0].name == "Iron Sword"
        assert items[0].type.name == "Weapon"
    
    @pytest.mark.asyncio
    async def test_filter_by_quality(self, db_session, sample_items):
        """Test filtering items by quality."""
        service = ItemService(db_session)
        pagination = PaginationParams(page=1, limit=10)
        filters = create_item_filter(quality=ItemQuality.UNCOMMON)
        
        items, total = await service.get_items_with_filters(filters, pagination)
        
        assert total == 1
        assert len(items) == 1
        assert items[0].name == "Steel Chestplate"
        assert items[0].quality == "uncommon"
    
    @pytest.mark.asyncio
    async def test_filter_by_level_range(self, db_session, sample_items):
        """Test filtering items by level range."""
        service = ItemService(db_session)
        pagination = PaginationParams(page=1, limit=10)
        filters = create_item_filter(level_min=10, level_max=15)
        
        items, total = await service.get_items_with_filters(filters, pagination)
        
        assert total == 2  # Iron Sword (level 10) and Steel Chestplate (level 15)
        assert len(items) == 2
        
        item_names = {item.name for item in items}
        assert "Iron Sword" in item_names
        assert "Steel Chestplate" in item_names
    
    @pytest.mark.asyncio
    async def test_search_by_name(self, db_session, sample_items):
        """Test searching items by name."""
        service = ItemService(db_session)
        pagination = PaginationParams(page=1, limit=10)
        filters = create_item_filter(search="sword")
        
        items, total = await service.get_items_with_filters(filters, pagination)
        
        assert total == 1
        assert len(items) == 1
        assert items[0].name == "Iron Sword"
    
    @pytest.mark.asyncio
    async def test_pagination_first_page(self, db_session, sample_items):
        """Test pagination first page."""
        service = ItemService(db_session)
        pagination = PaginationParams(page=1, limit=2)
        filters = ItemFilter(
            type_name=None,
            subtype_name=None,
            slot_name=None,
            quality=None,
            level_min=None,
            level_max=None,
            required_level_min=None,
            required_level_max=None,
            vendor_sellable=None,
            craftable=None,
            search=None
        )
        
        items, total = await service.get_items_with_filters(filters, pagination)
        
        assert total == 3
        assert len(items) == 2  # Limited to 2 items per page
    
    @pytest.mark.asyncio
    async def test_pagination_second_page(self, db_session, sample_items):
        """Test pagination second page."""
        service = ItemService(db_session)
        pagination = PaginationParams(page=2, limit=2)
        filters = ItemFilter(
            type_name=None,
            subtype_name=None,
            slot_name=None,
            quality=None,
            level_min=None,
            level_max=None,
            required_level_min=None,
            required_level_max=None,
            vendor_sellable=None,
            craftable=None,
            search=None
        )
        
        items, total = await service.get_items_with_filters(filters, pagination)
        
        assert total == 3
        assert len(items) == 1  # Only 1 item on second page
    
    @pytest.mark.asyncio
    async def test_combined_filters(self, db_session, sample_items):
        """Test combining multiple filters."""
        service = ItemService(db_session)
        pagination = PaginationParams(page=1, limit=10)
        filters = ItemFilter(
            type_name="Armor",
            subtype_name=None,
            slot_name=None,
            quality=ItemQuality.UNCOMMON,
            level_min=10,
            level_max=None,
            required_level_min=None,
            required_level_max=None,
            vendor_sellable=None,
            craftable=None,
            search=None
        )
        
        items, total = await service.get_items_with_filters(filters, pagination)
        
        assert total == 1
        assert len(items) == 1
        assert items[0].name == "Steel Chestplate"
    
    @pytest.mark.asyncio
    async def test_filter_no_results(self, db_session, sample_items):
        """Test filter that returns no results."""
        service = ItemService(db_session)
        pagination = PaginationParams(page=1, limit=10)
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
            search=None
        )
        
        items, total = await service.get_items_with_filters(filters, pagination)
        
        assert total == 0
        assert len(items) == 0