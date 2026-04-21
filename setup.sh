#!/bin/bash
set -e

echo "=== Inmuebles Colombia - Setup ==="

# 1. Levantar base de datos
echo ""
echo "[1/4] Levantando PostgreSQL + PostGIS..."
docker compose up db -d

echo "Esperando que la DB esté lista..."
until docker compose exec db pg_isready -U inmuebles_user -d inmuebles > /dev/null 2>&1; do
  sleep 2
done
echo "DB lista."

# 2. Levantar API
echo ""
echo "[2/4] Levantando API..."
docker compose up api -d
sleep 3

# 3. Verificar API
echo ""
echo "[3/4] Verificando API..."
if curl -s http://localhost:8000/health | grep -q "ok"; then
  echo "API OK en http://localhost:8000"
else
  echo "ADVERTENCIA: La API no respondió. Revisa: docker compose logs api"
fi

# 4. Instrucciones finales
echo ""
echo "[4/4] Setup completo."
echo ""
echo "Próximos pasos:"
echo "  Correr scraper:  cd data-engine && python main.py --portal finca_raiz --city bogota --operation venta"
echo "  Frontend:        cd frontend && npm run dev"
echo "  Ver logs API:    docker compose logs -f api"
echo "  Ver logs DB:     docker compose logs -f db"
echo ""
echo "URLs:"
echo "  API:      http://localhost:8000"
echo "  API docs: http://localhost:8000/docs"
echo "  Frontend: http://localhost:3000 (correr manualmente)"
