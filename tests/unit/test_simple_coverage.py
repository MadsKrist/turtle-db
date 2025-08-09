"""
Simple tests to increase code coverage on utility modules.
"""
from turtle_db.config import Settings
from turtle_db.schemas.common import Currency, ItemQuality, BindType, APIResponse, PaginationMeta


class TestConfig:
    """Test configuration settings."""
    
    def test_settings_creation(self):
        """Test settings instance creation."""
        settings = Settings()
        assert settings.database_url is not None
        assert settings.copper_per_silver == 100
        assert settings.copper_per_gold == 10000
        assert hasattr(settings, 'environment')


class TestCommonSchemas:
    """Test common schema functionality."""
    
    def test_currency_conversion_edge_cases(self):
        """Test currency conversion edge cases."""
        # Test negative copper (should be 0)
        currency = Currency.from_copper(-100)
        assert currency.gold == 0
        assert currency.silver == 0
        assert currency.copper == 0
        
        # Test exact gold amount
        currency = Currency.from_copper(10000)
        assert currency.gold == 1
        assert currency.silver == 0
        assert currency.copper == 0
        
        # Test exact silver amount
        currency = Currency.from_copper(100)
        assert currency.gold == 0
        assert currency.silver == 1
        assert currency.copper == 0
    
    def test_currency_round_trip(self):
        """Test currency conversion round trip."""
        original_copper = 15375  # 1g 53s 75c
        currency = Currency.from_copper(original_copper)
        converted_back = currency.to_copper()
        assert converted_back == original_copper
    
    def test_item_quality_enum(self):
        """Test ItemQuality enum values."""
        assert ItemQuality.POOR == "poor"
        assert ItemQuality.COMMON == "common"
        assert ItemQuality.UNCOMMON == "uncommon"
        assert ItemQuality.RARE == "rare"
        assert ItemQuality.EPIC == "epic"
        assert ItemQuality.LEGENDARY == "legendary"
    
    def test_bind_type_enum(self):
        """Test BindType enum values."""
        assert BindType.NONE == "none"
        assert BindType.PICKUP == "pickup"
        assert BindType.EQUIP == "equip"
        assert BindType.USE == "use"
    
    def test_api_response_success(self):
        """Test successful API response."""
        response = APIResponse[dict](
            success=True,
            data={"test": "data"},
            message="Operation successful"
        )
        assert response.success is True
        assert response.data == {"test": "data"}
        assert response.error is None
    
    def test_api_response_error(self):
        """Test error API response."""
        error_details = {"code": "TEST_ERROR", "message": "Test error"}
        response = APIResponse[None](
            success=False,
            data=None,
            error=error_details
        )
        assert response.success is False
        assert response.data is None
        assert response.error == error_details
    
    def test_pagination_meta(self):
        """Test pagination metadata."""
        pagination = PaginationMeta(
            page=2,
            limit=10,
            total=25,
            pages=3,
            has_next=True,
            has_previous=True
        )
        assert pagination.page == 2
        assert pagination.limit == 10
        assert pagination.total == 25
        assert pagination.pages == 3
        assert pagination.has_next is True
        assert pagination.has_previous is True


class TestModelBasics:
    """Test basic model instantiation."""
    
    def test_item_model_creation(self):
        """Test Item model instantiation."""
        from turtle_db.database.models import Item
        
        item = Item(
            name="Test Item",
            type_id=1,
            quality="common",
            item_level=1,
            required_level=1,
            vendor_price_copper=100
        )
        assert item.name == "Test Item"
        assert item.type_id == 1
        assert item.quality == "common"
        assert item.vendor_price_copper == 100
    
    def test_item_type_model_creation(self):
        """Test ItemType model instantiation."""
        from turtle_db.database.models import ItemType
        
        item_type = ItemType(name="Weapon", description="Combat weapons")
        assert item_type.name == "Weapon"
        assert item_type.description == "Combat weapons"
    
    def test_profession_model_creation(self):
        """Test Profession model instantiation."""
        from turtle_db.database.models import Profession
        
        profession = Profession(
            name="Blacksmithing",
            description="Metalworking",
            max_skill_level=375
        )
        assert profession.name == "Blacksmithing"
        assert profession.max_skill_level == 375


class TestScraperModels:
    """Test scraper model classes."""
    
    def test_scraped_item_creation(self):
        """Test ScrapedItem model creation."""
        from turtle_db.scrapers.models import ScrapedItem
        
        item = ScrapedItem(
            name="Test Sword",
            item_type="Weapon",
            subtype="Sword", 
            slot="Main Hand",
            quality="uncommon",
            item_level=10,
            required_level=8,
            description="A test sword",
            crafting_spells=[]
        )
        assert item.name == "Test Sword"
        assert item.item_type == "Weapon"
        assert item.quality == "uncommon"
        assert item.crafting_spells == []
    
    def test_scraped_recipe_creation(self):
        """Test ScrapedRecipe model creation."""
        from turtle_db.scrapers.models import ScrapedRecipe
        
        recipe = ScrapedRecipe(
            spell_id="123",
            name="Iron Sword Recipe",
            profession="Blacksmithing",
            required_skill=100,
            ingredients=[]
        )
        assert recipe.spell_id == "123"
        assert recipe.name == "Iron Sword Recipe"
        assert recipe.profession == "Blacksmithing"
        assert recipe.required_skill == 100
    
    def test_scraped_ingredient_creation(self):
        """Test ScrapedIngredient model creation."""
        from turtle_db.scrapers.models import ScrapedIngredient
        
        ingredient = ScrapedIngredient(name="Iron Bar", quantity=3)
        assert ingredient.name == "Iron Bar"
        assert ingredient.quantity == 3


class TestBaseScraper:
    """Test base scraper functionality."""
    
    def test_base_scraper_instantiation(self):
        """Test BaseScraper can be instantiated."""
        from turtle_db.scrapers.base import BaseScraper
        from turtle_db.scrapers.models import ScrapedItem, ScrapedRecipe
        
        class TestScraper(BaseScraper):
            async def scrape_item(self, url: str) -> ScrapedItem:
                return ScrapedItem(
                    name="Test",
                    item_type="Test",
                    subtype=None,
                    slot=None,
                    quality="common",
                    item_level=1,
                    required_level=1,
                    description="Test",
                    crafting_spells=[]
                )
            
            async def scrape_recipe(self, spell_id: str) -> ScrapedRecipe:
                return ScrapedRecipe(
                    spell_id=spell_id,
                    name="Test Recipe",
                    profession="Test",
                    required_skill=1,
                    ingredients=[]
                )
            
            def validate_url(self, url: str) -> bool:
                return True
            
            def get_supported_domains(self) -> list[str]:
                return ["test.com"]
        
        scraper = TestScraper()
        assert scraper is not None