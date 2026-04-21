# Inmuebles Colombia

Plataforma de datos inmobiliarios normalizados y deduplicados para el mercado colombiano.

## Requisitos

- Docker y Docker Compose
- Python 3.12+ (para correr scrapers localmente)
- Node.js 20+ (para el frontend en desarrollo)

## Inicio rápido

```bash
# 1. Levantar DB + API
./setup.sh

# 2. Correr el frontend
cd frontend && npm install && npm run dev

# 3. Poblar datos (en otra terminal)
cd data-engine
pip install -r requirements.txt
python main.py --portal finca_raiz --city bogota --operation venta
```

Abre http://localhost:3000

## Estructura

```
├── api/              FastAPI — endpoints REST
├── data-engine/      Scrapers + pipeline de datos
│   ├── scrapers/     Finca Raíz, Metrocuadrado, Ciencuadras
│   ├── normalizer/   Estandarización de tipos y precios
│   ├── deduplicator/ Algoritmo de identidad de inmuebles
│   └── db/           Schema SQL y repositorio
├── frontend/         Next.js — interfaz web
└── docker-compose.yml
```

## Comandos útiles

```bash
# Ver API docs interactivos
open http://localhost:8000/docs

# Scraper completo (todos los portales y ciudades)
cd data-engine && ./scrape_all.sh venta

# Logs
docker compose logs -f api
docker compose logs -f db

# Reiniciar todo
docker compose down && ./setup.sh
```

## Variables de entorno

| Archivo | Variable | Descripción |
|---|---|---|
| `api/.env` | `DATABASE_URL` | Conexión PostgreSQL |
| `data-engine/.env` | `DATABASE_URL` | Conexión PostgreSQL |
| `data-engine/.env` | `SCRAPER_DELAY` | Segundos entre requests (default: 2) |
| `data-engine/.env` | `MAX_PAGES` | Páginas máximas por scraper (default: 10) |
| `frontend/.env.local` | `NEXT_PUBLIC_API_URL` | URL de la API |
