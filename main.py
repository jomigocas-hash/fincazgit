from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import properties, stats, matching, price_score

app = FastAPI(
    title="Inmuebles Colombia API",
    description="API de datos inmobiliarios normalizados y deduplicados",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(properties.router,   prefix="/properties",   tags=["Propiedades"])
app.include_router(stats.router,        prefix="/stats",        tags=["Estadísticas"])
app.include_router(matching.router,     prefix="/matching",     tags=["Matching"])
app.include_router(price_score.router,  prefix="/price-score",  tags=["Score de Precio"])


@app.get("/health")
def health():
    return {"status": "ok"}
