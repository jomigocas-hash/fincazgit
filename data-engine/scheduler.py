"""
Scheduler automático para ejecutar los scrapers cada noche.
Uso: venv/bin/python scheduler.py
"""
import schedule
import time
import logging
from main import run_pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("scrape.log"),
        logging.StreamHandler(),
    ]
)
logger = logging.getLogger(__name__)

# Configuración de trabajos
JOBS = [
    # Bogotá — ciudad principal, más páginas
    {"portal": "finca_raiz", "city": "bogota",       "operation": "venta",    "pages": 50},
    {"portal": "finca_raiz", "city": "bogota",       "operation": "arriendo", "pages": 30},
    # Otras ciudades
    {"portal": "finca_raiz", "city": "medellin",     "operation": "venta",    "pages": 20},
    {"portal": "finca_raiz", "city": "medellin",     "operation": "arriendo", "pages": 20},
    {"portal": "finca_raiz", "city": "cali",         "operation": "venta",    "pages": 20},
    {"portal": "finca_raiz", "city": "barranquilla", "operation": "venta",    "pages": 15},
    {"portal": "finca_raiz", "city": "bucaramanga",  "operation": "venta",    "pages": 15},
    {"portal": "finca_raiz", "city": "pereira",      "operation": "venta",    "pages": 15},
]


def run_all():
    logger.info("=== Iniciando scraping nocturno ===")
    total = 0
    for job in JOBS:
        try:
            logger.info(f"Scraping: {job['portal']} | {job['city']} | {job['operation']}")
            results = run_pipeline(job["portal"], job["city"], job["operation"], job["pages"])
            if results:
                total += len(results)
        except Exception as e:
            logger.error(f"Error en job {job}: {e}")
    logger.info(f"=== Scraping completo. Total procesados: {total} ===")


# Ejecutar todos los días a las 2:00 AM
schedule.every().day.at("02:00").do(run_all)

logger.info("Scheduler iniciado. Próxima ejecución: 02:00 AM diario.")
logger.info("Presiona Ctrl+C para detener.")

# Solo correr al arrancar si se pasa --now como argumento
import sys
if "--now" in sys.argv:
    logger.info("Flag --now detectado, ejecutando inmediatamente.")
    run_all()

while True:
    schedule.run_pending()
    time.sleep(60)
