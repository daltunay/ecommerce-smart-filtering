import structlog

from analyzer import Product

from .base import BaseScraper
from .websites.ebay import EbayScraper
from .websites.leboncoin import LeboncoinScraper
from .websites.vinted import VintedScraper

SCRAPERS: list[BaseScraper] = [
    LeboncoinScraper,
    VintedScraper,
    EbayScraper,
]

log = structlog.get_logger()


def get_scraper_class_for_url(url: str) -> type[BaseScraper] | None:
    """Find a suitable scraper class for the given URL."""
    for scraper_class in SCRAPERS:
        if scraper_class.can_handle_url(url):
            return scraper_class
    return None


def get_page_type(url: str) -> str | None:
    """Determine if the URL is for a product or a search page."""
    scraper_class = get_scraper_class_for_url(url)
    if scraper_class:
        return scraper_class.find_page_type(url)
    return None


def scrape_product(url: str) -> Product | None:
    """Scrape a product from the given URL (CLI use only)."""
    scraper_cls = get_scraper_class_for_url(url)
    if not scraper_cls:
        return None
    scraper = scraper_cls()

    try:
        return scraper.scrape_product_detail(url)
    finally:
        scraper.close()


def scrape_search_page(url: str, max_products: int = 5) -> list[Product]:
    """Scrape search results from the given URL (CLI use only)."""
    scraper_cls = get_scraper_class_for_url(url)
    if not scraper_cls:
        return []
    scraper = scraper_cls()

    try:
        return scraper.scrape_search_results(url, max_products=max_products)
    finally:
        scraper.close()
