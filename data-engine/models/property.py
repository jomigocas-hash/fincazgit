from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class Property:
    """Modelo normalizado de un inmueble."""

    # Identificación
    source_id: str           # ID original del portal
    source_portal: str       # finca_raiz | metrocuadrado | ciencuadras
    canonical_id: Optional[str] = None  # ID único tras deduplicación

    # Tipo
    property_type: str = ""  # apartamento | casa | lote | etc.
    operation_type: str = "" # venta | arriendo

    # Ubicación
    city: str = ""
    neighborhood: str = ""
    address: str = ""
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    # Características
    area_m2: Optional[float] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    parking: Optional[int] = None
    floor: Optional[int] = None
    stratum: Optional[int] = None  # estrato

    # Precio
    price: Optional[float] = None
    price_per_m2: Optional[float] = None
    currency: str = "COP"
    admin_fee: Optional[float] = None  # cuota de administración

    # Contenido
    title: str = ""
    description: str = ""
    image_urls: list = field(default_factory=list)
    url: str = ""

    # Metadata
    published_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    scraped_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True

    def compute_price_per_m2(self):
        if self.price and self.area_m2 and self.area_m2 > 0:
            self.price_per_m2 = round(self.price / self.area_m2, 2)
