"""Data models for PubMed paper fetcher."""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class AuthorInfo:
    """Information about a paper author."""
    
    name: str
    affiliation: Optional[str] = None
    email: Optional[str] = None
    is_corresponding: bool = False
    is_non_academic: bool = False


@dataclass
class PaperResult:
    """Result data for a research paper."""
    
    pubmed_id: str
    title: str
    publication_date: Optional[datetime] = None
    authors: List[AuthorInfo] = None
    non_academic_authors: List[str] = None
    company_affiliations: List[str] = None
    corresponding_author_email: Optional[str] = None
    
    def __post_init__(self) -> None:
        """Initialize default values for mutable fields."""
        if self.authors is None:
            self.authors = []
        if self.non_academic_authors is None:
            self.non_academic_authors = []
        if self.company_affiliations is None:
            self.company_affiliations = []