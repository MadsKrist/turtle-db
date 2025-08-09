"""
Custom exceptions for the WoW Items API.
"""
from typing import Optional, Dict, Any


class TurtleDBException(Exception):
    """Base exception for turtle-db API."""
    
    def __init__(
        self, 
        message: str, 
        code: str = "GENERIC_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)


class ItemNotFoundException(TurtleDBException):
    """Exception raised when an item is not found."""
    
    def __init__(self, item_id: int):
        super().__init__(
            message=f"Item with ID {item_id} not found",
            code="ITEM_NOT_FOUND",
            details={"item_id": item_id}
        )


class RecipeNotFoundException(TurtleDBException):
    """Exception raised when a recipe is not found."""
    
    def __init__(self, recipe_id: int):
        super().__init__(
            message=f"Recipe with ID {recipe_id} not found",
            code="RECIPE_NOT_FOUND",
            details={"recipe_id": recipe_id}
        )


class VendorNotFoundException(TurtleDBException):
    """Exception raised when a vendor is not found."""
    
    def __init__(self, vendor_id: int):
        super().__init__(
            message=f"Vendor with ID {vendor_id} not found",
            code="VENDOR_NOT_FOUND",
            details={"vendor_id": vendor_id}
        )


class ProfessionNotFoundException(TurtleDBException):
    """Exception raised when a profession is not found."""
    
    def __init__(self, profession_id: int):
        super().__init__(
            message=f"Profession with ID {profession_id} not found",
            code="PROFESSION_NOT_FOUND",
            details={"profession_id": profession_id}
        )


class ReferenceDataNotFoundException(TurtleDBException):
    """Exception raised when reference data (type, subtype, slot) is not found."""
    
    def __init__(self, reference_type: str, name: str):
        super().__init__(
            message=f"{reference_type.title()} '{name}' not found",
            code="REFERENCE_DATA_NOT_FOUND",
            details={"reference_type": reference_type, "name": name}
        )


class ValidationException(TurtleDBException):
    """Exception raised for validation errors."""
    
    def __init__(self, message: str, field: Optional[str] = None):
        details = {"field": field} if field else {}
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            details=details
        )


class RecipeValidationException(TurtleDBException):
    """Exception raised for recipe-specific validation errors."""
    
    def __init__(self, message: str):
        super().__init__(
            message=message,
            code="RECIPE_VALIDATION_ERROR"
        )


class DatabaseException(TurtleDBException):
    """Exception raised for database-related errors."""
    
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        details = {"original_error": str(original_error)} if original_error else {}
        super().__init__(
            message=message,
            code="DATABASE_ERROR",
            details=details
        )


# Import-specific exceptions

class ImportException(TurtleDBException):
    """Base exception for import operations."""
    pass


class ImportValidationError(ImportException):
    """Invalid import data or URL format."""
    def __init__(self, message: str):
        super().__init__(message, "IMPORT_VALIDATION_ERROR")


class ImportSourceError(ImportException):
    """Error accessing external data source."""
    def __init__(self, message: str):
        super().__init__(message, "IMPORT_SOURCE_ERROR")


class ImportDuplicateError(ImportException):
    """Attempting to import duplicate item."""
    def __init__(self, item_name: str):
        super().__init__(f"Item '{item_name}' already exists", "IMPORT_DUPLICATE")


class ImportMappingError(ImportException):
    """Error mapping scraped data to database models."""
    def __init__(self, field: str, value: str):
        super().__init__(f"Cannot map {field}: {value}", "IMPORT_MAPPING_ERROR")