import pytest
from unittest.mock import Mock, patch
from isbndb.client import ISBNdbClient, ISBNdbAPIError
from isbndb.models import BookData, AuthorData

@pytest.fixture
def mock_client():
    client = ISBNdbClient(api_key="test-key", plan="default")
    client.session = Mock()
    return client

def test_get_book_success(mock_client):
    mock_response = Mock()
    mock_response.json.return_value = {
        "book": {
            "title": "Test Book",
            "isbn": "1234567890",
            "isbn13": "1234567890123",
            "authors": ["Author 1"],
            "publisher": "Test Publisher",
            "date_published": "2023-01-01",
            "pages": 100,
            "language": "en",
            "image": "cover.jpg"
        }
    }
    mock_client.session.get.return_value = mock_response

    book = mock_client.get_book("1234567890")
    assert isinstance(book, BookData)
    assert book.title == "Test Book"
    assert book.isbn13 == "1234567890123"

def test_rate_limit_handling(mock_client):
    mock_response = Mock()
    mock_response.status_code = 429
    mock_response.headers = {"Retry-After": "1"}
    mock_client.session.get.return_value = mock_response

    with pytest.raises(ISBNdbAPIError):
        mock_client.get_book("1234567890")

def test_author_not_found(mock_client):
    mock_response = Mock()
    mock_response.status_code = 404
    mock_client.session.get.return_value = mock_response

    with pytest.raises(ISBNdbAPIError) as excinfo:
        mock_client.get_author("Unknown Author")
    assert "Resource not found" in str(excinfo.value)
