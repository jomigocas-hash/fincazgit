import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import properties, stats, matching
from db import get_conn
from auth import APIKeyMiddleware

logger = logging.getLogger(__name__)

SCHEMA_FILES = [
    os.path.join(os.path.dirname(__file__), "schema", "schema.sql"),
    os.path.join(os.path.dirname(__file__), "schema", "schema_matching.sql"),
]


def _run_migrations():
    """Ejecuta los archivos SQL de schema al arrancar (idempotente por IF NOT EXISTS)."""
    for path in SCHEMA_FILES:
        if not os.path.exists(path):
            logger.warning(f"Schema file not found, skipping: {path}")
            continue
        with open(path, "r") as f:
            sql = f.read()
        try:
            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(sql)
                conn.commit()
            logger.info(f"Migration applied: {os.path.basename(path)}")
        except Exception as e:
            logger.error(f"Error applying {os.path.basename(path)}: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    _run_migrations()
    yield


app = FastAPI(
    title="Inmuebles Colombia API",
    description="API de datos inmobiliarios normalizados y deduplicados",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(APIKeyMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(properties.router, prefix="/properties", tags=["Propiedades"])
app.include_router(stats.router,      prefix="/stats",      tags=["Estadísticas"])
app.include_router(matching.router,   prefix="/matching",   tags=["Matching"])


@app.get("/health")
def health():
    return {"status": "ok"}
