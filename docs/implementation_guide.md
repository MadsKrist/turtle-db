# Implementation Architecture & Patterns

## System Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   FastAPI       │    │   Service        │    │   Database      │
│   Endpoints     │───▶│   Layer          │───▶│   SQLAlchemy    │
│                 │    │                  │    │   + SQLite      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Pydantic      │    │   Business       │    │   Data Access   │
│   Schemas       │    │   Logic          │    │   Layer         │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Key Architectural Patterns

### 1. Dependency Injection Pattern
```python
# api/deps.py
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_async_session

async def get_db() -> AsyncSession:
    async with get_async_session() as session:
        yield session
```

### 2. Repository Pattern (Optional Enhancement)
```python
# services/base.py
class BaseService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, id: int):
        # Generic get by ID implementation
        pass
    
    async def create(self, data: BaseModel):
        # Generic create implementation
        pass
```

### 3. Service Layer Pattern
```python
# services/items.py
class ItemService:
    async def create_item_with_dependencies(
        self, 
        item_data: ItemCreate, 
        db: AsyncSession
    ) -> Item:
        # Resolve type/subtype/slot by name
        # Create item with relationships
        # Handle business logic
        pass
    
    async def get_items_with_filters(
        self, 
        filters: ItemFilters,
        pagination: Pagination
    ) -> PaginatedResponse:
        # Complex filtering logic
        # Pagination handling
        # Related data loading
        pass
```

### 4. Factory Pattern for Complex Objects
```python
# utils/factories.py
class RecipeFactory:
    @staticmethod
    async def create_from_request(
        recipe_data: RecipeCreate,
        db: AsyncSession
    ) -> Recipe:
        # Resolve profession by name
        # Resolve item references
        # Create recipe with ingredients
        # Validate business rules
        pass
```

## Implementation Phases

### Phase 1: Foundation (MVP)
1. **Database Setup**
   - SQLAlchemy models
   - Database connection management
   - Initial migrations
   
2. **Basic CRUD**
   - Item endpoints
   - Simple filtering
   - Basic error handling

3. **Core Validation**
   - Pydantic schemas
   - Input validation
   - Response formatting

### Phase 2: Enhanced Features
1. **Recipe System**
   - Recipe CRUD
   - Ingredient relationships
   - Cost calculations
   
2. **Vendor System**
   - Vendor CRUD
   - Item pricing
   - Stock management

3. **Advanced Filtering**
   - Complex queries
   - Search functionality
   - Pagination

### Phase 3: Advanced Features
1. **Business Logic**
   - Recipe cost calculations
   - Ingredient dependency trees
   - Bulk operations
   
2. **Performance Optimization**
   - Query optimization
   - Caching strategies
   - Async improvements

3. **Enhanced API Features**
   - API versioning
   - Rate limiting
   - Authentication (if needed)

## Key Implementation Decisions

### Database Design Decisions

**Currency Storage Strategy:**
- Store all prices as copper (INTEGER)
- Provide utility functions for gold/silver/copper conversion
- Use computed properties for API responses

**Relationship Management:**
- Use SQLAlchemy relationships for eager loading
- Implement proper foreign key constraints
- Consider cascade delete behaviors

**Indexing Strategy:**
- Index frequently filtered fields (type, quality, level)
- Composite indexes for common filter combinations
- Monitor query performance and add indexes as needed

### API Design Decisions

**Error Handling Strategy:**
```python
# utils/exceptions.py
class ItemNotFoundException(Exception):
    pass

class RecipeValidationException(Exception):
    pass

# In endpoints, convert to proper HTTP responses
```

**Response Formatting:**
```python
# All responses follow consistent format
{
    "success": true,
    "data": {...},
    "error": null
}
```

**Filtering Strategy:**
- Use query parameters for simple filters
- Support multiple filter combinations
- Implement pagination for large result sets

### Performance Considerations

**Database Optimization:**
- Use async SQLAlchemy for non-blocking operations
- Implement proper connection pooling
- Use eager loading for related data

**Caching Strategy:**
- Cache reference data (types, slots, professions)
- Cache expensive calculations (recipe costs)
- Use in-memory caching for development

**Query Optimization:**
- Use appropriate indexes
- Optimize N+1 query problems
- Monitor slow query performance

## Development Guidelines

### Code Organization
```
# File naming convention
- models.py: SQLAlchemy ORM models
- schemas.py: Pydantic request/response models  
- services.py: Business logic implementation
- endpoints.py: FastAPI route handlers
```

### Error Handling Standards
- Use specific exception classes
- Provide meaningful error messages
- Include error codes for API consumers
- Log errors appropriately

### Testing Strategy
- Unit tests for service layer
- Integration tests for API endpoints
- Test database with fixtures
- Mock external dependencies

### Documentation Standards
- OpenAPI/Swagger auto-generation
- Docstrings for all public methods
- API examples in documentation
- Database schema documentation

## Security Considerations

### Input Validation
- Validate all input using Pydantic
- Sanitize user input
- Prevent SQL injection through ORM
- Validate business logic constraints

### Data Protection
- No sensitive data in logs
- Proper error message handling
- Input length limitations
- Rate limiting considerations

## Monitoring & Observability

### Logging Strategy
- Structured logging (JSON format)
- Log levels: DEBUG, INFO, WARNING, ERROR
- Request/response logging
- Database query logging (development)

### Health Checks
- Database connection health
- Application startup checks
- Dependency health validation

### Metrics Considerations
- API response times
- Database query performance
- Error rates by endpoint
- Resource utilization