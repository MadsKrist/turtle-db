"""
SQLAlchemy ORM models for the WoW Items API.
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ItemType(Base):
    """Item types like armor, weapon, consumable."""
    __tablename__ = "item_types"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    subtypes: Mapped[List["ItemSubtype"]] = relationship("ItemSubtype", back_populates="type")
    items: Mapped[List["Item"]] = relationship("Item", back_populates="type")


class ItemSubtype(Base):
    """Item subtypes like plate, cloth, sword."""
    __tablename__ = "item_subtypes"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type_id: Mapped[int] = mapped_column(Integer, ForeignKey("item_types.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    type: Mapped["ItemType"] = relationship("ItemType", back_populates="subtypes")
    items: Mapped[List["Item"]] = relationship("Item", back_populates="subtype")


class ItemSlot(Base):
    """Item slots like head, chest, feet."""
    __tablename__ = "item_slots"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    items: Mapped[List["Item"]] = relationship("Item", back_populates="slot")


class Profession(Base):
    """Crafting professions like blacksmithing, tailoring."""
    __tablename__ = "professions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    max_skill_level: Mapped[int] = mapped_column(Integer, default=375)
    
    # Relationships
    recipes: Mapped[List["Recipe"]] = relationship("Recipe", back_populates="profession")


class Item(Base):
    """Main items table."""
    __tablename__ = "items"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    type_id: Mapped[int] = mapped_column(Integer, ForeignKey("item_types.id"), nullable=False)
    subtype_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("item_subtypes.id"), nullable=True)
    slot_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("item_slots.id"), nullable=True)
    item_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    required_level: Mapped[int] = mapped_column(Integer, default=1)
    quality: Mapped[str] = mapped_column(String(20), default="common")
    bind_type: Mapped[str] = mapped_column(String(20), default="none")
    max_stack: Mapped[int] = mapped_column(Integer, default=1)
    vendor_price_copper: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    type: Mapped["ItemType"] = relationship("ItemType", back_populates="items")
    subtype: Mapped[Optional["ItemSubtype"]] = relationship("ItemSubtype", back_populates="items")
    slot: Mapped[Optional["ItemSlot"]] = relationship("ItemSlot", back_populates="items")
    vendor_items: Mapped[List["VendorItem"]] = relationship("VendorItem", back_populates="item")
    created_by_recipes: Mapped[List["Recipe"]] = relationship("Recipe", back_populates="creates_item")
    used_in_recipes: Mapped[List["RecipeIngredient"]] = relationship("RecipeIngredient", back_populates="ingredient_item")


class Vendor(Base):
    """NPCs that sell items."""
    __tablename__ = "vendors"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    faction: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    vendor_items: Mapped[List["VendorItem"]] = relationship("VendorItem", back_populates="vendor")


class VendorItem(Base):
    """Items sold by vendors with pricing."""
    __tablename__ = "vendor_items"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vendor_id: Mapped[int] = mapped_column(Integer, ForeignKey("vendors.id"), nullable=False)
    item_id: Mapped[int] = mapped_column(Integer, ForeignKey("items.id"), nullable=False)
    price_copper: Mapped[int] = mapped_column(Integer, nullable=False)
    stock_quantity: Mapped[int] = mapped_column(Integer, default=-1)  # -1 = unlimited
    required_reputation: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Relationships
    vendor: Mapped["Vendor"] = relationship("Vendor", back_populates="vendor_items")
    item: Mapped["Item"] = relationship("Item", back_populates="vendor_items")
    
    __table_args__ = (
        UniqueConstraint("vendor_id", "item_id", name="uq_vendor_item"),
    )


class Recipe(Base):
    """Crafting recipes."""
    __tablename__ = "recipes"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    profession_id: Mapped[int] = mapped_column(Integer, ForeignKey("professions.id"), nullable=False)
    creates_item_id: Mapped[int] = mapped_column(Integer, ForeignKey("items.id"), nullable=False)
    required_skill_level: Mapped[int] = mapped_column(Integer, default=1)
    recipe_type: Mapped[str] = mapped_column(String(20), default="learned")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    profession: Mapped["Profession"] = relationship("Profession", back_populates="recipes")
    creates_item: Mapped["Item"] = relationship("Item", back_populates="created_by_recipes")
    ingredients: Mapped[List["RecipeIngredient"]] = relationship("RecipeIngredient", back_populates="recipe")


class RecipeIngredient(Base):
    """Ingredients required for recipes."""
    __tablename__ = "recipe_ingredients"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    recipe_id: Mapped[int] = mapped_column(Integer, ForeignKey("recipes.id"), nullable=False)
    ingredient_item_id: Mapped[int] = mapped_column(Integer, ForeignKey("items.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    
    # Relationships
    recipe: Mapped["Recipe"] = relationship("Recipe", back_populates="ingredients")
    ingredient_item: Mapped["Item"] = relationship("Item", back_populates="used_in_recipes")
    
    __table_args__ = (
        UniqueConstraint("recipe_id", "ingredient_item_id", name="uq_recipe_ingredient"),
    )