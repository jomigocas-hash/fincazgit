"""
Algoritmo de identidad para detectar inmuebles duplicados.
Compara metadatos clave y genera un canonical_id por hash.
"""
import hashlib
from typing import Optional
from models import Property


# Tolerancias para considerar dos inmuebles "iguales"
AREA_TOLERANCE_PCT = 0.05      # 5% diferencia en m²
PRICE_TOLERANCE_PCT = 0.10     # 10% diferencia en precio
GEO_TOLERANCE_KM = 0.1         # 100 metros


def _geo_distance_km(lat1, lon1, lat2, lon2) -> float:
    """Distancia aproximada entre dos coordenadas (Haversine simplificado)."""
    from math import radians, sin, cos, sqrt, atan2
    R = 6371
    lat1, lon1, lat2, lon2 = float(lat1), float(lon1), float(lat2), float(lon2)
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))


def _within_tolerance(a, b, pct) -> bool:
    if a is None or b is None:
        return True  # sin datos no podemos descartar
    if b == 0:
        return a == 0
    return abs(a - b) / b <= pct


def are_duplicates(p1: Property, p2: Property) -> bool:
    """Determina si dos propiedades son el mismo inmueble."""

    # Mismo portal y mismo ID → definitivamente el mismo
    if p1.source_portal == p2.source_portal and p1.source_id == p2.source_id:
        return True

    # Tipo de operación y propiedad deben coincidir
    if p1.operation_type != p2.operation_type:
        return False
    if p1.property_type != p2.property_type:
        return False

    # Ciudad debe coincidir
    if p1.city and p2.city and p1.city != p2.city:
        return False

    # Área similar
    if not _within_tolerance(p1.area_m2, p2.area_m2, AREA_TOLERANCE_PCT):
        return False

    # Precio similar
    if not _within_tolerance(p1.price, p2.price, PRICE_TOLERANCE_PCT):
        return False

    # Habitaciones y baños deben coincidir si están disponibles
    if p1.bedrooms and p2.bedrooms and p1.bedrooms != p2.bedrooms:
        return False
    if p1.bathrooms and p2.bathrooms and p1.bathrooms != p2.bathrooms:
        return False

    # Geolocalización: si ambos tienen coordenadas, verificar proximidad
    if all([p1.latitude, p1.longitude, p2.latitude, p2.longitude]):
        dist = _geo_distance_km(p1.latitude, p1.longitude, p2.latitude, p2.longitude)
        if dist > GEO_TOLERANCE_KM:
            return False

    return True


def generate_canonical_id(prop: Property) -> str:
    """
    Genera un ID canónico basado en características físicas del inmueble.
    Propiedades duplicadas deberían producir el mismo canonical_id.
    """
    parts = [
        prop.operation_type or "",
        prop.property_type or "",
        prop.city or "",
        prop.neighborhood or "",
        str(round(prop.area_m2 or 0, -1)),   # redondea a decena más cercana
        str(prop.bedrooms or 0),
        str(prop.bathrooms or 0),
        # Coordenadas redondeadas a ~100m de precisión
        str(round(float(prop.latitude or 0), 3)),
        str(round(float(prop.longitude or 0), 3)),
    ]
    fingerprint = "|".join(parts)
    return hashlib.md5(fingerprint.encode()).hexdigest()


def deduplicate(properties: list[Property]) -> list[Property]:
    """
    Recibe una lista de propiedades y retorna solo las únicas,
    asignando canonical_id a cada una.
    """
    unique: list[Property] = []

    for prop in properties:
        prop.canonical_id = generate_canonical_id(prop)
        # Buscar si ya existe un duplicado en la lista única
        duplicate_found = any(are_duplicates(prop, u) for u in unique)
        if not duplicate_found:
            unique.append(prop)

    return unique
