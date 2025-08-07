# Project Structure

## Recommended Directory Layout
```
turtle-db/
├── src/
│   └── turtle_db/
│       ├── __init__.py                 # Main entry point
│       ├── main.py                     # FastAPI application
│       ├── config.py                   # Configuration management
│       ├── database/
│       │   ├── __init__.py
│       │   ├── connection.py           # Database connection setup
│       │   ├── models.py               # SQLAlchemy ORM models
│       │   └── migrations/             # Database migration scripts
│       ├── api/
│       │   ├── __init__.py
│       │   ├── deps.py                 # Dependencies (DB session, etc.)
│       │   └── v1/
│       │       ├── __init__.py
│       │       ├── router.py           # Main API router
│       │       └── endpoints/
│       │           ├── __init__.py
│       │           ├── items.py        # Items CRUD endpoints
│       │           ├── recipes.py      # Recipes CRUD endpoints
│       │           ├── vendors.py      # Vendors CRUD endpoints
│       │           ├── professions.py  # Professions CRUD endpoints
│       │           └── reference.py    # Reference data endpoints
│       ├── schemas/
│       │   ├── __init__.py
│       │   ├── items.py                # Item Pydantic models
│       │   ├── recipes.py              # Recipe Pydantic models
│       │   ├── vendors.py              # Vendor Pydantic models
│       │   ├── professions.py          # Profession Pydantic models
│       │   └── common.py               # Common schemas and responses
│       ├── services/
│       │   ├── __init__.py
│       │   ├── items.py                # Items business logic
│       │   ├── recipes.py              # Recipe business logic
│       │   ├── vendors.py              # Vendor business logic
│       │   └── professions.py          # Profession business logic
│       └── utils/
│           ├── __init__.py
│           ├── currency.py             # Gold/silver/copper utilities
│           └── exceptions.py           # Custom exceptions
├── tests/
│   ├── __init__.py
│   ├── conftest.py                     # Pytest configuration
│   ├── test_api/
│   │   ├── __init__.py
│   │   ├── test_items.py
│   │   ├── test_recipes.py
│   │   ├── test_vendors.py
│   │   └── test_professions.py
│   └── test_services/
│       ├── __init__.py
│       └── test_*.py
├── docs/
│   ├── database_schema.sql
│   ├── api_design.md
│   └── project_structure.md
├── data/
│   ├── sample_data.sql                 # Sample WoW items/recipes
│   └── turtle_db.sqlite               # SQLite database file
├── pyproject.toml
├── README.md
├── CLAUDE.md
└── .gitignore
```

## Architecture Layers

### 1. API Layer (`api/`)
- **FastAPI routers** for endpoint organization
- **Dependencies** for database sessions, authentication
- **Request/response handling** with proper HTTP status codes
- **Input validation** using Pydantic schemas

### 2. Schema Layer (`schemas/`)
- **Pydantic models** for request/response serialization
- **Input validation** and type checking
- **Documentation** generation for OpenAPI/Swagger

### 3. Service Layer (`services/`)
- **Business logic** implementation
- **Data processing** and transformation
- **Complex operations** like recipe cost calculation
- **Cross-entity operations** and aggregations

### 4. Database Layer (`database/`)
- **SQLAlchemy ORM models** for data persistence
- **Database connection** management
- **Migration scripts** for schema evolution
- **Query optimization** and relationships

### 5. Utils Layer (`utils/`)
- **Currency conversion** (copper ↔ gold/silver/copper)
- **Custom exceptions** for business logic errors
- **Helper functions** and utilities

## Key Design Decisions

### Database Strategy
- **SQLite** for development and small deployments
- **SQLAlchemy async** for non-blocking database operations
- **Migration support** for schema evolution

### API Design
- **RESTful endpoints** following standard conventions
- **Nested resources** for logical grouping (vendor items, profession recipes)
- **Filtering and pagination** for large datasets
- **Consistent response format** with success/error structure

### Error Handling
- **Custom exceptions** mapped to appropriate HTTP status codes
- **Validation errors** with detailed field-level messages
- **Business logic errors** with meaningful error codes

### Performance Considerations
- **Async/await** throughout the stack
- **Database indexes** on frequently queried fields
- **Eager loading** for related entities
- **Response caching** for reference data