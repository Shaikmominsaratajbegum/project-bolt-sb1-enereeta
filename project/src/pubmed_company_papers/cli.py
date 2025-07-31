"""Command-line interface for PubMed paper fetcher."""

import sys
import click
from typing import Optional
import logging

from .fetcher import PubMedFetcher, PubMedAPIError
from .csv_writer import CSVWriter


@click.command()
@click.argument('query', required=True)
@click.option('-h', '--help', 'show_help', is_flag=True, help='Show this help message and exit.')
@click.option('-d', '--debug', is_flag=True, help='Print debug information during execution.')
@click.option('-f', '--file', 'output_file', type=str, help='Specify filename to save results.')
@click.option('--max-results', type=int, default=100, help='Maximum number of results to fetch.')
@click.option('--email', type=str, default='user@example.com', help='Email for PubMed API requests.')
def main(query: str, show_help: bool, debug: bool, output_file: Optional[str], 
         max_results: int, email: str) -> None:
    """
    Fetch research papers from PubMed with pharmaceutical/biotech company affiliations.
    
    QUERY: PubMed search query (supports full PubMed syntax)
    
    Examples:
        get-papers-list "cancer AND drug therapy"
        get-papers-list "COVID-19 AND vaccine" --file results.csv
        get-papers-list "diabetes[MeSH] AND 2023[PDAT]" --debug
    """
    if show_help:
        ctx = click.get_current_context()
        click.echo(ctx.get_help())
        ctx.exit()
    
    # Set up logging
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    
    try:
        # Initialize fetcher
        fetcher = PubMedFetcher(email=email, debug=debug)
        
        # Fetch papers
        click.echo(f"Searching PubMed for: {query}")
        papers = fetcher.fetch_company_papers(query, max_results)
        
        if not papers:
            click.echo("No papers with company affiliations found.")
            return
        
        click.echo(f"Found {len(papers)} papers with company affiliations.")
        
        # Output results
        if output_file:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                CSVWriter.write_results(papers, f)
            click.echo(f"Results saved to {output_file}")
        else:
            # Print to console
            csv_output = CSVWriter.format_results_string(papers)
            click.echo(csv_output)
    
    except PubMedAPIError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        if debug:
            import traceback
            click.echo(f"Unexpected error: {e}", err=True)
            click.echo(traceback.format_exc(), err=True)
        else:
            click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()