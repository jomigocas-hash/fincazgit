"""
Scraper para Ciencuadras (ciencuadras.com).
Usa Playwright para renderizar JavaScript y extraer __NEXT_DATA__.
"""
from typing import Generator
from models import Property
from .base_scraper import BaseScraper

BASE_URL = "https://www.ciencuadras.com"

OPERATION_SLUGS = {"venta": "venta", "arriendo": "arriendo"}

CITY_SLUGS = {
    "bogota":       "bogota",
    "medellin":     "medellin",
    "cali":         "cali",
    "barranquilla": "barranquilla",
    "bucaramanga":  "bucaramanga",
}


class CiencuadrasScraper(BaseScraper):

    PORTAL = "ciencuadras"

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

                for page in range(1, max_pages + 1):
                    url = f"{BASE_URL}/{op_slug}/inmuebles/{city_slug}?pagina={page}"
                    self.logger.info(f"Scraping página {page} | {url}")

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

                    page_props = data.get("props", {}).get("pageProps", {})
                    listings   = (
                        page_props.get("initialData", {}).get("properties", [])
                        or page_props.get("properties", [])
                        or []
                    )

                    if not listings:
                        self.logger.info("Sin más resultados.")
                        break

                    for raw in listings:
                        source_id = self.safe_source_id(raw.get("id"))
                        if not source_id:
                            continue
                        try:
                            yield self.parse_listing(raw)
                        except Exception as e:
                            self.logger.warning(f"Error parseando listing {source_id}: {e}")

                    # Verificar si hay más páginas
                    pagination = page_props.get("initialData", {}).get("pagination", {}) or {}
                    total_pages = pagination.get("totalPages") or pagination.get("lastPage")
                    if total_pages and page >= int(total_pages):
                        self.logger.info("Última página alcanzada.")
                        break
            finally:
                browser.close()

    def parse_listing(self, raw: dict) -> Property:
        location = raw.get("location", {}) or {}
        features = raw.get("features", {}) or {}

        # images puede ser lista de strings o lista de dicts
        raw_images = raw.get("photos", []) or raw.get("images", []) or []
        images = []
        for img in raw_images:
            if isinstance(img, str):
                images.append(img)
            elif isinstance(img, dict):
                images.append(img.get("url") or img.get("image") or "")
        images = [i for i in images if i]  # filtrar vacíos

        return Property(
            source_id      = self.safe_source_id(raw.get("id")),
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
            image_urls     = images,
            url            = f"{BASE_URL}{raw.get('url', '')}",
            published_at   = self.parse_date(raw.get("publishedAt") or raw.get("fechaPublicacion")),
            updated_at     = self.parse_date(raw.get("updatedAt") or raw.get("fechaActualizacion")),
        )
