"""
Scraper para Metrocuadrado (metrocuadrado.com).
Usa Playwright para renderizar JavaScript y extraer __NEXT_DATA__.
"""
from typing import Generator
from models import Property
from .base_scraper import BaseScraper

BASE_URL = "https://www.metrocuadrado.com"

OPERATION_SLUGS = {"venta": "venta", "arriendo": "arriendo"}

CITY_SLUGS = {
    "bogota":       "bogota",
    "medellin":     "medellin",
    "cali":         "cali",
    "barranquilla": "barranquilla",
    "bucaramanga":  "bucaramanga",
}

# Metrocuadrado devuelve ~24 resultados por página
_PAGE_SIZE = 24


class MetrocuadradoScraper(BaseScraper):

    PORTAL = "metrocuadrado"

    def scrape(self, city: str, operation: str, max_pages: int = 50) -> Generator[Property, None, None]:
        from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

        op_slug   = OPERATION_SLUGS.get(operation, "venta")
        city_slug = CITY_SLUGS.get(city.lower(), city.lower())

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                context = browser.new_context(
                    user_agent=(
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
                    ),
                    locale="es-CO",
                )
                pw_page = context.new_page()
                total_results = None

                for page in range(1, max_pages + 1):
                    url = f"{BASE_URL}/{op_slug}/inmuebles/{city_slug}/?page={page}"
                    self.logger.info(f"Scraping página {page} | {url}")

                    # Retry a nivel Playwright para timeouts
                    data = None
                    for attempt in range(1, 4):
                        try:
                            pw_page.goto(url, wait_until="networkidle", timeout=45000)
                            data = self.extract_next_data(pw_page.content())
                            break
                        except PWTimeout:
                            self.logger.warning(f"Timeout página {page}, intento {attempt}/3")
                        except Exception as e:
                            self.logger.error(f"Error página {page}: {e}")
                            break

                    if data is None:
                        break

                    page_props  = data.get("props", {}).get("pageProps", {})
                    search_data = page_props.get("searchResults", {}) or {}
                    listings    = (
                        search_data.get("results", [])
                        or page_props.get("results", [])
                        or []
                    )

                    if not listings:
                        self.logger.info("Sin más resultados.")
                        break

                    # Capturar total en primera página
                    if total_results is None:
                        total_results = search_data.get("totalResults", 0) or 0
                        self.logger.info(f"Total anunciado por portal: {total_results}")

                    for raw in listings:
                        source_id = self.safe_source_id(raw.get("id"))
                        if not source_id:
                            continue
                        try:
                            yield self.parse_listing(raw)
                        except Exception as e:
                            self.logger.warning(f"Error parseando listing {source_id}: {e}")

                    # Parar si ya cubrimos todos los resultados
                    if total_results and page * _PAGE_SIZE >= total_results:
                        self.logger.info("Todos los resultados cubiertos.")
                        break
            finally:
                browser.close()

    def parse_listing(self, raw: dict) -> Property:
        coords = raw.get("coordinates", {}) or {}
        city   = raw.get("city", {}) or {}
        sector = raw.get("sector", {}) or {}
        ptype  = raw.get("propertyType", {}) or {}
        images = [
            img.get("image", "")
            for img in (raw.get("images") or [])
            if isinstance(img, dict) and img.get("image")
        ]

        return Property(
            source_id      = self.safe_source_id(raw.get("id")),
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
            published_at   = self.parse_date(raw.get("createdAt")),
            updated_at     = self.parse_date(raw.get("updatedAt")),
        )
