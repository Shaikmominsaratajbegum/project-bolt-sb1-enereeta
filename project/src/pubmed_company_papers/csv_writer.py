"""CSV output utilities for paper results."""

import csv
from typing import List, TextIO
from datetime import datetime

from .models import PaperResult


class CSVWriter:
    """Writes paper results to CSV format."""
    
    @staticmethod
    def write_results(papers: List[PaperResult], output_file: TextIO) -> None:
        """
        Write paper results to CSV file.
        
        Args:
            papers: List of paper results to write
            output_file: File object to write to
        """
        fieldnames = [
            "PubmedID",
            "Title", 
            "Publication Date",
            "Non-academic Author(s)",
            "Company Affiliation(s)",
            "Corresponding Author Email"
        ]
        
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        
        for paper in papers:
            writer.writerow({
                "PubmedID": paper.pubmed_id,
                "Title": paper.title,
                "Publication Date": paper.publication_date.strftime('%Y-%m-%d') if paper.publication_date else "",
                "Non-academic Author(s)": "; ".join(paper.non_academic_authors),
                "Company Affiliation(s)": "; ".join(paper.company_affiliations),
                "Corresponding Author Email": paper.corresponding_author_email or ""
            })
    
    @staticmethod
    def format_results_string(papers: List[PaperResult]) -> str:
        """
        Format paper results as CSV string.
        
        Args:
            papers: List of paper results to format
            
        Returns:
            CSV-formatted string
        """
        import io
        
        output = io.StringIO()
        CSVWriter.write_results(papers, output)
        result = output.getvalue()
        output.close()
        
        return result