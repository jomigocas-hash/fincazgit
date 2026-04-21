"""
Orquestador principal del Data Engine.
Ejecuta el pipeline: Scrape → Normalize → Deduplicate → Save
"""
import argparse
import logging
from scrapers import FincaRaizScraper, MetrocuadradoScraper, CiencuadrasScraper
from normalizer import normalize
from deduplicator import deduplicate
from db import bulk_upsert
from config import MAX_PAGES

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

SCRAPERS = {
    "finca_raiz": FincaRaizScraper,
    "metrocuadrado": MetrocuadradoScraper,
    "ciencuadras": CiencuadrasScraper,
}


def run_pipeline(portal: str, city: str, operation: str, max_pages: int):
    logger.info(f"Iniciando pipeline | portal={portal} | ciudad={city} | operación={operation}")

    ScraperClass = SCRAPERS.get(portal)
    if not ScraperClass:
        logger.error(f"Portal '{portal}' no soportado. Disponibles: {list(SCRAPERS.keys())}")
        return

    # 1. Scraping
    scraper = ScraperClass()
    raw_properties = list(scraper.scrape(city, operation, max_pages))
    logger.info(f"Scrapeados: {len(raw_properties)} inmuebles")

    # 2. Normalización
    normalized = [normalize(p) for p in raw_properties]
    logger.info(f"Normalizados: {len(normalized)} inmuebles")

    # 3. Deduplicación
    unique = deduplicate(normalized)
    logger.info(f"Únicos tras deduplicación: {len(unique)} (eliminados: {len(normalized) - len(unique)})")

    # 4. Persistencia
    saved = bulk_upsert(unique)
    logger.info(f"Guardados/actualizados en DB: {saved}")

    return unique


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Data Engine - Scraper de inmuebles Colombia")
    parser.add_argument("--portal",    default="finca_raiz", choices=list(SCRAPERS.keys()))
    parser.add_argument("--city",      default="bogota",     help="Ciudad a scrapear")
    parser.add_argument("--operation", default="venta",      choices=["venta", "arriendo"])
    parser.add_argument("--pages",     default=MAX_PAGES,    type=int)
    args = parser.parse_args()

    run_pipeline(args.portal, args.city, args.operation, args.pages)
