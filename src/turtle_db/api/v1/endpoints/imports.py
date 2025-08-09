"""
Import endpoints for the WoW Items API.
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, HttpUrl, Field

from turtle_db.api.deps import get_db
from turtle_db.services.import_service import ImportService
from turtle_db.schemas.common import APIResponse
from turtle_db.utils.exceptions import (
    ImportValidationError, ImportSourceError, ImportDuplicateError, ImportMappingError
)

router = APIRouter()
logger = logging.getLogger(__name__)


class ImportItemRequest(BaseModel):
    """Request schema for importing an item from external source."""
    url: HttpUrl = Field(..., description="URL to the item in external database")
    import_recipes: bool = Field(True, description="Whether to import associated recipes")


class ImportItemResponse(BaseModel):
    """Response schema for item import operation."""
    item_id: int = Field(..., description="ID of the imported item")
    item_name: str = Field(..., description="Name of the imported item")
    recipes_imported: int = Field(..., description="Number of recipes imported")
    warnings: List[str] = Field(default_factory=list, description="Import warnings")


@router.post(
    "/item",
    response_model=APIResponse[ImportItemResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Import item from external database",
    description="""
    Import an item and its associated recipes from an external database URL.
    
    Currently supports:
    - Turtle-WoW Database (database.turtle-wow.org)
    
    The import process:
    1. Validates the URL format
    2. Scrapes item data (name, type, subtype, slot, quality, etc.)
    3. Finds crafting spells in the 'tab-created-by' section
    4. Imports each recipe with ingredients
    5. Maps external data to internal database models
    
    Duplicate items are rejected with 409 Conflict status.
    """
)
async def import_item_from_url(
    request: ImportItemRequest,
    db: AsyncSession = Depends(get_db)
):
    """Import item and associated recipes from external database URL."""
    
    logger.info(f"Import request received for URL: {request.url}")
    
    # Validate URL format first, before entering try block
    import_service_temp = ImportService(db)
    if not import_service_temp.validate_source_url(str(request.url)):
        logger.warning(f"Invalid URL format: {request.url}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": {
                    "code": "INVALID_URL",
                    "message": "Invalid or unsupported database URL format. Only Turtle-WoW database URLs are supported."
                }
            }
        )
    
    try:
        # Use async context manager for automatic cleanup
        async with ImportService(db) as import_service:
            
            # Perform import
            result = await import_service.import_item_from_url(
                url=str(request.url),
                import_recipes=request.import_recipes
            )
            
            # Convert to response format
            response_data = ImportItemResponse(
                item_id=result.item_id,
                item_name=result.item_name,
                recipes_imported=result.recipes_imported,
                warnings=result.warnings
            )
            
            logger.info(f"Import completed successfully: {result.item_name} (ID: {result.item_id})")
            
            return APIResponse(
                success=True,
                data=response_data,
                message=f"Successfully imported '{result.item_name}' with {result.recipes_imported} recipes"
            )
            
    except ImportDuplicateError as e:
        logger.warning(f"Duplicate item import attempt: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "success": False,
                "error": {
                    "code": e.code,
                    "message": e.message
                }
            }
        )
    
    except ImportValidationError as e:
        logger.error(f"Import validation error: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": {
                    "code": e.code,
                    "message": e.message
                }
            }
        )
    
    except ImportSourceError as e:
        logger.error(f"Import source error: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "success": False,
                "error": {
                    "code": e.code,
                    "message": f"External data source unavailable: {e.message}"
                }
            }
        )
    
    except ImportMappingError as e:
        logger.error(f"Import mapping error: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "success": False,
                "error": {
                    "code": e.code,
                    "message": f"Data mapping failed: {e.message}"
                }
            }
        )
    
    except Exception as e:
        logger.error(f"Unexpected error during import: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Import operation failed due to an internal error"
                }
            }
        )


@router.get(
    "/sources",
    response_model=APIResponse[List[dict]],
    summary="Get supported import sources",
    description="List all supported external data sources for importing items and recipes."
)
async def get_supported_sources():
    """Get list of supported import sources."""
    
    sources = [
        {
            "name": "Turtle-WoW Database",
            "base_url": "https://database.turtle-wow.org",
            "supported_formats": ["item", "spell"],
            "example_urls": [
                "https://database.turtle-wow.org/?item=12640",
                "https://database.turtle-wow.org/?spell=16729"
            ],
            "description": "Community-maintained World of Warcraft database for Turtle WoW private server"
        }
    ]
    
    return APIResponse(
        success=True,
        data=sources,
        message=f"Found {len(sources)} supported import sources"
    )