"""Tests for CSV writer functionality."""

import pytest
import io
from datetime import datetime
from pubmed_company_papers.csv_writer import CSVWriter
from pubmed_company_papers.models import PaperResult, AuthorInfo


class TestCSVWriter:
    """Test cases for CSVWriter class."""
    
    def test_write_empty_results(self) -> None:
        """Test writing empty results."""
        output = io.StringIO()
        CSVWriter.write_results([], output)
        
        result = output.getvalue()
        lines = result.strip().split('\n')
        
        # Should have header only
        assert len(lines) == 1
        assert "PubmedID" in lines[0]
        assert "Title" in lines[0]
    
    def test_write_single_result(self) -> None:
        """Test writing a single paper result."""
        paper = PaperResult(
            pubmed_id="12345678",
            title="Test Paper Title",
            publication_date=datetime(2023, 6, 15),
            non_academic_authors=["Smith, John", "Doe, Jane"],
            company_affiliations=["Pfizer Inc.", "Novartis"],
            corresponding_author_email="john.smith@pfizer.com"
        )
        
        output = io.StringIO()
        CSVWriter.write_results([paper], output)
        
        result = output.getvalue()
        lines = result.strip().split('\n')
        
        # Should have header + 1 data row
        assert len(lines) == 2
        
        # Check data row content
        data_row = lines[1]
        assert "12345678" in data_row
        assert "Test Paper Title" in data_row
        assert "2023-06-15" in data_row
        assert "Smith, John; Doe, Jane" in data_row
        assert "Pfizer Inc.; Novartis" in data_row
        assert "john.smith@pfizer.com" in data_row
    
    def test_write_multiple_results(self) -> None:
        """Test writing multiple paper results."""
        papers = [
            PaperResult(
                pubmed_id="11111111",
                title="First Paper",
                publication_date=datetime(2023, 1, 1),
                non_academic_authors=["Author One"],
                company_affiliations=["Company A"],
                corresponding_author_email="author1@companya.com"
            ),
            PaperResult(
                pubmed_id="22222222",
                title="Second Paper",
                publication_date=datetime(2023, 2, 1),
                non_academic_authors=["Author Two"],
                company_affiliations=["Company B"],
                corresponding_author_email="author2@companyb.com"
            )
        ]
        
        output = io.StringIO()
        CSVWriter.write_results(papers, output)
        
        result = output.getvalue()
        lines = result.strip().split('\n')
        
        # Should have header + 2 data rows
        assert len(lines) == 3
        assert "11111111" in lines[1]
        assert "22222222" in lines[2]
    
    def test_format_results_string(self) -> None:
        """Test formatting results as string."""
        paper = PaperResult(
            pubmed_id="12345678",
            title="Test Paper",
            publication_date=datetime(2023, 6, 15),
            non_academic_authors=["Smith, John"],
            company_affiliations=["Pfizer Inc."],
            corresponding_author_email="john.smith@pfizer.com"
        )
        
        result = CSVWriter.format_results_string([paper])
        
        assert isinstance(result, str)
        assert "PubmedID" in result  # Header
        assert "12345678" in result  # Data
        assert "Test Paper" in result
        assert "2023-06-15" in result
    
    def test_handle_missing_data(self) -> None:
        """Test handling of missing/None data."""
        paper = PaperResult(
            pubmed_id="12345678",
            title="Test Paper",
            publication_date=None,  # Missing date
            non_academic_authors=[],  # Empty authors
            company_affiliations=[],  # Empty affiliations
            corresponding_author_email=None  # Missing email
        )
        
        output = io.StringIO()
        CSVWriter.write_results([paper], output)
        
        result = output.getvalue()
        lines = result.strip().split('\n')
        
        # Should still have header + 1 data row
        assert len(lines) == 2
        
        # Check that empty fields are handled gracefully
        data_row = lines[1]
        assert "12345678" in data_row
        assert "Test Paper" in data_row