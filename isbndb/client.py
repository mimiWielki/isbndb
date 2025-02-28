import requests
from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Literal
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

from .models import BookData, AuthorData, PublisherData, SubjectData, SearchResults

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
    
    def _request(self, endpoint: str, params: Optional[Dict] = None, 
                method: str = "GET", data: Optional[Dict] = None) -> Dict:
        """Base request method with error handling and rate limiting"""
        url = f"{self.base_url}{endpoint}"
        
        with self.ratelimiter:
            try:
                if method == "POST":
                    response = self.session.post(url, data=data)
                else:
                    response = self.session.get(url, params=params)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.HTTPError as e:
                if response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', 1))
                    time.sleep(retry_after)
                    return self._request(endpoint, params)
                elif response.status_code == 404:
                    error_msg = response.json().get('errorMessage', 'Resource not found')
                    raise ISBNdbAPIError(error_msg) from e
                else:
                    error_msg = response.json().get('message', str(e))
                    raise ISBNdbAPIError(f"API Error ({response.status_code}): {error_msg}") from e
    
    def get_book(self, isbn: str, with_prices: bool = False) -> BookData:
        """Get book details by ISBN"""
        params = {'with_prices': int(with_prices)} if with_prices else None
        data = self._request(f"/book/{isbn}", params)
        return BookData(**data['book'])
    
    def get_books_bulk(self, isbns: List[str]) -> List[BookData]:
        """Get multiple books by ISBN list"""
        data = self._request("/books", params={}, method="POST", data={"isbns": isbns})
        return [BookData(**item['book']) for item in data.get('books', [])]

    def search_books(self, query: str, page: int = 1, page_size: int = 20,
                    language: Optional[str] = None, column: Optional[str] = None,
                    year: Optional[int] = None, edition: Optional[int] = None,
                    should_match_all: bool = False) -> List[BookData]:
        """Search books with pagination and filters"""
        params = {
            'query': query,
            'page': page,
            'pageSize': page_size,
            'language': language,
            'column': column,
            'year': year,
            'edition': edition,
            'shouldMatchAll': int(should_match_all)
        }
        data = self._request(f"/books/{query}", {k: v for k, v in params.items() if v is not None})
        return [BookData(**item['book']) for item in data.get('books', [])]
    
    def get_author(self, name: str, page: int = 1, page_size: int = 20, 
                  language: Optional[str] = None) -> AuthorData:
        """Get author details with paginated books"""
        params = {
            'page': page,
            'pageSize': page_size,
            'language': language
        }
        data = self._request(f"/author/{name}", params)
        return AuthorData(
            name=data['author'],
            books=[book['isbn'] for book in data.get('books', [])]
        )
    
    def search_authors(self, query: str, page: int = 1, page_size: int = 20) -> List[str]:
        """Search authors by name"""
        params = {'page': page, 'pageSize': page_size}
        data = self._request(f"/authors/{query}", params)
        return data.get('authors', [])

    def search_publishers(self, query: str, page: int = 1, page_size: int = 20) -> List[str]:
        """Search publishers by name"""
        params = {'page': page, 'pageSize': page_size}
        data = self._request(f"/publishers/{query}", params)
        return data.get('publishers', [])

    def general_search(self, index: str, query: str, filters: Dict[str, str], 
                      page: int = 1, page_size: int = 20) -> SearchResults:
        """General search across all indexes"""
        params = {'page': page, 'pageSize': page_size, **filters}
        data = self._request(f"/search/{index}/{query}", params)
        return SearchResults(
            total=data.get('total', 0),
            results=[BookData(**item['book']) for item in data.get('results', [])]
        )

    def get_subject(self, name: str) -> SubjectData:
        """Get subject details"""
        data = self._request(f"/subject/{name}")
        return SubjectData(**data)

    def search_subjects(self, query: str, page: int = 1, page_size: int = 20) -> List[str]:
        """Search subjects"""
        params = {'page': page, 'pageSize': page_size}
        data = self._request(f"/subjects/{query}", params)
        return data.get('subjects', [])

    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        return self._request("/stats")

    def get_publisher(self, name: str, page: int = 1, page_size: int = 20) -> PublisherData:
        """Get publisher details with paginated books"""
        params = {'page': page, 'pageSize': page_size}
        data = self._request(f"/publisher/{name}", params)
        return PublisherData(
            name=data.get('name', ''),
            books=[BookData(**book['book']) for book in data.get('books', [])]
        )
