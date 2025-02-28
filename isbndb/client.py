import requests
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from ratelimiter import RateLimiter
import time

BASE_URLS = {
    'default': 'https://api2.isbndb.com',
    'premium': 'https://api.premium.isbndb.com',
    'pro': 'https://api.pro.isbndb.com'
}

RATE_LIMITS = {
    'default': 1,
    'premium': 3,
    'pro': 5
}

class ISBNdbAPIError(Exception):
    """Custom exception for API errors"""
    pass

from .models import BookData, AuthorData, PublisherData, SubjectData

class ISBNdbClient:
    def __init__(self, api_key: str, plan: str = 'default'):
        self.api_key = api_key
        self.base_url = BASE_URLS.get(plan, BASE_URLS['default'])
        self.rate_limit = RATE_LIMITS.get(plan, 1)
        
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': api_key,
            'Content-Type': 'application/json'
        })
        
        # Set up rate limiter
        self.ratelimiter = RateLimiter(max_calls=self.rate_limit, period=1)
    
    def _request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Base request method with error handling and rate limiting"""
        url = f"{self.base_url}{endpoint}"
        
        with self.ratelimiter:
            try:
                response = self.session.get(url, params=params)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.HTTPError as e:
                if response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', 1))
                    time.sleep(retry_after)
                    return self._request(endpoint, params)
                elif response.status_code == 404:
                    raise ISBNdbAPIError("Resource not found") from e
                else:
                    raise ISBNdbAPIError(f"API Error: {str(e)}") from e
    
    def get_book(self, isbn: str, with_prices: bool = False) -> BookData:
        """Get book details by ISBN"""
        params = {'with_prices': int(with_prices)} if with_prices else None
        data = self._request(f"/book/{isbn}", params)
        return BookData(**data['book'])
    
    def search_books(self, query: str, page: int = 1, page_size: int = 20, 
                    language: Optional[str] = None) -> List[BookData]:
        """Search books with pagination and filters"""
        params = {
            'query': query,
            'page': page,
            'pageSize': page_size,
            'language': language
        }
        data = self._request(f"/books/{query}", {k: v for k, v in params.items() if v is not None})
        return [BookData(**item['book']) for item in data.get('books', [])]
    
    def get_author(self, name: str, page: int = 1, page_size: int = 20) -> AuthorData:
        """Get author details with paginated books"""
        params = {'page': page, 'pageSize': page_size}
        data = self._request(f"/author/{name}", params)
        return AuthorData(
            name=data['author'],
            books=[BookData(**book['book']) for book in data.get('books', [])]
        )
    
    def get_publisher(self, name: str, page: int = 1, page_size: int = 20) -> PublisherData:
        """Get publisher details with paginated books"""
        params = {'page': page, 'pageSize': page_size}
        data = self._request(f"/publisher/{name}", params)
        return PublisherData(
            name=data['name'],
            books=[BookData(isbn=book['isbn']) for book in data.get('books', [])]
        )
