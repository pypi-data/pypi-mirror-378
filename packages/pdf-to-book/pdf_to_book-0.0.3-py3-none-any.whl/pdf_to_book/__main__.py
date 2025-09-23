"""
Entry point for running pdf_to_book as a module.

Usage:
    python -m pdf_to_book input.pdf output.pdf [options]
"""

from .pdf_to_book import cli

if __name__ == "__main__":
    cli()
