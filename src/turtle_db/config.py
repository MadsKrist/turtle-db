"""
Configuration management for the WoW Items API.
"""
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """Application settings."""
    
    # Database configuration
    database_url: str = "sqlite+aiosqlite:///./data/turtle_db.sqlite"
    database_echo: bool = False  # Set to True for SQL query logging
    
    # API configuration
    api_title: str = "World of Warcraft Items API"
    api_version: str = "0.1.0"
    api_description: str = "CRUD API for WoW items, recipes, vendors, and professions"
    
    # CORS configuration
    allowed_origins: list[str] = ["*"]
    allowed_methods: list[str] = ["*"]
    allowed_headers: list[str] = ["*"]
    
    # Pagination defaults
    default_page_size: int = 20
    max_page_size: int = 100
    
    # Currency constants
    copper_per_silver: int = 100
    copper_per_gold: int = 10000
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()

# Ensure data directory exists
data_dir = Path("./data")
data_dir.mkdir(exist_ok=True)