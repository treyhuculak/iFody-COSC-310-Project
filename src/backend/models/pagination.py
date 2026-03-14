from typing import List, Generic, TypeVar
from pydantic import BaseModel

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T] # List of items for the current page
    total: int # Total number of items across all pages
    page:int # Current page number
    page_size: int # Number of items per page
    total_pages: int # Total number of pages based on total_items and page_size
    has_next: bool # Whether there is a next page
    has_prev: bool # Whether there is a previous page