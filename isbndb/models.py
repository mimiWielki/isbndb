from dataclasses import dataclass
from typing import Dict, List, Optional, Union

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
class MerchantLogoOffset:
    x: str
    y: str

@dataclass
class Price:
    condition: str
    merchant: str
    merchant_logo: Optional[str] = None
    merchant_logo_offset: Optional[MerchantLogoOffset] = None
    shipping: Optional[str] = None
    price: str
    total: str
    link: str

@dataclass
class BookData:
    title: str
    title_long: Optional[str] = None
    isbn: str
    isbn13: str
    dewey_decimal: Optional[str] = None
    binding: Optional[str] = None
    authors: List[str]
    publisher: str
    date_published: str
    pages: int
    language: str
    image: str
    dimensions: Optional[str] = None
    msrp: Optional[float] = None
    excerpt: Optional[str] = None
    synopsis: Optional[str] = None
    subjects: Optional[List[str]] = None
    overview: Optional[str] = None
    edition: Optional[str] = None
    dimensions_structured: Optional[StructuredDimensions] = None
    prices: Optional[List[Price]] = None

@dataclass
class AuthorData:
    name: str
    books: List[BookData]
    total: int  # Added to match AuthorQueryResults schema

@dataclass
class PublisherData:
    name: str
    books: List[str]  # Should be ISBNs according to schema

@dataclass
class SubjectData:
    subject: str
    parent: str

@dataclass
class SearchResults:
    total: int
    results: List[Union[BookData, str]]  # Can be books or authors/publishers
