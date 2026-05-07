"""
Scraper para Finca Raíz (fincaraiz.com.co).
Lee los datos desde __NEXT_DATA__ inyectado por Next.js en el HTML.
"""
from typing import Generator
from models import Property
from .base_scraper import BaseScraper

BASE_URL = "https://www.fincaraiz.com.co"

OPERATION_SLUGS = {"venta": "venta", "arriendo": "arriendo"}

CITY_SLUGS = {
    "bogota":       "bogota-d-c",
    "medellin":     "medellin",
    "cali":         "cali",
    "barranquilla": "barranquilla",
    "cartagena":    "cartagena",
    "bucaramanga":  "bucaramanga",
    "pereira":      "pereira",
}


class FincaRaizScraper(BaseScraper):

    PORTAL = "finca_raiz"

    def scrape(self, city: str, operation: str, max_pages: int = 50) -> Generator[Property, None, None]:
        op_slug   = OPERATION_SLUGS.get(operation, "venta")
        city_slug = CITY_SLUGS.get(city.lower(), city.lower())
        page = 1

        while page <= max_pages:
            url = f"{BASE_URL}/{op_slug}/inmuebles/{city_slug}/?page={page}"
            self.logger.info(f"Scraping página {page} | {url}")

            try:
                response = self.get(url)
                data = self.extract_next_data(response.text)
            except Exception as e:
                self.logger.error(f"Error en página {page}: {e}")
                break

            search_fast = (
                data.get("props", {})
                    .get("pageProps", {})
                    .get("fetchResult", {})
                    .get("searchFast", {})
            )
            listings = search_fast.get("data", []) or []

            if not listings:
                self.logger.info("Sin más resultados.")
                break

            for raw in listings:
                source_id = self.safe_source_id(raw.get("id"))
                if not source_id:
                    self.logger.warning("Listing sin ID, omitiendo.")
                    continue
                try:
                    yield self.parse_listing(raw)
                except Exception as e:
                    self.logger.warning(f"Error parseando listing {source_id}: {e}")

            if not search_fast.get("paginatorInfo", {}).get("hasMorePages", False):
                self.logger.info("Última página alcanzada.")
                break

            page += 1

    def parse_listing(self, raw: dict) -> Property:
        price_data = raw.get("price", {}) or {}
        locations  = raw.get("locations", {}) or {}
        images     = [
            img.get("image", "")
            for img in (raw.get("images") or [])
            if img.get("image")
        ]

        city_name    = ""
        neighborhood = ""
        city_list    = locations.get("city", []) or []
        neigh_list   = locations.get("neighbourhood", []) or []
        loc_main     = locations.get("location_main", {}) or {}

        if city_list:
            city_name = city_list[0].get("name", "")
        if neigh_list:
            neighborhood = neigh_list[0].get("name", "")
        elif loc_main:
            neighborhood = loc_main.get("name", "")

        prop_type = raw.get("property_type", {})
        op_type   = raw.get("operation_type", {})
        if isinstance(prop_type, dict):
            prop_type = prop_type.get("name", "")
        if isinstance(op_type, dict):
            op_type = op_type.get("name", "")

        admin_fee_raw = raw.get("commonExpenses", {}) or {}
        admin_fee = admin_fee_raw.get("amount") if isinstance(admin_fee_raw, dict) else admin_fee_raw

        return Property(
            source_id      = self.safe_source_id(raw.get("id")),
            source_portal  = self.PORTAL,
            property_type  = prop_type,
            operation_type = op_type,
            city           = city_name,
            neighborhood   = neighborhood,
            address        = raw.get("address", "") if raw.get("showAddress") else "",
            latitude       = raw.get("latitude"),
            longitude      = raw.get("longitude"),
            area_m2        = raw.get("m2") or raw.get("m2Built"),
            bedrooms       = raw.get("bedrooms") or raw.get("rooms"),
            bathrooms      = raw.get("bathrooms"),
            parking        = raw.get("garage"),
            floor          = raw.get("floor") or None,
            stratum        = raw.get("stratum"),
            price          = price_data.get("amount"),
            admin_fee      = admin_fee,
            title          = raw.get("title", ""),
            description    = raw.get("description", ""),
            image_urls     = images,
            url            = f"{BASE_URL}{raw.get('link', '')}",
            published_at   = self.parse_date(raw.get("created_at")),
            updated_at     = self.parse_date(raw.get("updated_at")),
        )
