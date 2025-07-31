# PubMed Company Papers Fetcher

A Python program to fetch research papers from PubMed and identify papers with at least one author affiliated with pharmaceutical or biotech companies.

## Features

- Fetch papers using the PubMed API with full query syntax support
- Identify papers with pharmaceutical/biotech company affiliations using advanced heuristics
- Export results to CSV format with comprehensive paper information
- Command-line interface with flexible options
- Typed Python with comprehensive error handling
- Modular architecture for easy extension and testing

## Installation

This project uses [Poetry](https://python-poetry.org/) for dependency management. Make sure you have Poetry installed on your system.

### Clone the repository

```bash
git clone <repository-url>
cd pubmed-company-papers
```

### Install dependencies

```bash
poetry install
```

This will create a virtual environment and install all required dependencies.

## Usage

### Command Line Interface

The program provides an executable command `get-papers-list` after installation:

```bash
# Basic usage
poetry run get-papers-list "cancer AND drug therapy"

# Save results to a file
poetry run get-papers-list "COVID-19 AND vaccine" --file results.csv

# Enable debug mode
poetry run get-papers-list "diabetes[MeSH] AND 2023[PDAT]" --debug

# Limit number of results
poetry run get-papers-list "immunotherapy" --max-results 50 --file immuno.csv

# Show help
poetry run get-papers-list --help
```

### Command Line Options

- `-h, --help`: Display usage instructions
- `-d, --debug`: Print debug information during execution
- `-f, --file FILENAME`: Specify filename to save results (prints to console if not provided)
- `--max-results NUMBER`: Maximum number of results to fetch (default: 100)
- `--email EMAIL`: Email address for PubMed API requests (default: user@example.com)

### PubMed Query Syntax

The program supports PubMed's full query syntax:

```bash
# Search by topic
get-papers-list "breast cancer"

# Use MeSH terms
get-papers-list "Diabetes Mellitus[MeSH]"

# Combine with publication date
get-papers-list "COVID-19 AND 2023[PDAT]"

# Search by author
get-papers-list "Smith J[Author]"

# Complex queries with Boolean operators
get-papers-list "(cancer OR tumor) AND (immunotherapy OR immunology) AND 2022:2023[PDAT]"
```

### Using as a Python Module

```python
from pubmed_company_papers import PubMedFetcher

# Initialize fetcher
fetcher = PubMedFetcher(email="your.email@example.com", debug=True)

# Search for papers
papers = fetcher.fetch_company_papers("cancer AND drug therapy", max_results=50)

# Process results
for paper in papers:
    print(f"Title: {paper.title}")
    print(f"PubMed ID: {paper.pubmed_id}")
    print(f"Company Authors: {', '.join(paper.non_academic_authors)}")
    print(f"Companies: {', '.join(paper.company_affiliations)}")
    print("---")
```

## Output Format

The program outputs a CSV file with the following columns:

- **PubmedID**: Unique identifier for the paper
- **Title**: Title of the paper
- **Publication Date**: Date the paper was published (YYYY-MM-DD format)
- **Non-academic Author(s)**: Names of authors affiliated with non-academic institutions (semicolon-separated)
- **Company Affiliation(s)**: Names of pharmaceutical/biotech companies (semicolon-separated)
- **Corresponding Author Email**: Email address of the corresponding author

## Company Detection Algorithm

The program uses sophisticated heuristics to identify pharmaceutical and biotech companies:

### Known Companies Database
- Major pharmaceutical companies (Pfizer, J&J, Roche, Novartis, etc.)
- Biotech companies (Genentech, Moderna, BioNTech, etc.)
- Generic industry terms (pharmaceuticals, biotech, therapeutics, etc.)

### Detection Methods
1. **Known Company Matching**: Direct matching against a comprehensive database of pharmaceutical and biotech companies
2. **Email Domain Analysis**: Checking author email domains against known company domains
3. **Pattern Recognition**: Identifying company-like patterns in affiliations (Inc., Corp., Ltd., etc.)
4. **Academic Institution Exclusion**: Filtering out clearly academic institutions (universities, hospitals, research centers)

### Scoring System
The algorithm uses a scoring system to differentiate between academic and industry affiliations when both indicators are present.

## Code Organization

```
src/pubmed_company_papers/
├── __init__.py              # Package initialization and exports
├── models.py                # Data models (PaperResult, AuthorInfo)
├── fetcher.py              # Main PubMed API interaction and paper fetching
├── company_detector.py     # Company affiliation detection logic
├── csv_writer.py           # CSV output formatting
└── cli.py                  # Command-line interface
```

### Architecture Principles

- **Separation of Concerns**: Each module has a single, well-defined responsibility
- **Type Safety**: Comprehensive type hints throughout the codebase
- **Error Handling**: Robust error handling with specific exception types
- **Logging**: Configurable logging for debugging and monitoring
- **Testability**: Modular design enables easy unit testing

## Dependencies

### Core Dependencies
- **requests**: HTTP client for PubMed API calls
- **pandas**: Data manipulation and analysis
- **click**: Command-line interface framework
- **lxml**: XML parsing for PubMed responses
- **email-validator**: Email address validation

### Development Dependencies
- **pytest**: Testing framework
- **black**: Code formatting
- **mypy**: Static type checking
- **flake8**: Code linting

## Error Handling

The program includes comprehensive error handling for:

- Invalid PubMed queries
- API failures and timeouts
- Network connectivity issues
- XML parsing errors
- File I/O errors
- Invalid email addresses

## Performance Considerations

- **Rate Limiting**: Respects PubMed's API rate limits (~3 requests per second)
- **Batch Processing**: Processes papers in batches to optimize API usage
- **Efficient Parsing**: Uses streaming XML parsing for large datasets
- **Memory Management**: Processes results incrementally to handle large result sets

## Development Tools Used

This project was developed with assistance from:

- **Claude 4 (Sonnet)**: AI assistant for code generation and architecture design
- **Python Standard Library**: Core functionality
- **Poetry**: Dependency management and packaging
- **Git**: Version control

## Testing

Run tests with:

```bash
poetry run pytest
```

Run type checking:

```bash
poetry run mypy src/
```

Format code:

```bash
poetry run black src/
```

Lint code:

```bash
poetry run flake8 src/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite and type checking
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Bonus Features

### Module Structure
The project is organized as a proper Python package with:
- Separate module (`pubmed_company_papers`) and CLI interface
- Clean separation between core functionality and command-line interface
- Importable classes and functions for programmatic use

### Test PyPI Publishing
To publish to Test PyPI:

```bash
poetry config repositories.test-pypi https://test.pypi.org/legacy/
poetry config pypi-token.test-pypi <your-test-pypi-token>
poetry build
poetry publish -r test-pypi
```

## Support

For issues, questions, or contributions, please create an issue on the GitHub repository.