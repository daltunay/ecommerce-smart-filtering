import typing as tp
from abc import ABC, abstractmethod
from urllib.parse import urlparse

import structlog
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from pydantic import BaseModel

logger = structlog.get_logger(__name__)


class ScrapedProduct(BaseModel):
    """Class to hold product data scraped from websites."""

    url: str
    title: str
    description: str
    image_urls: list[str]


class BaseScraper(ABC):
    """Abstract base class for all website scrapers."""

    # Class attributes
    HEADLESS_MODE: bool = True
    SUPPORTED_DOMAINS: list[str] = []

    PAGE_TYPE_PATTERNS: dict[str, dict[str, list[str]]] = {
        "product": {"path_patterns": [], "query_params": []},
        "search": {"path_patterns": [], "query_params": []},
    }

    # Initialization and cleanup
    def __init__(self):
        """Initialize the scraper with browser instance."""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.firefox.launch(headless=self.HEADLESS_MODE)

    def close(self):
        """Close the browser and Playwright instance."""
        self.browser.close()
        self.playwright.stop()

    # Primary public methods
    def scrape_product(self, product_url: str) -> ScrapedProduct:
        """Main method to scrape a product from a given URL."""
        soup = self.fetch_page(product_url)

        try:
            title = self.extract_product_title(soup)
        except Exception as e:
            logger.error("Error extracting title", error=str(e))
            title = ""

        try:
            description = self.extract_product_description(soup)
        except Exception as e:
            logger.error("Error extracting description", error=str(e))
            description = ""

        try:
            image_urls = self.extract_product_images(soup)
        except Exception as e:
            logger.error("Error extracting images", error=str(e))
            image_urls = []

        return ScrapedProduct(
            url=product_url, title=title, description=description, image_urls=image_urls
        )

    def scrape_search(
        self, search_url: str, max_items: int = 5
    ) -> list[ScrapedProduct]:
        """Main method to scrape search results from a given URL."""
        soup = self.fetch_page(search_url)
        product_urls = self.extract_search_results(soup)
        products: list[ScrapedProduct] = []
        for url in product_urls[:max_items]:
            product = self.scrape_product(url)
            products.append(product)
        return products

    # Implementation methods
    def fetch_page(self, url: str) -> BeautifulSoup:
        """Fetch the page content using the instance browser and return a BeautifulSoup object."""
        logger.info(f"Fetching {self.__class__.__name__} page with Playwright", url=url)

        page = self.browser.new_page()
        page.goto(url)
        html_content = page.content()
        page.close()
        return BeautifulSoup(html_content, "html.parser")

    # Class methods
    @classmethod
    def can_handle_url(cls, url: str) -> bool:
        """Check if this scraper can handle the given URL based on supported domains."""
        if not cls.SUPPORTED_DOMAINS:
            return False

        parsed_url = urlparse(url)
        return any(
            parsed_url.netloc.endswith(domain) for domain in cls.SUPPORTED_DOMAINS
        )

    @classmethod
    def find_page_type(cls, url: str) -> tp.Literal["product", "search"] | None:
        """Determine if the URL is a product page or a search page."""
        parsed_url = urlparse(url)

        for page_type, patterns in cls.PAGE_TYPE_PATTERNS.items():
            for pattern in patterns["path_patterns"]:
                if pattern in parsed_url.path.lower():
                    return page_type

            for param in patterns["query_params"]:
                if param in parsed_url.query.lower():
                    return page_type

        return None

    # Abstract methods that subclasses must implement
    @staticmethod
    @abstractmethod
    def extract_product_title(soup: BeautifulSoup) -> str:
        """Extract the product title from the product page."""
        pass

    @staticmethod
    @abstractmethod
    def extract_product_description(soup: BeautifulSoup) -> str:
        """Extract the product description from the product page."""
        pass

    @staticmethod
    @abstractmethod
    def extract_product_images(soup: BeautifulSoup) -> list[str]:
        """Extract the product image URLs from the product page."""
        pass

    @staticmethod
    @abstractmethod
    def extract_search_results(soup: BeautifulSoup) -> list[str]:
        """Extract product URLs from the search results page."""
        pass
