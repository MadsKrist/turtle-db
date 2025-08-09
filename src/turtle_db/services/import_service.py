"""
Import orchestration service for ingesting data from external sources.
"""

import asyncio
import logging
from typing import List, Dict, Any
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx

from turtle_db.scrapers import TurtleWowScraper, ScrapedRecipe
from turtle_db.services.data_mapper import DataMapper
from turtle_db.services.items import ItemService
from turtle_db.database.models import Item, Recipe, RecipeIngredient
from turtle_db.utils.exceptions import (
    ImportSourceError, ImportDuplicateError
)

logger = logging.getLogger(__name__)


@dataclass
class ImportResult:
    """Result of an item import operation."""
    item_id: int
    item_name: str
    recipes_imported: int
    warnings: List[str]


class ImportService:
    """Orchestrates the item import process from external sources."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.scraper = TurtleWowScraper()
        self.mapper = DataMapper(db)
        self.item_service = ItemService(db)
    
    def validate_source_url(self, url: str) -> bool:
        """Validate that URL is from a supported source."""
        return self.scraper.validate_url(url)
    
    async def import_item_from_url(
        self, 
        url: str, 
        import_recipes: bool = True
    ) -> ImportResult:
        """Main import orchestration method."""
        logger.info(f"Starting import from URL: {url}")
        
        try:
            # 1. Scrape item data with retry
            scraped_item = await self._scrape_item_with_retry(url)
            logger.info(f"Successfully scraped item: {scraped_item.name}")
            
            # 2. Check for duplicates
            await self._check_duplicate_item(scraped_item.name)
            
            # 3. Map and create item
            item_data = await self.mapper.map_item(scraped_item)
            item = await self._create_item(item_data)
            logger.info(f"Created item with ID: {item.id}")
            
            # 4. Import recipes if requested
            recipes_count = 0
            warnings = []
            
            if import_recipes and scraped_item.crafting_spells:
                logger.info(f"Importing {len(scraped_item.crafting_spells)} recipes")
                recipes_count, recipe_warnings = await self._import_recipes(
                    scraped_item.crafting_spells, 
                    item.id
                )
                warnings.extend(recipe_warnings)
            
            # 5. Commit transaction
            await self.db.commit()
            
            result = ImportResult(
                item_id=item.id,
                item_name=item.name,
                recipes_imported=recipes_count,
                warnings=warnings
            )
            
            logger.info(f"Import completed successfully: {result}")
            return result
            
        except Exception as e:
            # Rollback transaction on any error
            await self.db.rollback()
            logger.error(f"Import failed, transaction rolled back: {e}")
            raise
    
    async def _scrape_item_with_retry(self, url: str, max_retries: int = 3):
        """Scrape item data with exponential backoff retry."""
        last_error = None
        
        for attempt in range(max_retries):
            try:
                logger.debug(f"Scraping attempt {attempt + 1}/{max_retries}")
                return await self.scraper.scrape_item(url)
                
            except httpx.HTTPError as e:
                last_error = e
                if attempt == max_retries - 1:
                    break
                    
                # Exponential backoff with jitter
                delay = (2 ** attempt) + (attempt * 0.1)
                logger.warning(f"Scraping failed, retrying in {delay}s: {e}")
                await asyncio.sleep(delay)
            
            except Exception as e:
                # Non-HTTP errors are not retryable
                logger.error(f"Non-retryable scraping error: {e}")
                raise ImportSourceError(f"Failed to scrape data from {url}: {str(e)}")
        
        # All retries exhausted
        raise ImportSourceError(f"Failed to access {url} after {max_retries} attempts: {last_error}")
    
    async def _check_duplicate_item(self, item_name: str):
        """Check if item already exists in database."""
        existing = await self.item_service.get_item_by_name(item_name)
        if existing:
            logger.warning(f"Duplicate item detected: {item_name}")
            raise ImportDuplicateError(item_name)
    
    async def _create_item(self, item_data: Dict[str, Any]) -> Item:
        """Create item from mapped data."""
        item = Item(**item_data)
        self.db.add(item)
        await self.db.flush()  # Get ID without committing
        await self.db.refresh(item)
        
        logger.debug(f"Created item: {item.name} (ID: {item.id})")
        return item
    
    async def _import_recipes(
        self, 
        spell_ids: List[str], 
        item_id: int
    ) -> tuple[int, List[str]]:
        """Import all recipes for the item."""
        recipes_imported = 0
        warnings = []
        
        for spell_id in spell_ids:
            try:
                logger.debug(f"Importing recipe for spell: {spell_id}")
                
                # Scrape recipe data with retry
                scraped_recipe = await self._scrape_recipe_with_retry(spell_id)
                
                # Map recipe data
                recipe_data = await self.mapper.map_recipe(scraped_recipe, item_id)
                
                # Create recipe and ingredients
                await self._create_recipe_with_ingredients(recipe_data, scraped_recipe)
                recipes_imported += 1
                
                logger.debug(f"Successfully imported recipe: {scraped_recipe.name}")
                
            except Exception as e:
                error_msg = f"Failed to import recipe {spell_id}: {str(e)}"
                logger.warning(error_msg)
                warnings.append(error_msg)
        
        logger.info(f"Imported {recipes_imported}/{len(spell_ids)} recipes")
        return recipes_imported, warnings
    
    async def _scrape_recipe_with_retry(self, spell_id: str, max_retries: int = 3) -> ScrapedRecipe:
        """Scrape recipe data with retry logic."""
        last_error = None
        
        for attempt in range(max_retries):
            try:
                return await self.scraper.scrape_recipe(spell_id)
                
            except httpx.HTTPError as e:
                last_error = e
                if attempt == max_retries - 1:
                    break
                    
                delay = (2 ** attempt) + (attempt * 0.1)
                logger.debug(f"Recipe scraping failed, retrying in {delay}s: {e}")
                await asyncio.sleep(delay)
            
            except Exception as e:
                logger.error(f"Non-retryable recipe scraping error: {e}")
                raise
        
        # All retries exhausted
        raise ImportSourceError(f"Failed to scrape recipe {spell_id} after {max_retries} attempts: {last_error}")
    
    async def _create_recipe_with_ingredients(
        self, 
        recipe_data: Dict[str, Any], 
        scraped_recipe: ScrapedRecipe
    ):
        """Create recipe and its ingredients."""
        
        # Check if recipe already exists
        existing_recipe_query = select(Recipe).where(
            Recipe.name == recipe_data['name'],
            Recipe.creates_item_id == recipe_data['creates_item_id']
        )
        result = await self.db.execute(existing_recipe_query)
        existing_recipe = result.scalar_one_or_none()
        
        if existing_recipe:
            logger.debug(f"Recipe already exists, skipping: {recipe_data['name']}")
            return existing_recipe
        
        # Create recipe
        recipe = Recipe(**recipe_data)
        self.db.add(recipe)
        await self.db.flush()  # Get ID without committing
        
        # Create ingredients
        for ingredient_name, quantity in scraped_recipe.ingredients:
            try:
                # Try to find existing item for ingredient
                ingredient_item = await self.item_service.get_item_by_name(ingredient_name)
                
                if ingredient_item:
                    ingredient = RecipeIngredient(
                        recipe_id=recipe.id,
                        ingredient_item_id=ingredient_item.id,
                        quantity=quantity
                    )
                    self.db.add(ingredient)
                    logger.debug(f"Added ingredient: {ingredient_name} x{quantity}")
                else:
                    logger.warning(f"Ingredient item not found: {ingredient_name}, skipping")
                    
            except Exception as e:
                logger.warning(f"Failed to add ingredient {ingredient_name}: {e}")
        
        await self.db.flush()
        logger.debug(f"Created recipe with {len(scraped_recipe.ingredients)} ingredients")
        return recipe
    
    async def cleanup(self):
        """Cleanup resources."""
        try:
            await self.scraper.cleanup()
        except Exception as e:
            logger.warning(f"Error during scraper cleanup: {e}")
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit with cleanup."""
        await self.cleanup()