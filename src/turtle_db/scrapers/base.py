"""
Abstract base scraper interface.
"""

from abc import ABC, abstractmethod
from typing import List

from .models import ScrapedItem, ScrapedRecipe


class BaseScraper(ABC):
    """Abstract base class for data scrapers."""

    @abstractmethod
    async def scrape_item(self, url: str) -> ScrapedItem:
        """Scrape item data from the given URL."""
        pass

    @abstractmethod
    async def scrape_recipe(self, spell_id: str) -> ScrapedRecipe:
        """Scrape recipe data for the given spell ID."""
        pass

    @abstractmethod
    def validate_url(self, url: str) -> bool:
        """Validate that the URL is supported by this scraper."""
        pass

    @abstractmethod
    def get_supported_domains(self) -> List[str]:
        """Return list of supported domains for this scraper."""
        pass

    async def cleanup(self) -> None:
        """Cleanup resources (override if needed)."""
        pass