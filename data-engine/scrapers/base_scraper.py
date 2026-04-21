import time
import logging
import requests
from abc import ABC, abstractmethod
from typing import Generator
from config import SCRAPER_DELAY
from models import Property

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")


class BaseScraper(ABC):
    """Clase base para todos los scrapers de portales."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "es-CO,es;q=0.9",
        })
        self.logger = logging.getLogger(self.__class__.__name__)

    def get(self, url: str, **kwargs) -> requests.Response:
        """GET con delay automático para no saturar el portal."""
        time.sleep(SCRAPER_DELAY)
        response = self.session.get(url, timeout=15, **kwargs)
        response.raise_for_status()
        return response

    @abstractmethod
    def scrape(self, city: str, operation: str, max_pages: int) -> Generator[Property, None, None]:
        """Genera Property objects desde el portal."""
        ...

    @abstractmethod
    def parse_listing(self, raw: dict) -> Property:
        """Convierte un item crudo del portal en un Property."""
        ...
