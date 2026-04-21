#!/bin/bash
# Ejecuta el scraper para todos los portales y ciudades principales
# Uso: ./scrape_all.sh [venta|arriendo]

set -e
cd "$(dirname "$0")"

OPERATION=${1:-venta}
CITIES=("bogota" "medellin" "cali" "barranquilla")
PORTALS=("finca_raiz" "metrocuadrado" "ciencuadras")

echo "=== Scraping: operación=$OPERATION ==="

for PORTAL in "${PORTALS[@]}"; do
  for CITY in "${CITIES[@]}"; do
    echo ""
    echo ">>> $PORTAL | $CITY | $OPERATION"
    python main.py --portal "$PORTAL" --city "$CITY" --operation "$OPERATION" --pages 5
  done
done

echo ""
echo "=== Scraping completo ==="
