"""
Score de precio: indica si un inmueble está caro o barato vs el mercado de su zona.
Compara price_per_m2 del inmueble contra el promedio del barrio/ciudad.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi import APIRouter, HTTPException
from db import get_conn

router = APIRouter()


def calculate_price_score(property_id: int) -> dict:
    """Calcula el score de precio para un inmueble."""

    # 1. Obtener datos del inmueble
    sql_prop = """
        SELECT id, city, neighborhood, property_type, operation_type,
               price, area_m2, price_per_m2
        FROM properties
        WHERE id = %(id)s AND is_active = TRUE
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql_prop, {"id": property_id})
            prop = cur.fetchone()

    if not prop:
        raise HTTPException(status_code=404, detail="Inmueble no encontrado")

    prop = dict(prop)
    if not prop["price_per_m2"]:
        return {**prop, "score": None, "label": "Sin datos suficientes",
                "diff_pct": None, "market_avg_m2": None, "sample_size": 0}

    # 2. Calcular promedio del barrio (mínimo 3 inmuebles similares)
    sql_market = """
        SELECT
            COUNT(*)                             AS sample_size,
            AVG(price_per_m2)                    AS avg_m2,
            PERCENTILE_CONT(0.5) WITHIN GROUP
                (ORDER BY price_per_m2)          AS median_m2
        FROM properties
        WHERE city           = %(city)s
          AND property_type  = %(property_type)s
          AND operation_type = %(operation_type)s
          AND neighborhood   = %(neighborhood)s
          AND is_active      = TRUE
          AND price_per_m2   IS NOT NULL
          AND id             != %(id)s
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql_market, {
                "city":           prop["city"],
                "property_type":  prop["property_type"],
                "operation_type": prop["operation_type"],
                "neighborhood":   prop["neighborhood"],
                "id":             property_id,
            })
            market = dict(cur.fetchone())

    # Si no hay suficientes datos en el barrio, usar la ciudad
    if not market["sample_size"] or market["sample_size"] < 3:
        sql_city = """
            SELECT
                COUNT(*)                             AS sample_size,
                AVG(price_per_m2)                    AS avg_m2,
                PERCENTILE_CONT(0.5) WITHIN GROUP
                    (ORDER BY price_per_m2)          AS median_m2
            FROM properties
            WHERE city           = %(city)s
              AND property_type  = %(property_type)s
              AND operation_type = %(operation_type)s
              AND is_active      = TRUE
              AND price_per_m2   IS NOT NULL
              AND id             != %(id)s
        """
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql_city, {
                    "city":           prop["city"],
                    "property_type":  prop["property_type"],
                    "operation_type": prop["operation_type"],
                    "id":             property_id,
                })
                market = dict(cur.fetchone())
        scope = "ciudad"
    else:
        scope = "barrio"

    if not market["avg_m2"]:
        return {**prop, "score": None, "label": "Sin datos suficientes",
                "diff_pct": None, "market_avg_m2": None, "sample_size": 0}

    # 3. Calcular diferencia porcentual
    prop_m2    = float(prop["price_per_m2"])
    market_avg = float(market["avg_m2"])
    diff_pct   = ((prop_m2 - market_avg) / market_avg) * 100

    # 4. Asignar etiqueta y color
    if diff_pct <= -20:
        label = "Muy por debajo del mercado"
        color = "green"
        score = 5
    elif diff_pct <= -10:
        label = "Por debajo del mercado"
        color = "green"
        score = 4
    elif diff_pct <= 5:
        label = "Precio de mercado"
        color = "yellow"
        score = 3
    elif diff_pct <= 20:
        label = "Por encima del mercado"
        color = "orange"
        score = 2
    else:
        label = "Muy por encima del mercado"
        color = "red"
        score = 1

    return {
        "property_id":   property_id,
        "price_per_m2":  round(prop_m2, 0),
        "market_avg_m2": round(market_avg, 0),
        "diff_pct":      round(diff_pct, 1),
        "label":         label,
        "color":         color,
        "score":         score,
        "scope":         scope,
        "sample_size":   int(market["sample_size"]),
    }


@router.get("/{property_id}")
def get_price_score(property_id: int):
    """Devuelve el score de precio de un inmueble."""
    return calculate_price_score(property_id)


@router.get("/batch/{city}")
def batch_price_score(city: str, operation_type: str = "venta", limit: int = 20):
    """Devuelve scores de precio para los inmuebles más recientes de una ciudad."""
    sql = """
        SELECT id FROM properties
        WHERE city = %(city)s AND operation_type = %(operation_type)s
          AND is_active = TRUE AND price_per_m2 IS NOT NULL
        ORDER BY scraped_at DESC
        LIMIT %(limit)s
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, {"city": city.lower(),
                              "operation_type": operation_type, "limit": limit})
            ids = [r["id"] for r in cur.fetchall()]

    results = []
    for pid in ids:
        try:
            results.append(calculate_price_score(pid))
        except Exception:
            pass

    return results
