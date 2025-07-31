"""PubMed API fetcher for research papers."""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Optional, Dict, Any
import logging
import time
import re
from email_validator import validate_email, EmailNotValidError

from .models import PaperResult, AuthorInfo
from .company_detector import CompanyDetector


class PubMedAPIError(Exception):
    """Exception raised for PubMed API errors."""
    pass


class PubMedFetcher:
    """Fetches research papers from PubMed API and identifies company affiliations."""
    
    def __init__(self, email: str = "user@example.com", debug: bool = False) -> None:
        """
        Initialize the PubMed fetcher.
        
        Args:
            email: Email address for PubMed API requests (required for large queries)
            debug: Enable debug logging
        """
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.email = email
        self.company_detector = CompanyDetector()
        
        # Set up logging
        logging.basicConfig(
            level=logging.DEBUG if debug else logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # API rate limiting
        self.request_delay = 0.34  # ~3 requests per second as recommended by NCBI
    
    def search_papers(self, query: str, max_results: int = 100) -> List[str]:
        """
        Search for papers using PubMed API.
        
        Args:
            query: PubMed search query
            max_results: Maximum number of results to return
            
        Returns:
            List of PubMed IDs
            
        Raises:
            PubMedAPIError: If the API request fails
        """
        self.logger.info(f"Searching PubMed with query: {query}")
        
        search_url = f"{self.base_url}/esearch.fcgi"
        params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "xml",
            "email": self.email,
            "tool": "pubmed_company_papers"
        }
        
        try:
            response = requests.get(search_url, params=params, timeout=30)
            response.raise_for_status()
        except requests.RequestException as e:
            raise PubMedAPIError(f"Failed to search PubMed: {e}")
        
        time.sleep(self.request_delay)
        
        try:
            root = ET.fromstring(response.content)
            id_list = root.find(".//IdList")
            if id_list is None:
                return []
            
            pmids = [id_elem.text for id_elem in id_list.findall("Id") if id_elem.text]
            self.logger.info(f"Found {len(pmids)} papers")
            return pmids
            
        except ET.ParseError as e:
            raise PubMedAPIError(f"Failed to parse search results: {e}")
    
    def fetch_paper_details(self, pmids: List[str]) -> List[PaperResult]:
        """
        Fetch detailed information for papers by PubMed IDs.
        
        Args:
            pmids: List of PubMed IDs
            
        Returns:
            List of PaperResult objects
            
        Raises:
            PubMedAPIError: If the API request fails
        """
        if not pmids:
            return []
        
        self.logger.info(f"Fetching details for {len(pmids)} papers")
        
        # Process in batches to avoid URL length limits
        batch_size = 200
        all_results = []
        
        for i in range(0, len(pmids), batch_size):
            batch = pmids[i:i + batch_size]
            results = self._fetch_batch_details(batch)
            all_results.extend(results)
            
            if i + batch_size < len(pmids):
                time.sleep(self.request_delay)
        
        return all_results
    
    def _fetch_batch_details(self, pmids: List[str]) -> List[PaperResult]:
        """Fetch details for a batch of PubMed IDs."""
        fetch_url = f"{self.base_url}/efetch.fcgi"
        params = {
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "xml",
            "email": self.email,
            "tool": "pubmed_company_papers"
        }
        
        try:
            response = requests.get(fetch_url, params=params, timeout=60)
            response.raise_for_status()
        except requests.RequestException as e:
            raise PubMedAPIError(f"Failed to fetch paper details: {e}")
        
        try:
            root = ET.fromstring(response.content)
            return self._parse_paper_details(root)
        except ET.ParseError as e:
            raise PubMedAPIError(f"Failed to parse paper details: {e}")
    
    def _parse_paper_details(self, root: ET.Element) -> List[PaperResult]:
        """Parse paper details from XML response."""
        results = []
        
        for article in root.findall(".//PubmedArticle"):
            try:
                result = self._parse_single_paper(article)
                if result:
                    results.append(result)
            except Exception as e:
                self.logger.warning(f"Failed to parse paper: {e}")
                continue
        
        return results
    
    def _parse_single_paper(self, article: ET.Element) -> Optional[PaperResult]:
        """Parse a single paper from XML."""
        # Get PubMed ID
        pmid_elem = article.find(".//PMID")
        if pmid_elem is None or pmid_elem.text is None:
            return None
        pmid = pmid_elem.text
        
        # Get title
        title_elem = article.find(".//ArticleTitle")
        title = title_elem.text if title_elem is not None and title_elem.text else "No title"
        
        # Get publication date
        pub_date = self._extract_publication_date(article)
        
        # Get authors
        authors = self._extract_authors(article)
        
        # Filter for papers with company affiliations
        non_academic_authors = []
        company_affiliations = []
        corresponding_author_email = None
        
        has_company_author = False
        
        for author in authors:
            if self.company_detector.is_company_affiliation(author.affiliation, author.email):
                author.is_non_academic = True
                has_company_author = True
                non_academic_authors.append(author.name)
                
                # Extract company names
                companies = self.company_detector.extract_company_names(author.affiliation)
                company_affiliations.extend(companies)
            
            if author.is_corresponding and author.email:
                corresponding_author_email = author.email
        
        # Only return papers with at least one company-affiliated author
        if not has_company_author:
            return None
        
        return PaperResult(
            pubmed_id=pmid,
            title=title,
            publication_date=pub_date,
            authors=authors,
            non_academic_authors=list(set(non_academic_authors)),
            company_affiliations=list(set(company_affiliations)),
            corresponding_author_email=corresponding_author_email
        )
    
    def _extract_publication_date(self, article: ET.Element) -> Optional[datetime]:
        """Extract publication date from article XML."""
        # Try different date elements
        date_elements = [
            ".//PubDate",
            ".//ArticleDate[@DateType='Electronic']",
            ".//DateCompleted",
            ".//DateRevised"
        ]
        
        for date_path in date_elements:
            date_elem = article.find(date_path)
            if date_elem is not None:
                year_elem = date_elem.find("Year")
                month_elem = date_elem.find("Month")
                day_elem = date_elem.find("Day")
                
                if year_elem is not None and year_elem.text:
                    try:
                        year = int(year_elem.text)
                        month = int(month_elem.text) if month_elem is not None and month_elem.text else 1
                        day = int(day_elem.text) if day_elem is not None and day_elem.text else 1
                        return datetime(year, month, day)
                    except (ValueError, TypeError):
                        continue
        
        return None
    
    def _extract_authors(self, article: ET.Element) -> List[AuthorInfo]:
        """Extract author information from article XML."""
        authors = []
        
        author_list = article.find(".//AuthorList")
        if author_list is None:
            return authors
        
        for author_elem in author_list.findall("Author"):
            name = self._extract_author_name(author_elem)
            if not name:
                continue
            
            # Extract affiliation
            affiliation = self._extract_affiliation(author_elem)
            
            # Check if corresponding author
            is_corresponding = self._is_corresponding_author(author_elem)
            
            # Extract email if available
            email = self._extract_email(author_elem, article)
            
            authors.append(AuthorInfo(
                name=name,
                affiliation=affiliation,
                email=email,
                is_corresponding=is_corresponding
            ))
        
        return authors
    
    def _extract_author_name(self, author_elem: ET.Element) -> Optional[str]:
        """Extract author name from author element."""
        last_name = author_elem.find("LastName")
        first_name = author_elem.find("ForeName")
        initials = author_elem.find("Initials")
        
        if last_name is not None and last_name.text:
            name_parts = [last_name.text]
            
            if first_name is not None and first_name.text:
                name_parts.append(first_name.text)
            elif initials is not None and initials.text:
                name_parts.append(initials.text)
            
            return ", ".join(name_parts)
        
        # Try collective name
        collective_name = author_elem.find("CollectiveName")
        if collective_name is not None and collective_name.text:
            return collective_name.text
        
        return None
    
    def _extract_affiliation(self, author_elem: ET.Element) -> Optional[str]:
        """Extract affiliation from author element."""
        affiliation_info = author_elem.find(".//AffiliationInfo/Affiliation")
        if affiliation_info is not None and affiliation_info.text:
            return affiliation_info.text.strip()
        return None
    
    def _is_corresponding_author(self, author_elem: ET.Element) -> bool:
        """Check if author is corresponding author."""
        # This is a heuristic - PubMed doesn't always mark corresponding authors clearly
        affiliation = self._extract_affiliation(author_elem)
        if affiliation and "corresponding" in affiliation.lower():
            return True
        return False
    
    def _extract_email(self, author_elem: ET.Element, article: ET.Element) -> Optional[str]:
        """Extract email address from author or article information."""
        # Look for email in affiliation
        affiliation = self._extract_affiliation(author_elem)
        if affiliation:
            email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', affiliation)
            if email_match:
                email = email_match.group()
                try:
                    validate_email(email)
                    return email
                except EmailNotValidError:
                    pass
        
        return None
    
    def fetch_company_papers(self, query: str, max_results: int = 100) -> List[PaperResult]:
        """
        Fetch papers with company affiliations based on a search query.
        
        Args:
            query: PubMed search query
            max_results: Maximum number of results to fetch
            
        Returns:
            List of papers with at least one company-affiliated author
        """
        pmids = self.search_papers(query, max_results)
        if not pmids:
            self.logger.info("No papers found for query")
            return []
        
        papers = self.fetch_paper_details(pmids)
        self.logger.info(f"Found {len(papers)} papers with company affiliations")
        
        return papers