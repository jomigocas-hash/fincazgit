"""
Scraper para Metrocuadrado (metrocuadrado.com).
Usa Playwright para renderizar JavaScript y extraer __NEXT_DATA__.
"""
import re
import json
from typing import Generator
from datetime import datetime
from models import Property
from .base_scraper import BaseScraper

BASE_URL = "https://www.metrocuadrado.com"

OPERATION_SLUGS = {"venta": "venta", "arriendo": "arriendo"}
CITY_SLUGS = {
    "bogota": "bogota", "medellin": "medellin", "cali": "cali",
    "barranquilla": "barranquilla", "bucaramanga": "bucaramanga",
}


class MetrocuadradoScraper(BaseScraper):

    PORTAL = "metrocuadrado"

    def scrape(self, city: str, operation: str, max_pages: int = 50) -> Generator[Property, None, None]:
        from playwright.sync_api import sync_playwright

        op_slug   = OPERATION_SLUGS.get(operation, "venta")
        city_slug = CITY_SLUGS.get(city.lower(), city.lower())

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
                locale="es-CO",
            )
            page_browser = context.new_page()

            for page in range(1, max_pages + 1):
                url = f"{BASE_URL}/{op_slug}/inmuebles/{city_slug}/?page={page}"
                self.logger.info(f"Scraping página {page} | {url}")

                try:
                    page_browser.goto(url, wait_until="networkidle", timeout=30000)
                    html = page_browser.content()
                    data = self._extract_next_data(html)
                except Exception as e:
                    self.logger.error(f"Error en página {page}: {e}")
                    break

                listings = (
                    data.get("props", {}).get("pageProps", {})
                        .get("searchResults", {}).get("results", [])
                    or data.get("props", {}).get("pageProps", {}).get("results", [])
                    or []
                )

                if not listings:
                    self.logger.info("Sin más resultados.")
                    break

                for raw in listings:
                    try:
                        yield self.parse_listing(raw)
                    except Exception as e:
                        self.logger.warning(f"Error parseando listing: {e}")

                total = (
                    data.get("props", {}).get("pageProps", {})
                        .get("searchResults", {}).get("totalResults", 0) or 0
                )
                if page * 20 >= total:
                    break

            browser.close()

    def parse_listing(self, raw: dict) -> Property:
        coords = raw.get("coordinates", {}) or {}
        images = [img.get("image", "") for img in (raw.get("images") or []) if img.get("image")]
        city   = raw.get("city", {}) or {}
        sector = raw.get("sector", {}) or {}
        ptype  = raw.get("propertyType", {}) or {}

        return Property(
            source_id      = str(raw.get("id", "")),
            source_portal  = self.PORTAL,
            property_type  = ptype.get("nombre", "") if isinstance(ptype, dict) else str(ptype),
            operation_type = raw.get("businessType", ""),
            city           = city.get("nombre", "") if isinstance(city, dict) else str(city),
            neighborhood   = sector.get("nombre", "") if isinstance(sector, dict) else str(sector),
            address        = raw.get("address", ""),
            latitude       = coords.get("lat"),
            longitude      = coords.get("lon"),
            area_m2        = raw.get("area"),
            bedrooms       = raw.get("rooms"),
            bathrooms      = raw.get("bathrooms"),
            parking        = raw.get("garages"),
            floor          = raw.get("piso"),
            stratum        = raw.get("stratum"),
            price          = raw.get("salePrice") or raw.get("rentPrice"),
            admin_fee      = raw.get("adminPrice"),
            title          = raw.get("title", ""),
            description    = raw.get("comment", ""),
            image_urls     = images,
            url            = f"{BASE_URL}{raw.get('link', '')}",
            published_at   = self._parse_date(raw.get("createdAt")),
            updated_at     = self._parse_date(raw.get("updatedAt")),
        )

    def _extract_next_data(self, html: str) -> dict:
        match = re.search(r'<script id="__NEXT_DATA__"[^>]*>({.*?})</script>', html, re.DOTALL)
        if not match:
            raise ValueError("__NEXT_DATA__ no encontrado")
        return json.loads(match.group(1))

    def _parse_date(self, raw) -> datetime | None:
        if not raw:
            return None
        try:
            return datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
        except Exception:
            return None
