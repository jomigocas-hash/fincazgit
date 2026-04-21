import psycopg2
import psycopg2.extras
from psycopg2.extras import execute_values
from config import DATABASE_URL
from models import Property


def get_connection():
    return psycopg2.connect(DATABASE_URL)


def upsert_property(prop: Property) -> None:
    """Inserta o actualiza un inmueble en la base de datos."""
    sql = """
        INSERT INTO properties (
            canonical_id, source_id, source_portal,
            property_type, operation_type,
            city, neighborhood, address, location,
            area_m2, bedrooms, bathrooms, parking, floor, stratum,
            price, price_per_m2, currency, admin_fee,
            title, description, image_urls, url,
            published_at, updated_at, scraped_at, is_active
        ) VALUES (
            %(canonical_id)s, %(source_id)s, %(source_portal)s,
            %(property_type)s, %(operation_type)s,
            %(city)s, %(neighborhood)s, %(address)s,
            ST_SetSRID(ST_MakePoint(%(longitude)s, %(latitude)s), 4326),
            %(area_m2)s, %(bedrooms)s, %(bathrooms)s, %(parking)s, %(floor)s, %(stratum)s,
            %(price)s, %(price_per_m2)s, %(currency)s, %(admin_fee)s,
            %(title)s, %(description)s, %(image_urls)s, %(url)s,
            %(published_at)s, %(updated_at)s, %(scraped_at)s, %(is_active)s
        )
        ON CONFLICT (source_portal, source_id) DO UPDATE SET
            canonical_id  = EXCLUDED.canonical_id,
            price         = EXCLUDED.price,
            price_per_m2  = EXCLUDED.price_per_m2,
            admin_fee     = EXCLUDED.admin_fee,
            title         = EXCLUDED.title,
            description   = EXCLUDED.description,
            image_urls    = EXCLUDED.image_urls,
            updated_at    = EXCLUDED.updated_at,
            scraped_at    = EXCLUDED.scraped_at,
            is_active     = EXCLUDED.is_active;
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, {
                **prop.__dict__,
                "image_urls": prop.image_urls,
                "latitude": prop.latitude,
                "longitude": prop.longitude,
            })


def bulk_upsert(properties: list[Property]) -> int:
    """Inserta múltiples propiedades. Retorna cantidad insertada/actualizada."""
    sql = """
        INSERT INTO properties (
            canonical_id, source_id, source_portal,
            property_type, operation_type,
            city, neighborhood, address, location,
            area_m2, bedrooms, bathrooms, parking, floor, stratum,
            price, price_per_m2, currency, admin_fee,
            title, description, image_urls, url,
            published_at, updated_at, scraped_at, is_active
        ) VALUES (
            %(canonical_id)s, %(source_id)s, %(source_portal)s,
            %(property_type)s, %(operation_type)s,
            %(city)s, %(neighborhood)s, %(address)s,
            CASE WHEN %(longitude)s IS NOT NULL AND %(latitude)s IS NOT NULL
                 THEN ST_SetSRID(ST_MakePoint(%(longitude)s, %(latitude)s), 4326)
                 ELSE NULL END,
            %(area_m2)s, %(bedrooms)s, %(bathrooms)s, %(parking)s, %(floor)s, %(stratum)s,
            %(price)s, %(price_per_m2)s, %(currency)s, %(admin_fee)s,
            %(title)s, %(description)s, %(image_urls)s, %(url)s,
            %(published_at)s, %(updated_at)s, %(scraped_at)s, %(is_active)s
        )
        ON CONFLICT (source_portal, source_id) DO UPDATE SET
            canonical_id  = EXCLUDED.canonical_id,
            price         = EXCLUDED.price,
            price_per_m2  = EXCLUDED.price_per_m2,
            admin_fee     = EXCLUDED.admin_fee,
            title         = EXCLUDED.title,
            description   = EXCLUDED.description,
            image_urls    = EXCLUDED.image_urls,
            updated_at    = EXCLUDED.updated_at,
            scraped_at    = EXCLUDED.scraped_at,
            is_active     = EXCLUDED.is_active;
    """
    count = 0
    with get_connection() as conn:
        with conn.cursor() as cur:
            for prop in properties:
                try:
                    cur.execute(sql, {
                        **prop.__dict__,
                        "image_urls": psycopg2.extras.Json(prop.image_urls),
                        "latitude": prop.latitude,
                        "longitude": prop.longitude,
                    })
                    count += 1
                except Exception as e:
                    conn.rollback()
                    print(f"Error guardando {prop.source_id}: {e}")
        conn.commit()
    return count
