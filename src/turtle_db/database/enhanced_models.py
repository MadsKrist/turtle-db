"""
Enhanced SQLAlchemy ORM models for the comprehensive WoW Items API.
Based on the full World of Warcraft item classification system.
"""
import json
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, UniqueConstraint, Boolean, Date
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

def utc_now():
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)


class ItemType(Base):
    """Item types like weapon, armor, consumable, etc."""
    __tablename__ = "item_types"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    
    # Relationships
    subtypes: Mapped[List["ItemSubtype"]] = relationship("ItemSubtype", back_populates="type", cascade="all, delete-orphan")
    items: Mapped[List["Item"]] = relationship("Item", back_populates="type")


class ItemSubtype(Base):
    """Item subtypes like plate, cloth, sword, dagger, etc."""
    __tablename__ = "item_subtypes"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type_id: Mapped[int] = mapped_column(Integer, ForeignKey("item_types.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    
    # Relationships
    type: Mapped["ItemType"] = relationship("ItemType", back_populates="subtypes")
    items: Mapped[List["Item"]] = relationship("Item", back_populates="subtype")
    
    __table_args__ = (
        UniqueConstraint("type_id", "name", name="uq_item_subtype_type_name"),
    )


class ItemSlot(Base):
    """Item slots like head, chest, feet, main_hand, etc."""
    __tablename__ = "item_slots"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    slot_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # equipment, bag, ammo, etc.
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    
    # Relationships
    items: Mapped[List["Item"]] = relationship("Item", back_populates="slot")


class Profession(Base):
    """Crafting professions like blacksmithing, tailoring, etc."""
    __tablename__ = "professions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    profession_type: Mapped[str] = mapped_column(String(20), default="primary")  # primary, secondary, special
    max_skill_level: Mapped[int] = mapped_column(Integer, default=375)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    
    # Relationships
    recipes: Mapped[List["Recipe"]] = relationship("Recipe", back_populates="profession")


class Item(Base):
    """Main items table with comprehensive WoW item attributes."""
    __tablename__ = "items"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Classification
    type_id: Mapped[int] = mapped_column(Integer, ForeignKey("item_types.id"), nullable=False)
    subtype_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("item_subtypes.id"), nullable=True)
    slot_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("item_slots.id"), nullable=True)
    
    # Level and requirements
    item_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    required_level: Mapped[int] = mapped_column(Integer, default=1)
    required_class: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # comma-separated
    required_race: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)   # comma-separated
    
    # Quality and rarity
    quality: Mapped[str] = mapped_column(String(20), default="common")  # poor, common, uncommon, rare, epic, legendary, artifact, heirloom
    
    # Item behavior
    bind_type: Mapped[str] = mapped_column(String(20), default="none")  # none, pickup, equip, use, quest, account
    unique_equipped: Mapped[bool] = mapped_column(Boolean, default=False)
    max_stack: Mapped[int] = mapped_column(Integer, default=1)
    
    # Pricing
    vendor_price_copper: Mapped[int] = mapped_column(Integer, default=0)
    
    # Item stats (JSON storage for flexibility)
    stats: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string
    
    # Special properties
    durability: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    charges: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    cooldown_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # External references
    external_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    external_source: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, onupdate=utc_now)
    
    # Relationships
    type: Mapped["ItemType"] = relationship("ItemType", back_populates="items")
    subtype: Mapped[Optional["ItemSubtype"]] = relationship("ItemSubtype", back_populates="items")
    slot: Mapped[Optional["ItemSlot"]] = relationship("ItemSlot", back_populates="items")
    vendor_items: Mapped[List["VendorItem"]] = relationship("VendorItem", back_populates="item")
    created_by_recipes: Mapped[List["Recipe"]] = relationship("Recipe", back_populates="creates_item")
    used_in_recipes: Mapped[List["RecipeIngredient"]] = relationship("RecipeIngredient", back_populates="ingredient_item")
    set_pieces: Mapped[List["ItemSetPiece"]] = relationship("ItemSetPiece", back_populates="item")
    
    @property
    def stats_dict(self) -> Dict[str, Any]:
        """Parse stats JSON string to dictionary."""
        if self.stats:
            try:
                return json.loads(self.stats)
            except json.JSONDecodeError:
                return {}
        return {}
    
    @stats_dict.setter
    def stats_dict(self, value: Dict[str, Any]) -> None:
        """Set stats from dictionary."""
        self.stats = json.dumps(value) if value else None
    
    @property
    def required_classes_list(self) -> List[str]:
        """Parse required_class string to list."""
        if self.required_class:
            return [cls.strip() for cls in self.required_class.split(",") if cls.strip()]
        return []
    
    @required_classes_list.setter
    def required_classes_list(self, value: List[str]) -> None:
        """Set required classes from list."""
        self.required_class = ", ".join(value) if value else None
    
    @property
    def required_races_list(self) -> List[str]:
        """Parse required_race string to list."""
        if self.required_race:
            return [race.strip() for race in self.required_race.split(",") if race.strip()]
        return []
    
    @required_races_list.setter
    def required_races_list(self, value: List[str]) -> None:
        """Set required races from list."""
        self.required_race = ", ".join(value) if value else None


class Vendor(Base):
    """NPCs that sell items with enhanced location data."""
    __tablename__ = "vendors"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    zone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    subzone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    faction: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # alliance, horde, neutral
    vendor_type: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)  # npc, guild, pvp, etc.
    coordinates: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # x,y coordinates
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    
    # Relationships
    vendor_items: Mapped[List["VendorItem"]] = relationship("VendorItem", back_populates="vendor")


class VendorItem(Base):
    """Items sold by vendors with enhanced requirements and availability."""
    __tablename__ = "vendor_items"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vendor_id: Mapped[int] = mapped_column(Integer, ForeignKey("vendors.id"), nullable=False)
    item_id: Mapped[int] = mapped_column(Integer, ForeignKey("items.id"), nullable=False)
    price_copper: Mapped[int] = mapped_column(Integer, nullable=False)
    stock_quantity: Mapped[int] = mapped_column(Integer, default=-1)  # -1 = unlimited
    required_reputation: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    required_faction: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    required_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    available_start_date: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)
    available_end_date: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    
    # Relationships
    vendor: Mapped["Vendor"] = relationship("Vendor", back_populates="vendor_items")
    item: Mapped["Item"] = relationship("Item", back_populates="vendor_items")
    
    __table_args__ = (
        UniqueConstraint("vendor_id", "item_id", name="uq_vendor_item"),
    )


class Recipe(Base):
    """Crafting recipes with comprehensive requirements and metadata."""
    __tablename__ = "recipes"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    profession_id: Mapped[int] = mapped_column(Integer, ForeignKey("professions.id"), nullable=False)
    creates_item_id: Mapped[int] = mapped_column(Integer, ForeignKey("items.id"), nullable=False)
    creates_quantity: Mapped[int] = mapped_column(Integer, default=1)
    required_skill_level: Mapped[int] = mapped_column(Integer, default=1)
    recipe_type: Mapped[str] = mapped_column(String(20), default="learned")  # learned, taught, discovered, quest
    recipe_difficulty: Mapped[str] = mapped_column(String(20), default="yellow")  # trivial, green, yellow, orange, red
    
    # Learning requirements
    teaches_spell_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    required_reputation: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    required_faction: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    required_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # External references
    external_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    external_source: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    
    # Relationships
    profession: Mapped["Profession"] = relationship("Profession", back_populates="recipes")
    creates_item: Mapped["Item"] = relationship("Item", back_populates="created_by_recipes")
    ingredients: Mapped[List["RecipeIngredient"]] = relationship("RecipeIngredient", back_populates="recipe", cascade="all, delete-orphan")


class RecipeIngredient(Base):
    """Ingredients required for recipes with support for optional reagents."""
    __tablename__ = "recipe_ingredients"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    recipe_id: Mapped[int] = mapped_column(Integer, ForeignKey("recipes.id"), nullable=False)
    ingredient_item_id: Mapped[int] = mapped_column(Integer, ForeignKey("items.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    is_optional: Mapped[bool] = mapped_column(Boolean, default=False)  # for optional reagents
    ingredient_group: Mapped[int] = mapped_column(Integer, default=1)  # for alternative ingredients
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    
    # Relationships
    recipe: Mapped["Recipe"] = relationship("Recipe", back_populates="ingredients")
    ingredient_item: Mapped["Item"] = relationship("Item", back_populates="used_in_recipes")
    
    __table_args__ = (
        UniqueConstraint("recipe_id", "ingredient_item_id", name="uq_recipe_ingredient"),
    )


class ItemSet(Base):
    """Item sets like Tier gear, dungeon sets, etc."""
    __tablename__ = "item_sets"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    set_type: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)  # tier, dungeon, pvp, crafted, etc.
    tier_level: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)  # T1, T2, T3, etc.
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    
    # Relationships
    pieces: Mapped[List["ItemSetPiece"]] = relationship("ItemSetPiece", back_populates="item_set", cascade="all, delete-orphan")
    bonuses: Mapped[List["ItemSetBonus"]] = relationship("ItemSetBonus", back_populates="item_set", cascade="all, delete-orphan")


class ItemSetPiece(Base):
    """Items that belong to equipment sets."""
    __tablename__ = "item_set_pieces"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    set_id: Mapped[int] = mapped_column(Integer, ForeignKey("item_sets.id"), nullable=False)
    item_id: Mapped[int] = mapped_column(Integer, ForeignKey("items.id"), nullable=False)
    piece_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # descriptive name like "Helmet", "Chestpiece"
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    
    # Relationships
    item_set: Mapped["ItemSet"] = relationship("ItemSet", back_populates="pieces")
    item: Mapped["Item"] = relationship("Item", back_populates="set_pieces")
    
    __table_args__ = (
        UniqueConstraint("set_id", "item_id", name="uq_item_set_piece"),
    )


class ItemSetBonus(Base):
    """Set bonuses for wearing multiple pieces of a set."""
    __tablename__ = "item_set_bonuses"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    set_id: Mapped[int] = mapped_column(Integer, ForeignKey("item_sets.id"), nullable=False)
    pieces_required: Mapped[int] = mapped_column(Integer, nullable=False)
    bonus_description: Mapped[str] = mapped_column(Text, nullable=False)
    bonus_stats: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON object with bonus stats
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    
    # Relationships
    item_set: Mapped["ItemSet"] = relationship("ItemSet", back_populates="bonuses")
    
    __table_args__ = (
        UniqueConstraint("set_id", "pieces_required", name="uq_item_set_bonus"),
    )
    
    @property
    def bonus_stats_dict(self) -> Dict[str, Any]:
        """Parse bonus_stats JSON string to dictionary."""
        if self.bonus_stats:
            try:
                return json.loads(self.bonus_stats)
            except json.JSONDecodeError:
                return {}
        return {}
    
    @bonus_stats_dict.setter
    def bonus_stats_dict(self, value: Dict[str, Any]) -> None:
        """Set bonus stats from dictionary."""
        self.bonus_stats = json.dumps(value) if value else None