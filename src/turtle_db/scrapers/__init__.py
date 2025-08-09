"""
Web scraping components for importing data from external sources.
"""

from .base import BaseScraper
from .models import ScrapedItem, ScrapedRecipe
from .turtle_wow import TurtleWowScraper

__all__ = ["BaseScraper", "ScrapedItem", "ScrapedRecipe", "TurtleWowScraper"]