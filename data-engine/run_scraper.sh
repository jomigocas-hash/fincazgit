#!/bin/bash
# Script ejecutado por cron cada noche
cd /media/Disco7/pygrupoamigos/cursoIA/fincaraiz/data-engine

LOG="/media/Disco7/pygrupoamigos/cursoIA/fincaraiz/data-engine/scrape.log"
echo "=== $(date) - Iniciando scraping ===" >> $LOG

PORTALES=("bogota venta 50" "bogota arriendo 30" "medellin venta 20" "cali venta 20" "barranquilla venta 15" "bucaramanga venta 15" "pereira venta 15")

for job in "${PORTALES[@]}"; do
    city=$(echo $job | cut -d' ' -f1)
    op=$(echo $job | cut -d' ' -f2)
    pages=$(echo $job | cut -d' ' -f3)
    echo "$(date) - finca_raiz | $city | $op | $pages páginas" >> $LOG
    venv/bin/python main.py --portal finca_raiz --city $city --operation $op --pages $pages >> $LOG 2>&1
done

echo "=== $(date) - Scraping completo ===" >> $LOG
