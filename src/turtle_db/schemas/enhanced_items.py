"""
Enhanced Pydantic schemas for item-related endpoints with comprehensive WoW attributes.
"""
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator
import json

from turtle_db.schemas.common import (
    Currency, ItemQuality, BindType,
    ItemTypeResponse, ItemSubtypeResponse, ItemSlotResponse
)


class ItemStats(BaseModel):
    """Schema for item stats stored as JSON."""
    strength: Optional[int] = None
    agility: Optional[int] = None
    stamina: Optional[int] = None
    intellect: Optional[int] = None
    spirit: Optional[int] = None
    
    # Combat stats
    damage_min: Optional[int] = None
    damage_max: Optional[int] = None
    speed: Optional[float] = None
    dps: Optional[float] = None
    
    # Resistances
    armor: Optional[int] = None
    fire_resistance: Optional[int] = None
    nature_resistance: Optional[int] = None
    frost_resistance: Optional[int] = None
    shadow_resistance: Optional[int] = None
    arcane_resistance: Optional[int] = None
    
    # Other stats
    additional_stats: Optional[Dict[str, Union[int, float, str]]] = None
    
    class Config:
        from_attributes = True


class EnhancedItemCreate(BaseModel):
    """Enhanced schema for creating a new item with all WoW attributes."""
    name: str = Field(min_length=1, max_length=100, description="Item name")
    description: Optional[str] = Field(None, description="Item description")
    type_name: str = Field(description="Item type name (e.g., 'armor')")
    subtype_name: Optional[str] = Field(None, description="Item subtype name (e.g., 'plate')")
    slot_name: Optional[str] = Field(None, description="Item slot name (e.g., 'feet')")
    
    # Level and requirements
    item_level: Optional[int] = Field(None, ge=1, le=100, description="Item level")
    required_level: int = Field(1, ge=1, le=80, description="Required character level")
    required_classes: Optional[List[str]] = Field(None, description="Required classes (comma-separated)")
    required_races: Optional[List[str]] = Field(None, description="Required races (comma-separated)")
    
    # Quality and behavior
    quality: ItemQuality = Field(ItemQuality.COMMON, description="Item quality")
    bind_type: BindType = Field(BindType.NONE, description="Item bind type")
    unique_equipped: bool = Field(False, description="Whether item is unique equipped")
    max_stack: int = Field(1, ge=1, le=200, description="Maximum stack size")
    
    # Pricing
    vendor_price: Optional[Currency] = Field(None, description="Vendor sell price")
    
    # Item stats
    stats: Optional[ItemStats] = Field(None, description="Item stats and bonuses")
    
    # Special properties
    durability: Optional[int] = Field(None, ge=1, description="Item durability")
    charges: Optional[int] = Field(None, ge=1, description="Number of charges")
    cooldown_seconds: Optional[int] = Field(None, ge=0, description="Use cooldown in seconds")
    
    # External references
    external_id: Optional[int] = Field(None, description="External database ID")
    external_source: Optional[str] = Field(None, max_length=50, description="External data source")


class EnhancedItemUpdate(BaseModel):
    """Enhanced schema for updating an existing item."""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Item name")
    description: Optional[str] = Field(None, description="Item description")
    
    # Level and requirements
    item_level: Optional[int] = Field(None, ge=1, le=100, description="Item level")
    required_level: Optional[int] = Field(None, ge=1, le=80, description="Required character level")
    required_classes: Optional[List[str]] = Field(None, description="Required classes")
    required_races: Optional[List[str]] = Field(None, description="Required races")
    
    # Quality and behavior
    quality: Optional[ItemQuality] = Field(None, description="Item quality")
    bind_type: Optional[BindType] = Field(None, description="Item bind type")
    unique_equipped: Optional[bool] = Field(None, description="Whether item is unique equipped")
    max_stack: Optional[int] = Field(None, ge=1, le=200, description="Maximum stack size")
    
    # Pricing
    vendor_price: Optional[Currency] = Field(None, description="Vendor sell price")
    
    # Item stats
    stats: Optional[ItemStats] = Field(None, description="Item stats and bonuses")
    
    # Special properties
    durability: Optional[int] = Field(None, ge=1, description="Item durability")
    charges: Optional[int] = Field(None, ge=1, description="Number of charges")
    cooldown_seconds: Optional[int] = Field(None, ge=0, description="Use cooldown in seconds")
    
    # External references
    external_id: Optional[int] = Field(None, description="External database ID")
    external_source: Optional[str] = Field(None, max_length=50, description="External data source")


class EnhancedItemResponse(BaseModel):
    """Enhanced schema for item responses with comprehensive attributes."""
    id: int
    name: str
    description: Optional[str]
    type: ItemTypeResponse
    subtype: Optional[ItemSubtypeResponse]
    slot: Optional[ItemSlotResponse]
    
    # Level and requirements
    item_level: Optional[int]
    required_level: int
    required_classes: Optional[List[str]] = None
    required_races: Optional[List[str]] = None
    
    # Quality and behavior
    quality: str
    bind_type: str
    unique_equipped: bool = False
    max_stack: int
    
    # Pricing
    vendor_price_copper: int
    vendor_price: Optional[Currency] = None  # Computed field
    
    # Item stats
    stats: Optional[ItemStats] = None
    
    # Special properties
    durability: Optional[int] = None
    charges: Optional[int] = None
    cooldown_seconds: Optional[int] = None
    
    # External references
    external_id: Optional[int] = None
    external_source: Optional[str] = None
    
    # Computed fields
    pricing: Optional[dict] = None  # Vendor pricing info
    crafting: Optional[dict] = None  # Recipe info
    set_info: Optional[dict] = None  # Set information
    
    created_at: datetime
    updated_at: datetime
    
    @validator('vendor_price', always=True)
    def compute_vendor_price(cls, v, values):
        """Compute currency display from copper value."""
        copper = values.get('vendor_price_copper', 0)
        if copper > 0:
            return Currency.from_copper(copper)
        return None
    
    @validator('required_classes', 'required_races', pre=True)
    def parse_string_list(cls, v):
        """Parse comma-separated strings to lists."""
        if isinstance(v, str) and v:
            return [item.strip() for item in v.split(',') if item.strip()]
        return v
    
    @validator('stats', pre=True)
    def parse_stats(cls, v):
        """Parse JSON stats string to ItemStats object."""
        if isinstance(v, str) and v:
            try:
                stats_dict = json.loads(v)
                return ItemStats(**stats_dict) if stats_dict else None
            except (json.JSONDecodeError, TypeError):
                return None
        return v
    
    class Config:
        from_attributes = True


class EnhancedItemFilter(BaseModel):
    """Enhanced query parameters for filtering items."""
    # Basic filters
    type_name: Optional[str] = Field(None, description="Filter by item type name")
    subtype_name: Optional[str] = Field(None, description="Filter by item subtype name")
    slot_name: Optional[str] = Field(None, description="Filter by item slot name")
    quality: Optional[ItemQuality] = Field(None, description="Filter by item quality")
    
    # Level filters
    level_min: Optional[int] = Field(None, ge=1, le=100, description="Minimum item level")
    level_max: Optional[int] = Field(None, ge=1, le=100, description="Maximum item level")
    required_level_min: Optional[int] = Field(None, ge=1, le=80, description="Minimum required level")
    required_level_max: Optional[int] = Field(None, ge=1, le=80, description="Maximum required level")
    
    # Class/Race filters
    usable_by_class: Optional[str] = Field(None, description="Filter by class that can use the item")
    usable_by_race: Optional[str] = Field(None, description="Filter by race that can use the item")
    
    # Behavior filters
    bind_type: Optional[BindType] = Field(None, description="Filter by bind type")
    unique_equipped: Optional[bool] = Field(None, description="Filter unique equipped items")
    
    # Availability filters
    vendor_sellable: Optional[bool] = Field(None, description="Filter items sold by vendors")
    craftable: Optional[bool] = Field(None, description="Filter craftable items")
    has_charges: Optional[bool] = Field(None, description="Filter items with charges")
    has_durability: Optional[bool] = Field(None, description="Filter items with durability")
    has_cooldown: Optional[bool] = Field(None, description="Filter items with cooldowns")
    
    # External data filters
    external_source: Optional[str] = Field(None, description="Filter by external data source")
    has_external_id: Optional[bool] = Field(None, description="Filter items with external references")
    
    # Search
    search: Optional[str] = Field(None, min_length=1, max_length=100, description="Search in item name/description")


class ItemSetResponse(BaseModel):
    """Schema for item set responses."""
    id: int
    name: str
    description: Optional[str]
    set_type: Optional[str]
    tier_level: Optional[str]
    pieces: List[dict]  # List of set pieces
    bonuses: List[dict]  # List of set bonuses
    created_at: datetime
    
    class Config:
        from_attributes = True


class ItemSetPieceResponse(BaseModel):
    """Schema for item set piece responses."""
    id: int
    set_id: int
    item_id: int
    piece_name: Optional[str]
    sort_order: int
    item: Optional[EnhancedItemResponse] = None
    
    class Config:
        from_attributes = True


class ItemSetBonusResponse(BaseModel):
    """Schema for item set bonus responses."""
    id: int
    set_id: int
    pieces_required: int
    bonus_description: str
    bonus_stats: Optional[Dict[str, Any]] = None
    
    @validator('bonus_stats', pre=True)
    def parse_bonus_stats(cls, v):
        """Parse JSON bonus stats string."""
        if isinstance(v, str) and v:
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return None
        return v
    
    class Config:
        from_attributes = True


class EnhancedItemListResponse(BaseModel):
    """Enhanced response schema for listing items."""
    items: List[EnhancedItemResponse]
    total: int
    page: int
    limit: int
    pages: int
    filters_applied: Optional[Dict[str, Any]] = None