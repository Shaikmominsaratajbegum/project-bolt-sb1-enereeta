"""PubMed Company Papers - A tool to fetch research papers with pharmaceutical/biotech affiliations."""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .fetcher import PubMedFetcher
from .models import PaperResult, AuthorInfo

__all__ = ["PubMedFetcher", "PaperResult", "AuthorInfo"]