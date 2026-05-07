import re
import json
import time
import logging
import requests
from abc import ABC, abstractmethod
from typing import Generator
from datetime import datetime
from config import SCRAPER_DELAY
from models import Property

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")

# Códigos HTTP que ameritan retry
_RETRY_STATUSES = {429, 500, 502, 503, 504}
_MAX_RETRIES = 3


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
        """GET con delay automático y retry con backoff exponencial."""
        time.sleep(SCRAPER_DELAY)
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                response = self.session.get(url, timeout=15, **kwargs)
                if response.status_code in _RETRY_STATUSES:
                    wait = 2 ** attempt
                    self.logger.warning(
                        f"HTTP {response.status_code} en {url} — reintento {attempt}/{_MAX_RETRIES} en {wait}s"
                    )
                    time.sleep(wait)
                    continue
                response.raise_for_status()
                return response
            except requests.exceptions.Timeout:
                wait = 2 ** attempt
                self.logger.warning(f"Timeout en {url} — reintento {attempt}/{_MAX_RETRIES} en {wait}s")
                time.sleep(wait)
            except requests.exceptions.RequestException as e:
                if attempt == _MAX_RETRIES:
                    raise
                wait = 2 ** attempt
                self.logger.warning(f"Error de red en {url}: {e} — reintento {attempt}/{_MAX_RETRIES} en {wait}s")
                time.sleep(wait)
        raise requests.exceptions.RetryError(f"Falló después de {_MAX_RETRIES} intentos: {url}")

    def extract_next_data(self, html: str) -> dict:
        """Extrae el JSON de __NEXT_DATA__ inyectado por Next.js."""
        match = re.search(
            r'<script[^>]+id=["\']__NEXT_DATA__["\'][^>]*>(.*?)</script>',
            html, re.DOTALL
        )
        if not match:
            raise ValueError("__NEXT_DATA__ no encontrado en el HTML")
        return json.loads(match.group(1))

    def parse_date(self, raw) -> datetime | None:
        """Convierte string ISO a datetime, retorna None si falla."""
        if not raw:
            return None
        try:
            return datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
        except Exception:
            return None

    def safe_source_id(self, raw_id) -> str | None:
        """Retorna el source_id como string, o None si está vacío."""
        if raw_id is None:
            return None
        sid = str(raw_id).strip()
        return sid if sid else None

    @abstractmethod
    def scrape(self, city: str, operation: str, max_pages: int) -> Generator[Property, None, None]:
        """Genera Property objects desde el portal."""
        ...

    @abstractmethod
    def parse_listing(self, raw: dict) -> Property:
        """Convierte un item crudo del portal en un Property."""
        ...
