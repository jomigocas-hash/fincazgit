"""
Endpoints de estadísticas de mercado.
Responde preguntas como: precio promedio por m², oferta por barrio, etc.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi import APIRouter, Query
from typing import Optional
from db import get_conn

router = APIRouter()


@router.get("/market-summary")
def market_summary(
    city:           str            = Query(..., description="Ciudad requerida"),
    operation_type: Optional[str]  = Query(None),
    property_type:  Optional[str]  = Query(None),
):
    """Resumen de mercado: precio promedio, mediana, m² promedio, total oferta."""
    filters = ["city = %(city)s", "is_active = TRUE", "price IS NOT NULL"]
    params = {"city": city.lower()}

    if operation_type:
        filters.append("operation_type = %(operation_type)s")
        params["operation_type"] = operation_type
    if property_type:
        filters.append("property_type = %(property_type)s")
        params["property_type"] = property_type

    where = "WHERE " + " AND ".join(filters)

    sql = f"""
        SELECT
            COUNT(*)                            AS total_listings,
            ROUND(AVG(price)::numeric, 0)       AS avg_price,
            ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price)::numeric, 0) AS median_price,
            ROUND(AVG(price_per_m2)::numeric, 0) AS avg_price_per_m2,
            ROUND(AVG(area_m2)::numeric, 1)     AS avg_area_m2,
            MIN(price)                          AS min_price,
            MAX(price)                          AS max_price
        FROM properties {where}
    """

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            row = cur.fetchone()

    return dict(row)


@router.get("/by-neighborhood")
def stats_by_neighborhood(
    city:           str           = Query(...),
    operation_type: Optional[str] = Query(None),
    property_type:  Optional[str] = Query(None),
):
    """Precio promedio por m² agrupado por barrio. Útil para heatmaps."""
    filters = ["city = %(city)s", "is_active = TRUE", "price_per_m2 IS NOT NULL"]
    params = {"city": city.lower()}

    if operation_type:
        filters.append("operation_type = %(operation_type)s")
        params["operation_type"] = operation_type
    if property_type:
        filters.append("property_type = %(property_type)s")
        params["property_type"] = property_type

    where = "WHERE " + " AND ".join(filters)

    sql = f"""
        SELECT
            neighborhood,
            COUNT(*)                             AS listings,
            ROUND(AVG(price_per_m2)::numeric, 0) AS avg_price_per_m2,
            ROUND(AVG(area_m2)::numeric, 1)      AS avg_area_m2
        FROM properties {where}
        GROUP BY neighborhood
        HAVING COUNT(*) >= 1
        ORDER BY avg_price_per_m2 DESC
    """

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()

    return [dict(r) for r in rows]


@router.get("/gap-analysis")
def gap_analysis(city: str = Query(...)):
    """
    Análisis de brecha: qué combinaciones de tipo/habitaciones
    tienen poca oferta vs. alta demanda implícita.
    """
    sql = """
        SELECT
            property_type,
            operation_type,
            bedrooms,
            COUNT(*) AS supply
        FROM properties
        WHERE city = %(city)s AND is_active = TRUE
        GROUP BY property_type, operation_type, bedrooms
        ORDER BY supply ASC
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, {"city": city.lower()})
            rows = cur.fetchall()

    return [dict(r) for r in rows]


@router.get("/freshness")
def data_freshness(city: str = Query(...)):
    """Qué tan frescos están los datos: distribución por antigüedad del anuncio."""
    sql = """
        SELECT
            source_portal,
            COUNT(*) FILTER (WHERE scraped_at >= NOW() - INTERVAL '1 day')  AS last_24h,
            COUNT(*) FILTER (WHERE scraped_at >= NOW() - INTERVAL '7 days') AS last_7d,
            COUNT(*) FILTER (WHERE scraped_at >= NOW() - INTERVAL '30 days') AS last_30d,
            COUNT(*) AS total
        FROM properties
        WHERE city = %(city)s AND is_active = TRUE
        GROUP BY source_portal
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, {"city": city.lower()})
            rows = cur.fetchall()

    return [dict(r) for r in rows]
