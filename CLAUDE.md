# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

turtle-db is a World of Warcraft Items API built with FastAPI and SQLite. It provides CRUD operations for game items, crafting recipes, vendors, and professions with hierarchical item categorization.

## Development Commands

**Package Management & Environment:**
```bash
# Install dependencies and set up environment
uv sync

# Install the package in development mode
uv pip install -e .

# Run the FastAPI development server
uvicorn turtle_db.main:app --reload --host 0.0.0.0 --port 8000

# Run via CLI tool (once implemented)
turtle-db
```

**Database Setup:**
```bash
# Initialize database with schema
python -c "from turtle_db.database.connection import create_tables; create_tables()"

# Load sample data
sqlite3 data/turtle_db.sqlite < docs/database_schema.sql
```

**Testing & Quality:**
```bash
# Run tests
pytest

# Run with coverage
pytest --cov=turtle_db

# Type checking
mypy src/turtle_db
```

## Code Architecture

**Domain Model:**
- **Items**: Core game items with type/subtype/slot hierarchy (armor→plate→feet)
- **Recipes**: Crafting instructions with ingredients and profession requirements
- **Vendors**: NPCs selling items with gold/silver/copper pricing
- **Professions**: Crafting specializations (blacksmithing, tailoring, etc.)
- **Imports**: Web scraping system for external data sources (Turtle-WoW database)

**API Structure:**
- `/api/v1/items` - Item CRUD with filtering by type, quality, level
- `/api/v1/recipes` - Recipe CRUD with profession and ingredient management
- `/api/v1/vendors` - Vendor CRUD with item pricing
- `/api/v1/professions` - Profession management
- `/api/v1/imports` - Import items and recipes from external sources

**Technical Stack:**
- **FastAPI**: Async web framework with automatic OpenAPI docs
- **SQLAlchemy**: Async ORM with SQLite backend
- **Pydantic**: Request/response validation and serialization
- **uv**: Modern Python package management
- **httpx**: Async HTTP client for web scraping
- **BeautifulSoup4**: HTML parsing for data extraction

## Key Design Patterns

**Currency System**: All prices stored as copper integers with utility functions for gold/silver/copper conversion

**Hierarchical Items**: Items have type→subtype→slot relationships (e.g., armor→plate→feet)

**Recipe Dependencies**: Recipes link to professions and have ingredient lists with quantities

**Service Layer**: Business logic separated from API endpoints for complex operations like recipe cost calculation

**Import System**: Web scraping architecture for importing items and recipes from external sources with data validation and error handling

## Development Guidelines

- Use async/await throughout the stack
- Follow the layered architecture: API → Service → Database
- Validate input with Pydantic schemas
- Handle currency as copper integers, display as gold/silver/copper
- Use SQLAlchemy relationships for efficient data loading
- Implement proper error handling and retry logic for external API calls
- Use data mappers to transform external data to internal models
- Reference design documents in `docs/` for detailed specifications

## Import System Usage

**Import Item from Turtle-WoW Database:**
```bash
curl -X POST "http://localhost:8000/api/v1/imports/item" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://database.turtle-wow.org/?item=12640",
    "import_recipes": true
  }'
```

**Import Flow:**
1. Validate Turtle-WoW URL format
2. Scrape item data (name, type, subtype, slot, etc.)
3. Find crafting spells in `tab-created-by` div
4. Scrape recipe data for each spell
5. Map external data to database models
6. Create item and associated recipes with ingredients

**Supported Sources:**
- Turtle-WoW Database (database.turtle-wow.org)

**Error Handling:**
- Invalid URLs return 400 Bad Request
- Duplicate items return 409 Conflict
- Source unavailable returns 503 Service Unavailable
- Partial failures include warnings in response