-- Requiere extensión PostGIS para georreferenciación
CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS properties (
    id              SERIAL PRIMARY KEY,
    canonical_id    VARCHAR(32),
    source_id       VARCHAR(100) NOT NULL,
    source_portal   VARCHAR(50)  NOT NULL,

    -- Tipo
    property_type   VARCHAR(50),
    operation_type  VARCHAR(20),

    -- Ubicación
    city            VARCHAR(100),
    neighborhood    VARCHAR(100),
    address         TEXT,
    location        GEOGRAPHY(POINT, 4326),  -- PostGIS

    -- Características
    area_m2         NUMERIC(10, 2),
    bedrooms        SMALLINT,
    bathrooms       SMALLINT,
    parking         SMALLINT,
    floor           SMALLINT,
    stratum         SMALLINT,

    -- Precio
    price           NUMERIC(15, 2),
    price_per_m2    NUMERIC(12, 2),
    currency        VARCHAR(5) DEFAULT 'COP',
    admin_fee       NUMERIC(12, 2),

    -- Contenido
    title           TEXT,
    description     TEXT,
    image_urls      TEXT[],
    url             TEXT,

    -- Metadata
    published_at    TIMESTAMPTZ,
    updated_at      TIMESTAMPTZ,
    scraped_at      TIMESTAMPTZ DEFAULT NOW(),
    is_active       BOOLEAN DEFAULT TRUE,

    UNIQUE(source_portal, source_id)
);

-- Índices para búsquedas frecuentes
CREATE INDEX IF NOT EXISTS idx_properties_city        ON properties(city);
CREATE INDEX IF NOT EXISTS idx_properties_type        ON properties(property_type, operation_type);
CREATE INDEX IF NOT EXISTS idx_properties_price       ON properties(price);
CREATE INDEX IF NOT EXISTS idx_properties_canonical   ON properties(canonical_id);
CREATE INDEX IF NOT EXISTS idx_properties_location    ON properties USING GIST(location);
CREATE INDEX IF NOT EXISTS idx_properties_scraped_at  ON properties(scraped_at DESC);
