"""
Common schemas and utilities for the WoW Items API.
"""
from typing import Optional, Any, List, Dict
from enum import Enum
from pydantic import BaseModel, Field

from turtle_db.config import settings


class ItemQuality(str, Enum):
    """Item quality levels."""
    POOR = "poor"
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


class BindType(str, Enum):
    """Item bind types."""
    NONE = "none"
    PICKUP = "pickup"
    EQUIP = "equip"
    USE = "use"


class Faction(str, Enum):
    """Character factions."""
    ALLIANCE = "alliance"
    HORDE = "horde"
    NEUTRAL = "neutral"


class Currency(BaseModel):
    """Currency representation in gold, silver, copper."""
    gold: int = Field(ge=0, description="Gold amount")
    silver: int = Field(ge=0, le=99, description="Silver amount (0-99)")
    copper: int = Field(ge=0, le=99, description="Copper amount (0-99)")
    
    @classmethod
    def from_copper(cls, total_copper: int) -> "Currency":
        """Convert total copper to gold/silver/copper breakdown."""
        if total_copper < 0:
            total_copper = 0
            
        gold = total_copper // settings.copper_per_gold
        remaining = total_copper % settings.copper_per_gold
        silver = remaining // settings.copper_per_silver
        copper = remaining % settings.copper_per_silver
        
        return cls(gold=gold, silver=silver, copper=copper)
    
    def to_copper(self) -> int:
        """Convert to total copper amount."""
        return (self.gold * settings.copper_per_gold + 
                self.silver * settings.copper_per_silver + 
                self.copper)


class APIResponse(BaseModel):
    """Standard API response wrapper."""
    success: bool = True
    data: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    message: Optional[str] = None


class APIError(BaseModel):
    """API error structure."""
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class PaginationParams(BaseModel):
    """Pagination parameters."""
    page: int = Field(ge=1, default=1, description="Page number (1-based)")
    limit: int = Field(
        ge=1, 
        le=settings.max_page_size, 
        default=settings.default_page_size,
        description=f"Items per page (1-{settings.max_page_size})"
    )
    
    @property
    def offset(self) -> int:
        """Calculate offset for database queries."""
        return (self.page - 1) * self.limit


class PaginationMeta(BaseModel):
    """Pagination metadata."""
    page: int
    limit: int
    total: int
    pages: int
    has_next: bool
    has_previous: bool


class PaginatedResponse(BaseModel):
    """Paginated response wrapper."""
    success: bool = True
    data: List[Any]
    pagination: PaginationMeta


# Reference data schemas
class ItemTypeBase(BaseModel):
    """Base item type schema."""
    name: str = Field(min_length=1, max_length=50)
    description: Optional[str] = None


class ItemTypeResponse(ItemTypeBase):
    """Item type response schema."""
    id: int
    
    class Config:
        from_attributes = True


class ItemSubtypeBase(BaseModel):
    """Base item subtype schema."""
    name: str = Field(min_length=1, max_length=50)
    description: Optional[str] = None


class ItemSubtypeResponse(ItemSubtypeBase):
    """Item subtype response schema."""
    id: int
    type: Optional[ItemTypeResponse] = None
    
    class Config:
        from_attributes = True


class ItemSlotBase(BaseModel):
    """Base item slot schema."""
    name: str = Field(min_length=1, max_length=30)
    description: Optional[str] = None


class ItemSlotResponse(ItemSlotBase):
    """Item slot response schema."""
    id: int
    
    class Config:
        from_attributes = True


class ProfessionBase(BaseModel):
    """Base profession schema."""
    name: str = Field(min_length=1, max_length=50)
    description: Optional[str] = None
    max_skill_level: int = Field(ge=1, le=450, default=375)


class ProfessionResponse(ProfessionBase):
    """Profession response schema."""
    id: int
    
    class Config:
        from_attributes = True