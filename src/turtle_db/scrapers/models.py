"""
Data transfer objects for scraped data.
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class ScrapedItem:
    """Represents an item scraped from external source."""
    name: str
    item_type: str
    subtype: Optional[str]
    slot: Optional[str]
    item_level: Optional[int]
    required_level: int
    quality: str
    description: Optional[str]
    crafting_spells: List[str]  # Spell IDs that create this item
    vendor_price_copper: int = 0
    bind_type: str = "none"
    max_stack: int = 1


@dataclass
class ScrapedRecipe:
    """Represents a recipe scraped from external source."""
    spell_id: str
    name: str
    profession: str
    required_skill: int
    ingredients: List[Tuple[str, int]]  # (ingredient_name, quantity)
    recipe_type: str = "learned"


@dataclass
class ScrapedIngredient:
    """Represents an ingredient within a recipe."""
    name: str
    quantity: int
    item_id: Optional[str] = None  # External item ID if available