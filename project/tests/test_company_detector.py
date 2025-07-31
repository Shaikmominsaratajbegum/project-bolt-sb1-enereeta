"""Tests for company detection functionality."""

import pytest
from pubmed_company_papers.company_detector import CompanyDetector


class TestCompanyDetector:
    """Test cases for CompanyDetector class."""
    
    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.detector = CompanyDetector()
    
    def test_known_pharmaceutical_company(self) -> None:
        """Test detection of known pharmaceutical companies."""
        affiliations = [
            "Pfizer Inc., New York, NY",
            "Johnson & Johnson, New Brunswick, NJ",
            "Novartis Pharmaceuticals, Basel, Switzerland",
            "Roche Holding AG, Basel, Switzerland"
        ]
        
        for affiliation in affiliations:
            assert self.detector.is_company_affiliation(affiliation), f"Failed to detect: {affiliation}"
    
    def test_known_biotech_company(self) -> None:
        """Test detection of known biotech companies."""
        affiliations = [
            "Genentech Inc., South San Francisco, CA",
            "Moderna Inc., Cambridge, MA",
            "BioNTech SE, Mainz, Germany",
            "Vertex Pharmaceuticals, Boston, MA"
        ]
        
        for affiliation in affiliations:
            assert self.detector.is_company_affiliation(affiliation), f"Failed to detect: {affiliation}"
    
    def test_academic_institutions(self) -> None:
        """Test that academic institutions are not detected as companies."""
        affiliations = [
            "Harvard University, Boston, MA",
            "Stanford University School of Medicine, Stanford, CA",
            "Massachusetts General Hospital, Boston, MA",
            "National Institutes of Health, Bethesda, MD",
            "University of California, San Francisco, CA"
        ]
        
        for affiliation in affiliations:
            assert not self.detector.is_company_affiliation(affiliation), f"Incorrectly detected: {affiliation}"
    
    def test_company_email_domains(self) -> None:
        """Test detection based on company email domains."""
        test_cases = [
            ("Any Affiliation", "researcher@pfizer.com", True),
            ("Any Affiliation", "scientist@jnj.com", True),
            ("Any Affiliation", "user@gmail.com", False),
            ("Any Affiliation", "researcher@university.edu", False)
        ]
        
        for affiliation, email, expected in test_cases:
            result = self.detector.is_company_affiliation(affiliation, email)
            assert result == expected, f"Failed for {affiliation}, {email}: expected {expected}, got {result}"
    
    def test_generic_company_patterns(self) -> None:
        """Test detection of generic company patterns."""
        affiliations = [
            "XYZ Pharmaceuticals Inc.",
            "ABC Biotech Corp.",
            "Research Therapeutics LLC",
            "Innovation Biosciences Ltd.",
            "Global Life Sciences Company"
        ]
        
        for affiliation in affiliations:
            assert self.detector.is_company_affiliation(affiliation), f"Failed to detect: {affiliation}"
    
    def test_mixed_affiliations(self) -> None:
        """Test affiliations that contain both academic and company indicators."""
        # These should be detected as companies due to strong company indicators
        company_affiliations = [
            "Pfizer University Research Center, New York, NY",  # Known company trumps "university"
            "Novartis Institute for Biomedical Research, Cambridge, MA"
        ]
        
        for affiliation in company_affiliations:
            assert self.detector.is_company_affiliation(affiliation), f"Failed to detect: {affiliation}"
        
        # These should not be detected as companies
        academic_affiliations = [
            "University Hospital Pharmaceutical Department",
            "Medical School Drug Research Laboratory"
        ]
        
        for affiliation in academic_affiliations:
            assert not self.detector.is_company_affiliation(affiliation), f"Incorrectly detected: {affiliation}"
    
    def test_extract_company_names(self) -> None:
        """Test extraction of company names from affiliations."""
        test_cases = [
            ("Pfizer Inc., New York, NY", ["Pfizer"]),
            ("Novartis Pharmaceuticals, Basel, Switzerland", ["Novartis", "Pharmaceuticals"]),
            ("Johnson & Johnson Research, New Brunswick, NJ", ["Johnson & Johnson"]),
            ("No company here", [])
        ]
        
        for affiliation, expected_companies in test_cases:
            companies = self.detector.extract_company_names(affiliation)
            # Check that at least one expected company is found
            if expected_companies:
                assert any(expected in ' '.join(companies).lower() for expected in [c.lower() for c in expected_companies]), \
                    f"Expected companies {expected_companies} not found in {companies} for {affiliation}"
            else:
                assert not companies, f"Unexpected companies found: {companies} for {affiliation}"
    
    def test_empty_or_none_input(self) -> None:
        """Test handling of empty or None inputs."""
        assert not self.detector.is_company_affiliation(None)
        assert not self.detector.is_company_affiliation("")
        assert not self.detector.is_company_affiliation("", "")
        assert self.detector.extract_company_names(None) == []
        assert self.detector.extract_company_names("") == []