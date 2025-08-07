"""
Pydantic schemas for item-related endpoints.
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

from turtle_db.schemas.common import (
    Currency, ItemQuality, BindType,
    ItemTypeResponse, ItemSubtypeResponse, ItemSlotResponse
)


class ItemCreate(BaseModel):
    """Schema for creating a new item."""
    name: str = Field(min_length=1, max_length=100, description="Item name")
    description: Optional[str] = Field(None, description="Item description")
    type_name: str = Field(description="Item type name (e.g., 'armor')")
    subtype_name: Optional[str] = Field(None, description="Item subtype name (e.g., 'plate')")
    slot_name: Optional[str] = Field(None, description="Item slot name (e.g., 'feet')")
    item_level: Optional[int] = Field(None, ge=1, le=100, description="Item level")
    required_level: int = Field(1, ge=1, le=80, description="Required character level")
    quality: ItemQuality = Field(ItemQuality.COMMON, description="Item quality")
    bind_type: BindType = Field(BindType.NONE, description="Item bind type")
    max_stack: int = Field(1, ge=1, le=200, description="Maximum stack size")
    vendor_price: Optional[Currency] = Field(None, description="Vendor sell price")


class ItemUpdate(BaseModel):
    """Schema for updating an existing item."""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Item name")
    description: Optional[str] = Field(None, description="Item description")
    item_level: Optional[int] = Field(None, ge=1, le=100, description="Item level")
    required_level: Optional[int] = Field(None, ge=1, le=80, description="Required character level")
    quality: Optional[ItemQuality] = Field(None, description="Item quality")
    bind_type: Optional[BindType] = Field(None, description="Item bind type")
    max_stack: Optional[int] = Field(None, ge=1, le=200, description="Maximum stack size")
    vendor_price: Optional[Currency] = Field(None, description="Vendor sell price")


class ItemResponse(BaseModel):
    """Schema for item responses."""
    id: int
    name: str
    description: Optional[str]
    type: ItemTypeResponse
    subtype: Optional[ItemSubtypeResponse]
    slot: Optional[ItemSlotResponse]
    item_level: Optional[int]
    required_level: int
    quality: str
    bind_type: str
    max_stack: int
    pricing: Optional[dict] = None  # Computed field for vendor pricing
    crafting: Optional[dict] = None  # Computed field for recipe info
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ItemFilter(BaseModel):
    """Query parameters for filtering items."""
    type_name: Optional[str] = Field(None, description="Filter by item type name")
    subtype_name: Optional[str] = Field(None, description="Filter by item subtype name")
    slot_name: Optional[str] = Field(None, description="Filter by item slot name")
    quality: Optional[ItemQuality] = Field(None, description="Filter by item quality")
    level_min: Optional[int] = Field(None, ge=1, le=100, description="Minimum item level")
    level_max: Optional[int] = Field(None, ge=1, le=100, description="Maximum item level")
    required_level_min: Optional[int] = Field(None, ge=1, le=80, description="Minimum required level")
    required_level_max: Optional[int] = Field(None, ge=1, le=80, description="Maximum required level")
    vendor_sellable: Optional[bool] = Field(None, description="Filter items sold by vendors")
    craftable: Optional[bool] = Field(None, description="Filter craftable items")
    search: Optional[str] = Field(None, min_length=1, max_length=100, description="Search in item name/description")


class ItemListResponse(BaseModel):
    """Response schema for listing items."""
    items: List[ItemResponse]
    total: int
    page: int
    limit: int
    pages: int