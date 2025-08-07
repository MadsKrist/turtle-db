"""
Item endpoints for the WoW Items API.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from turtle_db.api.deps import get_db
from turtle_db.services.items import ItemService
from turtle_db.schemas.items import ItemCreate, ItemUpdate, ItemFilter
from turtle_db.schemas.common import (
    APIResponse,
    PaginationParams,
    PaginatedResponse,
    PaginationMeta,
    Currency,
    ItemQuality,
)
from turtle_db.utils.exceptions import (
    TurtleDBException,
    ItemNotFoundException,
    ReferenceDataNotFoundException,
)

router = APIRouter()
logger = logging.getLogger(__name__)


def create_item_response_data(item) -> dict:
    """Create item response data with computed fields."""
    response_data = {
        "id": item.id,
        "name": item.name,
        "description": item.description,
        "type": {
            "id": item.type.id,
            "name": item.type.name,
            "description": item.type.description,
        },
        "subtype": None,
        "slot": None,
        "item_level": item.item_level,
        "required_level": item.required_level,
        "quality": item.quality,
        "bind_type": item.bind_type,
        "max_stack": item.max_stack,
        "pricing": None,
        "crafting": None,
        "created_at": item.created_at,
        "updated_at": item.updated_at,
    }

    if item.subtype:
        response_data["subtype"] = {
            "id": item.subtype.id,
            "name": item.subtype.name,
            "description": item.subtype.description,
            "type": {
                "id": item.subtype.type.id,
                "name": item.subtype.type.name,
                "description": item.subtype.type.description,
            }
            if item.subtype.type
            else None,
        }

    if item.slot:
        response_data["slot"] = {
            "id": item.slot.id,
            "name": item.slot.name,
            "description": item.slot.description,
        }

    if item.vendor_price_copper > 0:
        currency = Currency.from_copper(item.vendor_price_copper)
        response_data["pricing"] = {
            "vendor_price": {
                "gold": currency.gold,
                "silver": currency.silver,
                "copper": currency.copper,
                "total_copper": item.vendor_price_copper,
            }
        }

    return response_data


@router.get("", response_model=PaginatedResponse, summary="List items")
async def list_items(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    type_name: str = Query(None, description="Filter by item type"),
    subtype_name: str = Query(None, description="Filter by item subtype"),
    slot_name: str = Query(None, description="Filter by item slot"),
    quality: str = Query(None, description="Filter by item quality"),
    level_min: int = Query(None, ge=1, le=100, description="Minimum item level"),
    level_max: int = Query(None, ge=1, le=100, description="Maximum item level"),
    search: str = Query(
        None, min_length=1, max_length=100, description="Search in name/description"
    ),
):
    """Get a paginated list of items with optional filtering."""
    try:
        pagination = PaginationParams(page=page, limit=limit)
        # Convert quality string to enum if provided
        quality_enum = None
        if quality:
            try:
                quality_enum = ItemQuality(quality)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "success": False,
                        "error": {
                            "code": "INVALID_QUALITY",
                            "message": f"Invalid quality value: {quality}",
                        },
                    },
                )

        filters = ItemFilter(
            type_name=type_name,
            subtype_name=subtype_name,
            slot_name=slot_name,
            quality=quality_enum,
            level_min=level_min,
            level_max=level_max,
            required_level_min=None,
            required_level_max=None,
            vendor_sellable=None,
            craftable=None,
            search=search,
        )

        service = ItemService(db)
        items, total = await service.get_items_with_filters(filters, pagination)

        # Calculate pagination metadata
        pages = (total + pagination.limit - 1) // pagination.limit
        has_next = pagination.page < pages
        has_previous = pagination.page > 1

        pagination_meta = PaginationMeta(
            page=pagination.page,
            limit=pagination.limit,
            total=total,
            pages=pages,
            has_next=has_next,
            has_previous=has_previous,
        )

        # Convert items to response format
        item_data = [create_item_response_data(item) for item in items]

        return PaginatedResponse(
            success=True, data=item_data, pagination=pagination_meta
        )

    except TurtleDBException as e:
        logger.error(f"Business logic error in list_items: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success": False, "error": {"code": e.code, "message": e.message}},
        )
    except Exception as e:
        logger.error(f"Unexpected error in list_items: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {"code": "INTERNAL_ERROR", "message": "Internal server error"},
            },
        )


@router.post(
    "",
    response_model=APIResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create item",
)
async def create_item(item_data: ItemCreate, db: AsyncSession = Depends(get_db)):
    """Create a new item."""
    try:
        service = ItemService(db)
        item = await service.create_item(item_data)

        return APIResponse(
            success=True,
            data=create_item_response_data(item),
            message="Item created successfully",
        )

    except ReferenceDataNotFoundException as e:
        logger.error(f"Reference data not found in create_item: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success": False, "error": {"code": e.code, "message": e.message}},
        )
    except TurtleDBException as e:
        logger.error(f"Business logic error in create_item: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success": False, "error": {"code": e.code, "message": e.message}},
        )
    except Exception as e:
        logger.error(f"Unexpected error in create_item: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {"code": "INTERNAL_ERROR", "message": "Internal server error"},
            },
        )


@router.get("/{item_id}", response_model=APIResponse, summary="Get item by ID")
async def get_item(item_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific item by ID."""
    try:
        service = ItemService(db)
        item = await service.get_item_by_id(item_id)

        return APIResponse(success=True, data=create_item_response_data(item))

    except ItemNotFoundException as e:
        logger.error(f"Item not found in get_item: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"success": False, "error": {"code": e.code, "message": e.message}},
        )
    except Exception as e:
        logger.error(f"Unexpected error in get_item: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {"code": "INTERNAL_ERROR", "message": "Internal server error"},
            },
        )


@router.put("/{item_id}", response_model=APIResponse, summary="Update item")
async def update_item(
    item_id: int, item_data: ItemUpdate, db: AsyncSession = Depends(get_db)
):
    """Update an existing item."""
    try:
        service = ItemService(db)
        item = await service.update_item(item_id, item_data)

        return APIResponse(
            success=True,
            data=create_item_response_data(item),
            message="Item updated successfully",
        )

    except ItemNotFoundException as e:
        logger.error(f"Item not found in update_item: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"success": False, "error": {"code": e.code, "message": e.message}},
        )
    except TurtleDBException as e:
        logger.error(f"Business logic error in update_item: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success": False, "error": {"code": e.code, "message": e.message}},
        )
    except Exception as e:
        logger.error(f"Unexpected error in update_item: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {"code": "INTERNAL_ERROR", "message": "Internal server error"},
            },
        )


@router.delete("/{item_id}", response_model=APIResponse, summary="Delete item")
async def delete_item(item_id: int, db: AsyncSession = Depends(get_db)):
    """Delete an item."""
    try:
        service = ItemService(db)
        await service.delete_item(item_id)

        return APIResponse(success=True, message="Item deleted successfully")

    except ItemNotFoundException as e:
        logger.error(f"Item not found in delete_item: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"success": False, "error": {"code": e.code, "message": e.message}},
        )
    except Exception as e:
        logger.error(f"Unexpected error in delete_item: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error": {"code": "INTERNAL_ERROR", "message": "Internal server error"},
            },
        )
