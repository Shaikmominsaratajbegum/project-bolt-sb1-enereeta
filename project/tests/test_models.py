"""Tests for data models."""

import pytest
from datetime import datetime
from pubmed_company_papers.models import PaperResult, AuthorInfo


class TestAuthorInfo:
    """Test cases for AuthorInfo class."""
    
    def test_basic_author_creation(self) -> None:
        """Test basic author info creation."""
        author = AuthorInfo(name="Smith, John")
        assert author.name == "Smith, John"
        assert author.affiliation is None
        assert author.email is None
        assert author.is_corresponding is False
        assert author.is_non_academic is False
    
    def test_full_author_creation(self) -> None:
        """Test author info creation with all fields."""
        author = AuthorInfo(
            name="Johnson, Jane",
            affiliation="Pfizer Inc., New York, NY",
            email="jane.johnson@pfizer.com",
            is_corresponding=True,
            is_non_academic=True
        )
        assert author.name == "Johnson, Jane"
        assert author.affiliation == "Pfizer Inc., New York, NY"
        assert author.email == "jane.johnson@pfizer.com"
        assert author.is_corresponding is True
        assert author.is_non_academic is True


class TestPaperResult:
    """Test cases for PaperResult class."""
    
    def test_basic_paper_creation(self) -> None:
        """Test basic paper result creation."""
        paper = PaperResult(
            pubmed_id="12345678",
            title="A Novel Drug Discovery Approach"
        )
        assert paper.pubmed_id == "12345678"
        assert paper.title == "A Novel Drug Discovery Approach"
        assert paper.publication_date is None
        assert paper.authors == []
        assert paper.non_academic_authors == []
        assert paper.company_affiliations == []
        assert paper.corresponding_author_email is None
    
    def test_full_paper_creation(self) -> None:
        """Test paper result creation with all fields."""
        authors = [
            AuthorInfo(name="Smith, John", affiliation="University"),
            AuthorInfo(name="Doe, Jane", affiliation="Pfizer Inc.")
        ]
        
        paper = PaperResult(
            pubmed_id="87654321",
            title="Comprehensive Drug Analysis",
            publication_date=datetime(2023, 6, 15),
            authors=authors,
            non_academic_authors=["Doe, Jane"],
            company_affiliations=["Pfizer Inc."],
            corresponding_author_email="jane.doe@pfizer.com"
        )
        
        assert paper.pubmed_id == "87654321"
        assert paper.title == "Comprehensive Drug Analysis"
        assert paper.publication_date == datetime(2023, 6, 15)
        assert len(paper.authors) == 2
        assert paper.non_academic_authors == ["Doe, Jane"]
        assert paper.company_affiliations == ["Pfizer Inc."]
        assert paper.corresponding_author_email == "jane.doe@pfizer.com"
    
    def test_post_init_default_values(self) -> None:
        """Test that post_init properly initializes default values."""
        paper = PaperResult(pubmed_id="123", title="Test")
        
        # These should be initialized as empty lists, not None
        assert isinstance(paper.authors, list)
        assert isinstance(paper.non_academic_authors, list)
        assert isinstance(paper.company_affiliations, list)
        assert len(paper.authors) == 0
        assert len(paper.non_academic_authors) == 0
        assert len(paper.company_affiliations) == 0