"""
Scraper para Ciencuadras (ciencuadras.com).
Usa Playwright para renderizar JavaScript y extraer datos.
"""
import re
import json
from typing import Generator
from datetime import datetime
from models import Property
from .base_scraper import BaseScraper

BASE_URL = "https://www.ciencuadras.com"

OPERATION_SLUGS = {"venta": "venta", "arriendo": "arriendo"}
CITY_SLUGS = {
    "bogota": "bogota", "medellin": "medellin", "cali": "cali",
    "barranquilla": "barranquilla", "bucaramanga": "bucaramanga",
}


class CiencuadrasScraper(BaseScraper):

    PORTAL = "ciencuadras"

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
                url = f"{BASE_URL}/{op_slug}/inmuebles/{city_slug}?pagina={page}"
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
                        .get("initialData", {}).get("properties", [])
                    or data.get("props", {}).get("pageProps", {}).get("properties", [])
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

                page += 1

            browser.close()

    def parse_listing(self, raw: dict) -> Property:
        location = raw.get("location", {}) or {}
        features = raw.get("features", {}) or {}
        images   = raw.get("photos", []) or raw.get("images", []) or []

        return Property(
            source_id      = str(raw.get("id", "")),
            source_portal  = self.PORTAL,
            property_type  = raw.get("propertyType", "") or raw.get("tipo", ""),
            operation_type = raw.get("offerType", "") or raw.get("tipoNegocio", ""),
            city           = location.get("city", "") or raw.get("ciudad", ""),
            neighborhood   = location.get("neighborhood", "") or raw.get("barrio", ""),
            address        = location.get("address", "") or raw.get("direccion", ""),
            latitude       = location.get("lat") or raw.get("latitud"),
            longitude      = location.get("lng") or raw.get("longitud"),
            area_m2        = features.get("area") or raw.get("area"),
            bedrooms       = features.get("bedrooms") or raw.get("habitaciones"),
            bathrooms      = features.get("bathrooms") or raw.get("banos"),
            parking        = features.get("parking") or raw.get("garajes"),
            floor          = features.get("floor") or raw.get("piso"),
            stratum        = raw.get("stratum") or raw.get("estrato"),
            price          = raw.get("price") or raw.get("precio"),
            admin_fee      = raw.get("adminFee") or raw.get("administracion"),
            title          = raw.get("title", "") or raw.get("titulo", ""),
            description    = raw.get("description", "") or raw.get("descripcion", ""),
            image_urls     = images if isinstance(images, list) else [],
            url            = f"{BASE_URL}{raw.get('url', '')}",
            published_at   = self._parse_date(raw.get("publishedAt") or raw.get("fechaPublicacion")),
            updated_at     = self._parse_date(raw.get("updatedAt") or raw.get("fechaActualizacion")),
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
