import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from db import get_conn

router = APIRouter()


@router.get("/")
def list_properties(
    city:           Optional[str]   = Query(None, description="Ciudad"),
    operation_type: Optional[str]   = Query(None, description="venta | arriendo"),
    property_type:  Optional[str]   = Query(None, description="apartamento | casa | lote ..."),
    min_price:      Optional[float] = Query(None),
    max_price:      Optional[float] = Query(None),
    min_area:       Optional[float] = Query(None),
    max_area:       Optional[float] = Query(None),
    bedrooms:       Optional[int]   = Query(None),
    stratum:        Optional[int]   = Query(None),
    neighborhood:   Optional[str]   = Query(None),
    page:           int             = Query(1, ge=1),
    page_size:      int             = Query(20, ge=1, le=100),
):
    filters = []
    params = {}

    if city:
        filters.append("city = %(city)s")
        params["city"] = city.lower()
    if operation_type:
        filters.append("operation_type = %(operation_type)s")
        params["operation_type"] = operation_type.lower()
    if property_type:
        filters.append("property_type = %(property_type)s")
        params["property_type"] = property_type.lower()
    if min_price is not None:
        filters.append("price >= %(min_price)s")
        params["min_price"] = min_price
    if max_price is not None:
        filters.append("price <= %(max_price)s")
        params["max_price"] = max_price
    if min_area is not None:
        filters.append("area_m2 >= %(min_area)s")
        params["min_area"] = min_area
    if max_area is not None:
        filters.append("area_m2 <= %(max_area)s")
        params["max_area"] = max_area
    if bedrooms is not None:
        filters.append("bedrooms = %(bedrooms)s")
        params["bedrooms"] = bedrooms
    if stratum is not None:
        filters.append("stratum = %(stratum)s")
        params["stratum"] = stratum
    if neighborhood:
        filters.append("neighborhood ILIKE %(neighborhood)s")
        params["neighborhood"] = f"%{neighborhood}%"

    where = ("WHERE " + " AND ".join(filters)) if filters else ""
    offset = (page - 1) * page_size
    params["limit"] = page_size
    params["offset"] = offset

    sql = f"""
        SELECT id, canonical_id, source_portal, property_type, operation_type,
               city, neighborhood, address,
               ST_Y(location::geometry) AS latitude,
               ST_X(location::geometry) AS longitude,
               area_m2, bedrooms, bathrooms, parking, floor, stratum,
               price, price_per_m2, currency, admin_fee,
               title, url, image_urls, published_at, scraped_at
        FROM properties
        {where}
        AND is_active = TRUE
        ORDER BY scraped_at DESC
        LIMIT %(limit)s OFFSET %(offset)s
    """

    count_sql = f"SELECT COUNT(*) FROM properties {where} AND is_active = TRUE"

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(count_sql, params)
            total = cur.fetchone()["count"]
            cur.execute(sql, params)
            rows = cur.fetchall()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "results": [dict(r) for r in rows],
    }


@router.get("/{property_id}")
def get_property(property_id: int):
    sql = """
        SELECT *, ST_Y(location::geometry) AS latitude, ST_X(location::geometry) AS longitude
        FROM properties WHERE id = %(id)s
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, {"id": property_id})
            row = cur.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Inmueble no encontrado")
    return dict(row)
