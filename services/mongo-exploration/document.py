from beanie import Document, Link
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class Author(Document):
    """Child document representing an author"""
    name: str
    email: Optional[str] = None
    affiliation: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "authors"


class Tag(Document):
    """Child document representing a tag/category"""
    name: str
    color: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "tags"


class Article(Document):
    """Parent document representing an article with linked child documents"""
    title: str
    content: str
    pmc_id: Optional[str] = None  # To match the existing search functionality
    
    # Links to child documents - this might demonstrate Beanie linking issues
    authors: List[Link[Author]] = []
    tags: List[Link[Tag]] = []
    
    # Metadata
    published_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    # Status and counts
    view_count: int = 0
    is_published: bool = False

    class Settings:
        name = "articles"