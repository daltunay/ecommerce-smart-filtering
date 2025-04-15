import asyncio
import typing as tp
from abc import ABC, abstractmethod
from urllib.parse import urlparse

import structlog
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from analyzer import Product, ProductImage


class BaseScraper(ABC):
    """Abstract base class for all website scrapers."""

    HEADLESS_MODE: bool = True
    SUPPORTED_DOMAINS: list[str] = []

    PAGE_TYPE_PATTERNS: dict[str, list[str]] = {
        "product": [],
        "search": [],
    }

    async def __init__(self):
        """Initialize the scraper with Playwright and browser instances."""
        self.log = structlog.get_logger(scraper=self.__class__.__name__)
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.firefox.launch(headless=self.HEADLESS_MODE)

    @classmethod
    async def create(cls):
        """Factory method to properly create an async instance."""
        instance = cls.__new__(cls)
        await instance.__init__()
        return instance

    async def close(self):
        """Close the browser and Playwright instance."""
        await self.browser.close()
        await self.playwright.stop()

    @classmethod
    def get_vendor_name(cls) -> str:
        """Extract vendor name from the scraper class name."""
        return cls.__name__.replace("Scraper", "").lower()

    async def scrape_product_detail(self, url: str) -> Product:
        """Main method to scrape a product from a given URL."""
        soup = await self.fetch_page(url)

        try:
            title = self.extract_product_title(soup)
        except Exception as e:
            self.log.error("Error extracting title", exception=str(e))
            title = ""

        try:
            description = self.extract_product_description(soup)
        except Exception as e:
            self.log.error("Error extracting description", exception=str(e))
            description = ""

        try:
            image_urls = self.extract_product_images(soup)
            images = [ProductImage(url_or_path=url) for url in image_urls]
        except Exception as e:
            self.log.error("Error extracting images", exception=str(e))
            images = []

        return Product(
            url=url,
            title=title,
            description=description,
            images=images,
        )

    async def scrape_search_results(
        self, url: str, max_products: int = 5
    ) -> list[Product]:
        """Main method to scrape search results from a given URL."""
        soup = await self.fetch_page(url)
        product_urls = self.extract_product_urls(soup)[:max_products]

        products = await asyncio.gather(
            *[self.scrape_product_detail(url) for url in product_urls]
        )

        return products

    async def fetch_page(self, url: str) -> BeautifulSoup:
        """Fetch the page content using the instance browser and return a BeautifulSoup object."""
        self.log.info(
            f"Fetching {self.__class__.__name__} page with Playwright", url=url
        )

        page = await self.browser.new_page()
        await page.goto(url)
        html_content = await page.content()
        await page.close()
        return BeautifulSoup(html_content, "html.parser")

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
            for pattern in patterns:
                if pattern in parsed_url.path.lower():
                    return page_type

        return None

    @staticmethod
    @abstractmethod
    def extract_product_id(url: str) -> int:
        """Extract the product ID from the product URL."""
        pass

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
    def extract_product_urls(soup: BeautifulSoup) -> list[str]:
        """Extract product URLs from the search results page."""
        pass
