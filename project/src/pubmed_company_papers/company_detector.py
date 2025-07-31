"""Company detection utilities for identifying pharmaceutical/biotech affiliations."""

import re
from typing import List, Set, Optional
import logging


class CompanyDetector:
    """Detects pharmaceutical and biotech company affiliations in author information."""
    
    def __init__(self) -> None:
        """Initialize the company detector with known patterns and companies."""
        self.logger = logging.getLogger(__name__)
        
        # Known pharmaceutical and biotech companies
        self.known_companies: Set[str] = {
            # Major pharmaceutical companies
            "pfizer", "johnson & johnson", "j&j", "roche", "novartis", "merck", "sanofi",
            "glaxosmithkline", "gsk", "astrazeneca", "bristol myers squibb", "bms",
            "abbott", "amgen", "gilead", "biogen", "celgene", "regeneron", "moderna",
            "biontech", "vertex", "alexion", "incyte", "illumina", "thermo fisher",
            
            # Biotech companies
            "genentech", "immunogen", "seattle genetics", "biomarin", "alkermes",
            "bluebird bio", "crispr therapeutics", "editas medicine", "intellia",
            "sangamo", "alnylam", "ionis", "sarepta", "exelixis", "neurocrine",
            
            # Generic indicators
            "pharmaceuticals", "pharmaceutical", "pharma", "biotech", "biotechnology",
            "therapeutics", "biosciences", "life sciences", "drug discovery"
        }
        
        # Academic institution indicators
        self.academic_indicators: Set[str] = {
            "university", "college", "institute", "school", "hospital", "medical center",
            "research center", "academic", "faculty", "department", "lab", "laboratory"
        }
        
        # Email domain patterns for companies
        self.company_email_patterns: List[str] = [
            r"@pfizer\.com", r"@jnj\.com", r"@roche\.com", r"@novartis\.com",
            r"@merck\.com", r"@sanofi\.com", r"@gsk\.com", r"@astrazeneca\.com",
            r"@bms\.com", r"@abbott\.com", r"@amgen\.com", r"@gilead\.com",
            r"@biogen\.com", r"@regeneron\.com", r"@modernatx\.com",
            r"@biontech\.de", r"@vrtx\.com", r"@thermofisher\.com"
        ]
    
    def is_company_affiliation(self, affiliation: Optional[str], email: Optional[str] = None) -> bool:
        """
        Determine if an affiliation represents a pharmaceutical/biotech company.
        
        Args:
            affiliation: The affiliation string to check
            email: Optional email address to check for company domains
            
        Returns:
            True if the affiliation appears to be a pharmaceutical/biotech company
        """
        if not affiliation and not email:
            return False
        
        # Check email domain first
        if email and self._is_company_email(email):
            return True
        
        if not affiliation:
            return False
        
        affiliation_lower = affiliation.lower()
        
        # Check if it contains academic indicators (if so, likely not a company)
        if any(indicator in affiliation_lower for indicator in self.academic_indicators):
            # However, some companies have "research" or "lab" in their names
            # Only exclude if it's clearly academic
            academic_score = sum(1 for indicator in self.academic_indicators 
                                if indicator in affiliation_lower)
            company_score = sum(1 for company in self.known_companies 
                               if company in affiliation_lower)
            
            if academic_score > company_score:
                return False
        
        # Check for known companies
        if any(company in affiliation_lower for company in self.known_companies):
            return True
        
        # Check for company-like patterns
        company_patterns = [
            r'\b(inc\.?|corp\.?|corporation|ltd\.?|limited|llc|co\.?)\b',
            r'\bpharma\b',
            r'\bbiotech\b',
            r'\btherapeutics?\b',
            r'\bbiosciences?\b',
            r'\blife sciences?\b'
        ]
        
        for pattern in company_patterns:
            if re.search(pattern, affiliation_lower):
                return True
        
        return False
    
    def _is_company_email(self, email: str) -> bool:
        """Check if an email address belongs to a known company domain."""
        email_lower = email.lower()
        return any(re.search(pattern, email_lower) for pattern in self.company_email_patterns)
    
    def extract_company_names(self, affiliation: Optional[str]) -> List[str]:
        """
        Extract company names from an affiliation string.
        
        Args:
            affiliation: The affiliation string to parse
            
        Returns:
            List of identified company names
        """
        if not affiliation:
            return []
        
        companies = []
        affiliation_lower = affiliation.lower()
        
        # Look for known companies
        for company in self.known_companies:
            if company in affiliation_lower:
                # Try to extract the full company name from the original text
                pattern = re.compile(re.escape(company), re.IGNORECASE)
                match = pattern.search(affiliation)
                if match:
                    # Try to get more context around the match
                    start, end = match.span()
                    # Look for word boundaries to get full company name
                    words = affiliation.split()
                    for i, word in enumerate(words):
                        if company.lower() in word.lower():
                            # Take this word and potentially adjacent ones
                            company_name = word
                            if i + 1 < len(words) and any(suffix in words[i + 1].lower() 
                                                        for suffix in ['inc', 'corp', 'ltd', 'llc']):
                                company_name += f" {words[i + 1]}"
                            companies.append(company_name)
                            break
                    else:
                        companies.append(match.group())
        
        return list(set(companies))  # Remove duplicates