import re
import unicodedata
from config import PROPERTY_TYPE_MAP, OPERATION_TYPE_MAP
from models import Property


CITY_ALIASES = {
    "bogota d.c.": "bogota",
    "bogotá d.c.": "bogota",
    "bogotá": "bogota",
    "medellín": "medellin",
    "cali": "cali",
    "barranquilla": "barranquilla",
    "bucaramanga": "bucaramanga",
    "cartagena de indias": "cartagena",
    "cartagena": "cartagena",
    "pereira": "pereira",
}


def normalize_text(text: str) -> str:
    """Limpia, estandariza y elimina tildes del texto."""
    if not text:
        return ""
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", text.strip().lower())


def normalize_city(raw: str) -> str:
    cleaned = normalize_text(raw)
    return CITY_ALIASES.get(cleaned, cleaned)


def normalize_property_type(raw: str) -> str:
    raw = normalize_text(raw)
    for key, value in PROPERTY_TYPE_MAP.items():
        if key in raw:
            return value
    return "otro"


def normalize_operation_type(raw: str) -> str:
    raw = normalize_text(raw)
    for key, value in OPERATION_TYPE_MAP.items():
        if key in raw:
            return value
    return "desconocido"


def normalize_price(raw) -> float | None:
    """Convierte strings como '$1.200.000' a float."""
    if raw is None:
        return None
    if isinstance(raw, (int, float)):
        return float(raw)
    cleaned = re.sub(r"[^\d]", "", str(raw))
    return float(cleaned) if cleaned else None


def normalize_area(raw) -> float | None:
    if raw is None:
        return None
    if isinstance(raw, (int, float)):
        return float(raw)
    match = re.search(r"[\d]+[.,]?[\d]*", str(raw))
    return float(match.group().replace(",", ".")) if match else None


def normalize(prop: Property) -> Property:
    """Aplica todas las normalizaciones a un Property."""
    prop.property_type = normalize_property_type(prop.property_type)
    prop.operation_type = normalize_operation_type(prop.operation_type)
    prop.price = normalize_price(prop.price)
    prop.area_m2 = normalize_area(prop.area_m2)
    prop.city = normalize_city(prop.city)
    prop.neighborhood = normalize_text(prop.neighborhood)
    prop.title = prop.title.strip()
    prop.description = prop.description.strip()
    prop.compute_price_per_m2()
    return prop
