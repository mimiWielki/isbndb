# ISBNdb Python Wrapper

A modern Python client for the ISBNdb API with type hints, rate limiting, and dataclasses.

## Features

- Full type hint support
- Automatic rate limiting based on subscription plan
- Dataclasses for all API responses
- Proper error handling with custom exceptions
- Support for all main API endpoints

## Installation

```bash
pip install requests ratelimiter
```

## Quick Start

```python
from isbndb.client import ISBNdbClient

# Initialize client with your API key
client = ISBNdbClient(api_key="your_api_key_here", plan="pro")  # plan can be default/premium/pro

# Get book details
book = client.get_book("9780134093413")
print(f"{book.title} by {', '.join(book.authors)}")

# Search for books
results = client.search_books("python programming", page_size=5)
for book in results:
    print(f"{book.isbn13}: {book.title}")
```

## Usage

### Available Methods

- `get_book(isbn: str, with_prices: bool = False) -> BookData`
- `search_books(query: str, page: int = 1, page_size: int = 20, ...) -> List[BookData]`
- `get_author(name: str, page: int = 1, page_size: int = 20) -> AuthorData`
- `get_publisher(name: str, page: int = 1, page_size: int = 20) -> PublisherData`

### Error Handling

```python
try:
    book = client.get_book("invalid-isbn")
except ISBNdbAPIError as e:
    print(f"API Error: {e}")
```

## Rate Limiting

The client automatically handles rate limits:
- Default plan: 1 request/second
- Premium: 3 requests/second  
- Pro: 5 requests/second

429 errors are automatically retried after the `Retry-After` period specified by the API.

## License

MIT License - See [LICENSE](LICENSE) file
