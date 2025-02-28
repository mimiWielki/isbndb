from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Dimension:
    unit: str
    value: float

@dataclass
class StructuredDimensions:
    length: Dimension
    width: Dimension
    height: Dimension
    weight: Dimension

@dataclass
class Price:
    condition: str
    merchant: str
    price: str
    total: str
    link: str

@dataclass
class BookData:
    title: str
    isbn: str
    isbn13: str
    authors: List[str]
    publisher: str
    date_published: str
    pages: int
    language: str
    image: str
    overview: Optional[str] = None
    edition: Optional[str] = None
    dimensions_structured: Optional[StructuredDimensions] = None
    prices: Optional[List[Price]] = None

@dataclass
class AuthorData:
    name: str
    books: List[BookData]

@dataclass
class PublisherData:
    name: str
    books: List[BookData]

@dataclass
class SubjectData:
    subject: str
    parent: str

@dataclass
class SearchResults:
    total: int
    results: List[BookData]
