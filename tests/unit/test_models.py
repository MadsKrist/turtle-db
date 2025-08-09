"""
Unit tests for SQLAlchemy models.
"""
from turtle_db.database.models import Item, ItemType
from turtle_db.schemas.common import Currency


class TestCurrencyModel:
    """Test the Currency utility class."""
    
    def test_from_copper_basic(self):
        """Test basic copper conversion."""
        currency = Currency.from_copper(12345)
        assert currency.gold == 1
        assert currency.silver == 23
        assert currency.copper == 45
    
    def test_from_copper_zero(self):
        """Test zero copper conversion."""
        currency = Currency.from_copper(0)
        assert currency.gold == 0
        assert currency.silver == 0
        assert currency.copper == 0
    
    def test_from_copper_large_amount(self):
        """Test large copper amount."""
        currency = Currency.from_copper(999999)
        assert currency.gold == 99
        assert currency.silver == 99
        assert currency.copper == 99
    
    def test_to_copper(self):
        """Test converting currency back to copper."""
        currency = Currency(gold=1, silver=23, copper=45)
        assert currency.to_copper() == 12345


class TestItemModel:
    """Test Item model validation and relationships."""
    
    def test_item_creation(self, db_session):
        """Test basic item creation."""
        # This would require setting up database fixtures
        # For now, test model structure
        item = Item(
            name="Test Sword",
            description="A basic sword",
            type_id=1,
            item_level=50,
            required_level=45,
            quality="uncommon",
            vendor_price_copper=10000
        )
        assert item.name == "Test Sword"
        assert item.quality == "uncommon"
        assert item.vendor_price_copper == 10000


class TestItemTypeModel:
    """Test ItemType model."""
    
    def test_item_type_creation(self):
        """Test item type creation."""
        item_type = ItemType(
            name="Weapon",
            description="Combat weapons"
        )
        assert item_type.name == "Weapon"
        assert item_type.description == "Combat weapons"