"""
Turtle-WoW database scraper implementation.
"""

import re
import logging
from typing import List
from urllib.parse import urlparse, parse_qs

import httpx
from bs4 import BeautifulSoup, Tag
from bs4.element import NavigableString

from .base import BaseScraper
from .models import ScrapedItem, ScrapedRecipe

logger = logging.getLogger(__name__)


class TurtleWowScraper(BaseScraper):
    """Scraper for Turtle-WoW database (database.turtle-wow.org)."""

    BASE_URL = "https://database.turtle-wow.org"
    SUPPORTED_DOMAINS = ["database.turtle-wow.org"]

    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                'User-Agent': 'turtle-db/1.0.0 (+https://github.com/madskristensen/turtle-db)'
            }
        )

    def get_supported_domains(self) -> List[str]:
        """Return list of supported domains."""
        return self.SUPPORTED_DOMAINS

    def validate_url(self, url: str) -> bool:
        """Validate Turtle-WoW item URL format."""
        try:
            parsed = urlparse(url)
            if parsed.netloc not in self.SUPPORTED_DOMAINS:
                return False
            
            query_params = parse_qs(parsed.query)
            return "item" in query_params and len(query_params["item"]) > 0
        except Exception as e:
            logger.warning(f"URL validation failed for {url}: {e}")
            return False

    async def scrape_item(self, url: str) -> ScrapedItem:
        """Scrape item data from Turtle-WoW database."""
        logger.info(f"Scraping item from URL: {url}")
        
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Extract item name from page title or header
            name = self._extract_item_name(soup)
            logger.debug(f"Extracted item name: {name}")
            
            # Extract item details from the main content
            item_details = self._extract_item_details(soup)
            logger.debug(f"Extracted item details: {item_details}")
            
            # Find crafting spells in tab-created-by div
            crafting_spells = self._extract_crafting_spells(soup)
            logger.debug(f"Found {len(crafting_spells)} crafting spells")
            
            return ScrapedItem(
                name=name,
                item_type=item_details.get('type', 'miscellaneous'),
                subtype=item_details.get('subtype'),
                slot=item_details.get('slot'),
                item_level=item_details.get('item_level'),
                required_level=item_details.get('required_level', 1),
                quality=item_details.get('quality', 'common'),
                description=item_details.get('description'),
                crafting_spells=crafting_spells,
                vendor_price_copper=item_details.get('vendor_price_copper', 0),
                bind_type=item_details.get('bind_type', 'none'),
                max_stack=item_details.get('max_stack', 1)
            )
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error scraping item from {url}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error scraping item from {url}: {e}")
            raise

    async def scrape_recipe(self, spell_id: str) -> ScrapedRecipe:
        """Scrape recipe data for a specific spell."""
        url = f"{self.BASE_URL}/?spell={spell_id}"
        logger.info(f"Scraping recipe from spell ID: {spell_id}")
        
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Extract recipe details
            recipe_data = self._extract_recipe_details(soup)
            logger.debug(f"Extracted recipe data: {recipe_data}")
            
            return ScrapedRecipe(
                spell_id=spell_id,
                name=recipe_data.get('name', f'Recipe {spell_id}'),
                profession=recipe_data.get('profession', 'Unknown'),
                required_skill=recipe_data.get('required_skill', 1),
                ingredients=recipe_data.get('ingredients', [])
            )
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error scraping recipe {spell_id}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error scraping recipe {spell_id}: {e}")
            raise

    def _extract_item_name(self, soup: BeautifulSoup) -> str:
        """Extract item name from the page."""
        # Try main heading first
        heading = soup.find('h1')
        if heading:
            name = heading.get_text(strip=True)
            if name:
                return name
        
        # Try page title
        title = soup.find('title')
        if title:
            title_text = title.get_text(strip=True)
            # Remove common suffixes from title
            name = re.sub(r' - Turtle WoW Database$', '', title_text)
            if name and name != title_text:
                return name
        
        # Fallback to any prominent text
        main_content = soup.find('div', {'class': 'main-content'}) or soup.find('main')
        if main_content and isinstance(main_content, Tag):
            # Look for item name patterns
            name_candidates = main_content.find_all(text=True)
            for candidate in name_candidates:
                if isinstance(candidate, NavigableString):
                    candidate_text = candidate.strip()
                    if candidate_text and len(candidate_text) > 3 and len(candidate_text) < 100:
                        return candidate_text
        
        return "Unknown Item"

    def _extract_item_details(self, soup: BeautifulSoup) -> dict:
        """Extract item type, subtype, slot, quality, etc."""
        details = {}
        
        # Look for item info tables or sections
        info_table = soup.find('table', {'class': 'item-info'}) or soup.find('div', {'class': 'item-details'})
        
        if info_table and isinstance(info_table, Tag):
            rows = info_table.find_all('tr') if info_table.name == 'table' else info_table.find_all('div')
            
            for row in rows:
                text = row.get_text(strip=True).lower()
                
                # Extract item type
                if 'armor' in text:
                    details['type'] = 'armor'
                    if 'plate' in text:
                        details['subtype'] = 'plate'
                    elif 'mail' in text:
                        details['subtype'] = 'mail'
                    elif 'leather' in text:
                        details['subtype'] = 'leather'
                    elif 'cloth' in text:
                        details['subtype'] = 'cloth'
                elif 'weapon' in text:
                    details['type'] = 'weapon'
                
                # Extract slot
                slot_patterns = {
                    'head': ['head', 'helmet', 'hat', 'crown'],
                    'chest': ['chest', 'robe', 'tunic'],
                    'feet': ['feet', 'boots', 'shoes'],
                    'hands': ['hands', 'gloves', 'gauntlets'],
                    'legs': ['legs', 'pants', 'leggings'],
                    'shoulders': ['shoulders', 'pauldrons'],
                    'waist': ['waist', 'belt'],
                    'wrist': ['wrist', 'bracer']
                }
                
                for slot, keywords in slot_patterns.items():
                    if any(keyword in text for keyword in keywords):
                        details['slot'] = slot
                        break
                
                # Extract quality
                quality_patterns = ['poor', 'common', 'uncommon', 'rare', 'epic', 'legendary']
                for quality in quality_patterns:
                    if quality in text:
                        details['quality'] = quality
                        break
                
                # Extract levels
                level_match = re.search(r'level (\d+)', text)
                if level_match:
                    details['required_level'] = int(level_match.group(1))
                
                item_level_match = re.search(r'item level (\d+)', text)
                if item_level_match:
                    details['item_level'] = int(item_level_match.group(1))
        
        # Default fallbacks
        if 'type' not in details:
            details['type'] = 'miscellaneous'
        
        return details

    def _extract_crafting_spells(self, soup: BeautifulSoup) -> List[str]:
        """Extract crafting spell IDs from tab-created-by div."""
        spell_ids = []
        
        # Find the tab-created-by div
        tab_div = soup.find('div', {'id': 'tab-created-by'})
        if not tab_div:
            # Try alternative selectors
            tab_div = soup.find('div', {'class': 'created-by'}) or soup.find('section', {'id': 'created-by'})
        
        if tab_div and isinstance(tab_div, Tag):
            # Find all spell links
            spell_links = tab_div.find_all('a', href=re.compile(r'\?spell=(\d+)'))
            
            for link in spell_links:
                if isinstance(link, Tag):
                    href = link.get('href')
                    if href and isinstance(href, str):
                        match = re.search(r'spell=(\d+)', href)
                        if match:
                            spell_id = match.group(1)
                            spell_ids.append(spell_id)
                            logger.debug(f"Found crafting spell: {spell_id}")
        
        return spell_ids

    def _extract_recipe_details(self, soup: BeautifulSoup) -> dict:
        """Extract recipe information from spell page."""
        recipe_data = {
            'ingredients': [],
            'profession': 'Unknown',
            'required_skill': 1,
            'name': 'Unknown Recipe'
        }
        
        # Extract spell name
        heading = soup.find('h1')
        if heading:
            recipe_data['name'] = heading.get_text(strip=True)
        
        # Look for profession info
        profession_patterns = {
            'blacksmithing': ['blacksmithing', 'blacksmith'],
            'tailoring': ['tailoring', 'tailor'],
            'leatherworking': ['leatherworking', 'leatherwork'],
            'enchanting': ['enchanting'],
            'engineering': ['engineering', 'engineer'],
            'alchemy': ['alchemy', 'alchemist'],
            'cooking': ['cooking', 'cook'],
            'first aid': ['first aid'],
            'mining': ['mining'],
            'herbalism': ['herbalism']
        }
        
        page_text = soup.get_text().lower()
        for profession, keywords in profession_patterns.items():
            if any(keyword in page_text for keyword in keywords):
                recipe_data['profession'] = profession
                break
        
        # Extract required skill level
        skill_match = re.search(r'requires? .* \((\d+)\)', page_text)
        if skill_match:
            recipe_data['required_skill'] = int(skill_match.group(1))
        
        # Extract ingredients from reagents table
        reagents_table = soup.find('table', {'class': 'reagents'}) or soup.find('div', {'class': 'reagents'})
        if reagents_table and isinstance(reagents_table, Tag):
            ingredient_rows = reagents_table.find_all('tr')[1:] if reagents_table.name == 'table' else reagents_table.find_all('div')
            
            for row in ingredient_rows:
                # Extract ingredient name and quantity
                text = row.get_text(strip=True)
                
                # Look for quantity patterns like "2x Iron Bar" or "Iron Bar (2)"
                quantity_match = re.search(r'(\d+)x?\s*(.+)', text) or re.search(r'(.+)\s*\((\d+)\)', text)
                
                if quantity_match:
                    if text.startswith(quantity_match.group(1)) and quantity_match.group(1).isdigit():
                        quantity = int(quantity_match.group(1))
                        name = quantity_match.group(2).strip()
                    else:
                        name = quantity_match.group(1).strip()
                        quantity = int(quantity_match.group(2))
                    
                    recipe_data['ingredients'].append((name, quantity))
                    logger.debug(f"Found ingredient: {name} x{quantity}")
        
        return recipe_data

    async def cleanup(self) -> None:
        """Cleanup HTTP client resources."""
        await self.client.aclose()