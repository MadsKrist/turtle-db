"""
Service layer for item-related business logic.
"""
from typing import List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from turtle_db.database.models import Item, ItemType, ItemSubtype, ItemSlot
from turtle_db.schemas.items import ItemCreate, ItemUpdate, ItemFilter
from turtle_db.schemas.common import PaginationParams
from turtle_db.utils.exceptions import (
    ItemNotFoundException, 
    ReferenceDataNotFoundException
)


class ItemService:
    """Service class for item operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_item_by_id(self, item_id: int) -> Item:
        """Get an item by ID with all relationships loaded."""
        query = (
            select(Item)
            .options(
                selectinload(Item.type),
                selectinload(Item.subtype).selectinload(ItemSubtype.type),
                selectinload(Item.slot)
            )
            .where(Item.id == item_id)
        )
        
        result = await self.db.execute(query)
        item = result.scalar_one_or_none()
        
        if not item:
            raise ItemNotFoundException(item_id)
        
        return item
    
    async def get_items_with_filters(
        self, 
        filters: ItemFilter, 
        pagination: PaginationParams
    ) -> Tuple[List[Item], int]:
        """Get items with filtering and pagination."""
        query = (
            select(Item)
            .options(
                selectinload(Item.type),
                selectinload(Item.subtype).selectinload(ItemSubtype.type),
                selectinload(Item.slot)
            )
        )
        
        # Apply filters
        conditions = []
        
        if filters.type_name:
            query = query.join(Item.type)
            conditions.append(ItemType.name == filters.type_name)
        
        if filters.subtype_name:
            query = query.join(Item.subtype)
            conditions.append(ItemSubtype.name == filters.subtype_name)
        
        if filters.slot_name:
            query = query.join(Item.slot)
            conditions.append(ItemSlot.name == filters.slot_name)
        
        if filters.quality:
            conditions.append(Item.quality == filters.quality.value)
        
        if filters.level_min is not None:
            conditions.append(Item.item_level >= filters.level_min)
        
        if filters.level_max is not None:
            conditions.append(Item.item_level <= filters.level_max)
        
        if filters.required_level_min is not None:
            conditions.append(Item.required_level >= filters.required_level_min)
        
        if filters.required_level_max is not None:
            conditions.append(Item.required_level <= filters.required_level_max)
        
        if filters.vendor_sellable is not None:
            if filters.vendor_sellable:
                conditions.append(Item.vendor_price_copper > 0)
            else:
                conditions.append(Item.vendor_price_copper == 0)
        
        if filters.craftable is not None:
            # Note: craftable logic would require Recipe model relationship
            # For now, we'll add a placeholder that doesn't filter
            # In a full implementation, we'd join with Recipe table
            pass
        
        if filters.search:
            search_term = f"%{filters.search}%"
            conditions.append(
                or_(
                    Item.name.ilike(search_term),
                    Item.description.ilike(search_term)
                )
            )
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination and ordering
        query = query.order_by(Item.name).offset(pagination.offset).limit(pagination.limit)
        
        result = await self.db.execute(query)
        items = result.scalars().all()
        
        return list(items), total or 0
    
    async def create_item(self, item_data: ItemCreate) -> Item:
        """Create a new item."""
        # Resolve type, subtype, and slot by name
        type_obj = await self._get_item_type_by_name(item_data.type_name)
        subtype_obj = None
        if item_data.subtype_name:
            subtype_obj = await self._get_item_subtype_by_name(item_data.subtype_name, type_obj.id)
        
        slot_obj = None
        if item_data.slot_name:
            slot_obj = await self._get_item_slot_by_name(item_data.slot_name)
        
        # Convert currency to copper if provided
        vendor_price_copper = 0
        if item_data.vendor_price:
            vendor_price_copper = item_data.vendor_price.to_copper()
        
        # Create item
        item = Item(
            name=item_data.name,
            description=item_data.description,
            type_id=type_obj.id,
            subtype_id=subtype_obj.id if subtype_obj else None,
            slot_id=slot_obj.id if slot_obj else None,
            item_level=item_data.item_level,
            required_level=item_data.required_level,
            quality=item_data.quality.value,
            bind_type=item_data.bind_type.value,
            max_stack=item_data.max_stack,
            vendor_price_copper=vendor_price_copper
        )
        
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        
        # Load relationships
        return await self.get_item_by_id(item.id)
    
    async def update_item(self, item_id: int, item_data: ItemUpdate) -> Item:
        """Update an existing item."""
        item = await self.get_item_by_id(item_id)
        
        # Update fields if provided
        if item_data.name is not None:
            item.name = item_data.name
        if item_data.description is not None:
            item.description = item_data.description
        if item_data.item_level is not None:
            item.item_level = item_data.item_level
        if item_data.required_level is not None:
            item.required_level = item_data.required_level
        if item_data.quality is not None:
            item.quality = item_data.quality.value
        if item_data.bind_type is not None:
            item.bind_type = item_data.bind_type.value
        if item_data.max_stack is not None:
            item.max_stack = item_data.max_stack
        if item_data.vendor_price is not None:
            item.vendor_price_copper = item_data.vendor_price.to_copper()
        
        await self.db.commit()
        await self.db.refresh(item)
        
        return await self.get_item_by_id(item.id)
    
    async def delete_item(self, item_id: int) -> None:
        """Delete an item."""
        item = await self.get_item_by_id(item_id)
        
        await self.db.delete(item)
        await self.db.commit()
    
    async def _get_item_type_by_name(self, name: str) -> ItemType:
        """Get item type by name."""
        query = select(ItemType).where(ItemType.name == name)
        result = await self.db.execute(query)
        item_type = result.scalar_one_or_none()
        
        if not item_type:
            raise ReferenceDataNotFoundException("item_type", name)
        
        return item_type
    
    async def _get_item_subtype_by_name(self, name: str, type_id: int) -> ItemSubtype:
        """Get item subtype by name and type."""
        query = select(ItemSubtype).where(
            and_(ItemSubtype.name == name, ItemSubtype.type_id == type_id)
        )
        result = await self.db.execute(query)
        item_subtype = result.scalar_one_or_none()
        
        if not item_subtype:
            raise ReferenceDataNotFoundException("item_subtype", name)
        
        return item_subtype
    
    async def _get_item_slot_by_name(self, name: str) -> ItemSlot:
        """Get item slot by name."""
        query = select(ItemSlot).where(ItemSlot.name == name)
        result = await self.db.execute(query)
        item_slot = result.scalar_one_or_none()
        
        if not item_slot:
            raise ReferenceDataNotFoundException("item_slot", name)
        
        return item_slot