# Data Models Design - Pydantic Schemas and SQLAlchemy Models

"""
This file demonstrates the data model design for the WoW Items API.
Actual implementation would split these across multiple files.
"""

from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# =============================================================================
# ENUMS
# =============================================================================


class ItemQuality(str, Enum):
    POOR = "poor"
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


class BindType(str, Enum):
    NONE = "none"
    PICKUP = "pickup"
    EQUIP = "equip"
    USE = "use"


class Faction(str, Enum):
    ALLIANCE = "alliance"
    HORDE = "horde"
    NEUTRAL = "neutral"


# =============================================================================
# SQLALCHEMY ORM MODELS
# =============================================================================


class ItemType(Base):
    __tablename__ = "item_types"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text)

    # Relationships
    subtypes = relationship("ItemSubtype", back_populates="type")
    items = relationship("Item", back_populates="type")


class ItemSubtype(Base):
    __tablename__ = "item_subtypes"

    id = Column(Integer, primary_key=True)
    type_id = Column(Integer, ForeignKey("item_types.id"), nullable=False)
    name = Column(String(50), nullable=False)
    description = Column(Text)

    # Relationships
    type = relationship("ItemType", back_populates="subtypes")
    items = relationship("Item", back_populates="subtype")


class ItemSlot(Base):
    __tablename__ = "item_slots"

    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False, unique=True)
    description = Column(Text)

    # Relationships
    items = relationship("Item", back_populates="slot")


class Profession(Base):
    __tablename__ = "professions"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text)
    max_skill_level = Column(Integer, default=375)

    # Relationships
    recipes = relationship("Recipe", back_populates="profession")


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    type_id = Column(Integer, ForeignKey("item_types.id"), nullable=False)
    subtype_id = Column(Integer, ForeignKey("item_subtypes.id"))
    slot_id = Column(Integer, ForeignKey("item_slots.id"))
    item_level = Column(Integer)
    required_level = Column(Integer, default=1)
    quality = Column(String(20), default="common")
    bind_type = Column(String(20), default="none")
    max_stack = Column(Integer, default=1)
    vendor_price_copper = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    type = relationship("ItemType", back_populates="items")
    subtype = relationship("ItemSubtype", back_populates="items")
    slot = relationship("ItemSlot", back_populates="items")
    vendor_items = relationship("VendorItem", back_populates="item")
    created_by_recipes = relationship("Recipe", back_populates="creates_item")
    used_in_recipes = relationship("RecipeIngredient", back_populates="ingredient_item")


class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    location = Column(String(100))
    faction = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    vendor_items = relationship("VendorItem", back_populates="vendor")


class VendorItem(Base):
    __tablename__ = "vendor_items"

    id = Column(Integer, primary_key=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    price_copper = Column(Integer, nullable=False)
    stock_quantity = Column(Integer, default=-1)
    required_reputation = Column(String(50))

    # Relationships
    vendor = relationship("Vendor", back_populates="vendor_items")
    item = relationship("Item", back_populates="vendor_items")


class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    profession_id = Column(Integer, ForeignKey("professions.id"), nullable=False)
    creates_item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    required_skill_level = Column(Integer, default=1)
    recipe_type = Column(String(20), default="learned")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    profession = relationship("Profession", back_populates="recipes")
    creates_item = relationship("Item", back_populates="created_by_recipes")
    ingredients = relationship("RecipeIngredient", back_populates="recipe")


class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"

    id = Column(Integer, primary_key=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    ingredient_item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)

    # Relationships
    recipe = relationship("Recipe", back_populates="ingredients")
    ingredient_item = relationship("Item", back_populates="used_in_recipes")


# =============================================================================
# PYDANTIC SCHEMAS
# =============================================================================


# Currency utility
class Currency(BaseModel):
    gold: int = Field(ge=0)
    silver: int = Field(ge=0, le=99)
    copper: int = Field(ge=0, le=99)

    @classmethod
    def from_copper(cls, total_copper: int) -> "Currency":
        """Convert copper to gold/silver/copper breakdown"""
        gold = total_copper // 10000
        remaining = total_copper % 10000
        silver = remaining // 100
        copper = remaining % 100
        return cls(gold=gold, silver=silver, copper=copper)

    def to_copper(self) -> int:
        """Convert to total copper"""
        return self.gold * 10000 + self.silver * 100 + self.copper


# Base schemas
class ItemTypeSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str] = None


class ItemSubtypeSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str] = None
    type: Optional[ItemTypeSchema] = None


class ItemSlotSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str] = None


class ProfessionSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str] = None
    max_skill_level: int = 375


# Item schemas
class ItemCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = None
    type: str  # Will be resolved to type_id
    subtype: Optional[str] = None  # Will be resolved to subtype_id
    slot: Optional[str] = None  # Will be resolved to slot_id
    item_level: Optional[int] = Field(ge=1, le=100, default=None)
    required_level: int = Field(ge=1, le=80, default=1)
    quality: ItemQuality = ItemQuality.COMMON
    bind_type: BindType = BindType.NONE
    max_stack: int = Field(ge=1, le=200, default=1)
    vendor_price: Optional[Currency] = None


class ItemUpdate(BaseModel):
    name: Optional[str] = Field(min_length=1, max_length=100, default=None)
    description: Optional[str] = None
    item_level: Optional[int] = Field(ge=1, le=100, default=None)
    required_level: Optional[int] = Field(ge=1, le=80, default=None)
    quality: Optional[ItemQuality] = None
    bind_type: Optional[BindType] = None
    max_stack: Optional[int] = Field(ge=1, le=200, default=None)
    vendor_price: Optional[Currency] = None


class ItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str]
    type: ItemTypeSchema
    subtype: Optional[ItemSubtypeSchema]
    slot: Optional[ItemSlotSchema]
    item_level: Optional[int]
    required_level: int
    quality: str
    bind_type: str
    max_stack: int
    pricing: Optional[dict] = None  # Computed field for vendor pricing
    crafting: Optional[dict] = None  # Computed field for recipe info
    created_at: datetime
    updated_at: datetime


# Recipe schemas
class RecipeIngredientCreate(BaseModel):
    item_name: str
    quantity: int = Field(ge=1, le=200)


class RecipeIngredientResponse(BaseModel):
    item: ItemResponse
    quantity: int


class RecipeCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    profession: str  # Will be resolved to profession_id
    creates_item: str  # Item name, will be resolved to creates_item_id
    required_skill_level: int = Field(ge=1, le=375, default=1)
    recipe_type: str = Field(default="learned")
    ingredients: List[RecipeIngredientCreate]


class RecipeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    profession: ProfessionSchema
    creates_item: ItemResponse
    required_skill_level: int
    recipe_type: str
    ingredients: List[RecipeIngredientResponse]
    estimated_cost: Optional[Currency] = None  # Computed field
    created_at: datetime


# Vendor schemas
class VendorCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    location: Optional[str] = Field(max_length=100, default=None)
    faction: Faction = Faction.NEUTRAL


class VendorItemCreate(BaseModel):
    item_name: str
    price: Currency
    stock_quantity: int = Field(ge=-1, default=-1)  # -1 = unlimited
    required_reputation: Optional[str] = None


class VendorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    location: Optional[str]
    faction: str
    created_at: datetime


# Response wrappers
class APIResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    error: Optional[dict] = None


class PaginatedResponse(BaseModel):
    success: bool = True
    data: List[dict]
    pagination: dict  # page, limit, total, pages
