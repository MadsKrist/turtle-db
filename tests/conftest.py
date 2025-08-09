"""
Pytest configuration and fixtures for turtle-db tests.
"""
import asyncio
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from httpx import AsyncClient, ASGITransport
import tempfile
import os

from turtle_db.main import app
from turtle_db.database.models import Base, ItemType, ItemSubtype, ItemSlot, Profession, Item
from turtle_db.api.deps import get_db


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def test_db():
    """Create a test database with temporary SQLite file."""
    # Create temporary file for test database
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)
    
    # Create async engine for test database
    engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}", echo=True)
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session maker
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    yield async_session
    
    # Cleanup
    await engine.dispose()
    os.unlink(db_path)


@pytest_asyncio.fixture
async def db_session(test_db):
    """Create a database session for testing."""
    async with test_db() as session:
        try:
            yield session
        finally:
            # Rollback any uncommitted changes
            if session.in_transaction():
                await session.rollback()
            await session.close()


@pytest.fixture
def client(db_session):
    """Create a test client with database dependency override."""
    def get_test_db():
        return db_session
    
    app.dependency_overrides[get_db] = get_test_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def async_client(db_session):
    """Create an async test client."""
    async def get_test_db():
        yield db_session
    
    app.dependency_overrides[get_db] = get_test_db
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def reference_data(db_session):
    """Create reference data for tests."""
    # Create item types
    weapon_type = ItemType(name="Weapon", description="Combat weapons")
    armor_type = ItemType(name="Armor", description="Protective gear")
    consumable_type = ItemType(name="Consumable", description="Usable items")
    
    db_session.add_all([weapon_type, armor_type, consumable_type])
    await db_session.flush()  # Get IDs without committing
    
    # Create item subtypes
    sword_subtype = ItemSubtype(type_id=weapon_type.id, name="One-Hand Swords", description="Single-handed swords")
    plate_subtype = ItemSubtype(type_id=armor_type.id, name="Plate", description="Heavy armor")
    potion_subtype = ItemSubtype(type_id=consumable_type.id, name="Potion", description="Health/mana potions")
    
    db_session.add_all([sword_subtype, plate_subtype, potion_subtype])
    await db_session.flush()
    
    # Create item slots
    main_hand_slot = ItemSlot(name="Main Hand", description="Main hand weapon slot")
    chest_slot = ItemSlot(name="Chest", description="Chest armor slot")
    
    db_session.add_all([main_hand_slot, chest_slot])
    await db_session.flush()
    
    # Create professions
    blacksmithing = Profession(name="Blacksmithing", description="Metalworking", max_skill_level=375)
    alchemy = Profession(name="Alchemy", description="Potion making", max_skill_level=375)
    
    db_session.add_all([blacksmithing, alchemy])
    await db_session.flush()
    
    return {
        "item_types": {
            "weapon": weapon_type,
            "armor": armor_type,
            "consumable": consumable_type
        },
        "item_subtypes": {
            "sword": sword_subtype,
            "plate": plate_subtype,
            "potion": potion_subtype
        },
        "item_slots": {
            "main_hand": main_hand_slot,
            "chest": chest_slot
        },
        "professions": {
            "blacksmithing": blacksmithing,
            "alchemy": alchemy
        }
    }


@pytest_asyncio.fixture
async def sample_items(db_session, reference_data):
    """Create sample items for testing."""
    ref = reference_data
    
    # Create items
    iron_sword = Item(
        name="Iron Sword",
        description="A sturdy iron sword",
        type_id=ref["item_types"]["weapon"].id,
        subtype_id=ref["item_subtypes"]["sword"].id,
        slot_id=ref["item_slots"]["main_hand"].id,
        item_level=10,
        required_level=8,
        quality="common",
        bind_type="none",
        max_stack=1,
        vendor_price_copper=5000
    )
    
    steel_chestplate = Item(
        name="Steel Chestplate",
        description="Heavy steel chest armor",
        type_id=ref["item_types"]["armor"].id,
        subtype_id=ref["item_subtypes"]["plate"].id,
        slot_id=ref["item_slots"]["chest"].id,
        item_level=15,
        required_level=12,
        quality="uncommon",
        bind_type="boe",
        max_stack=1,
        vendor_price_copper=12000
    )
    
    health_potion = Item(
        name="Minor Health Potion",
        description="Restores 100 health",
        type_id=ref["item_types"]["consumable"].id,
        subtype_id=ref["item_subtypes"]["potion"].id,
        item_level=1,
        required_level=1,
        quality="common",
        bind_type="none",
        max_stack=20,
        vendor_price_copper=50
    )
    
    db_session.add_all([iron_sword, steel_chestplate, health_potion])
    await db_session.flush()
    
    return {
        "iron_sword": iron_sword,
        "steel_chestplate": steel_chestplate,
        "health_potion": health_potion
    }