import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/inmuebles")

SCRAPER_DELAY = float(os.getenv("SCRAPER_DELAY", "2.0"))  # segundos entre requests
MAX_PAGES = int(os.getenv("MAX_PAGES", "50"))

PORTALS = {
    "finca_raiz": "https://www.fincaraiz.com.co",
    "metrocuadrado": "https://www.metrocuadrado.com",
    "ciencuadras": "https://www.ciencuadras.com",
}

# Categorías normalizadas (estándar MISMO)
PROPERTY_TYPE_MAP = {
    "apto": "apartamento",
    "apartaestudio": "apartamento_estudio",
    "aparta estudio": "apartamento_estudio",
    "casa": "casa",
    "casa lote": "casa_lote",
    "oficina": "oficina",
    "local": "local_comercial",
    "bodega": "bodega",
    "lote": "lote",
    "finca": "finca",
    "apartamento": "apartamento",
}

OPERATION_TYPE_MAP = {
    "venta": "venta",
    "arriendo": "arriendo",
    "alquiler": "arriendo",
    "arrendamiento": "arriendo",
}
