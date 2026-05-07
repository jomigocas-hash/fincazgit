-- Tabla de búsquedas de demanda
CREATE TABLE IF NOT EXISTS demand_searches (
    id              SERIAL PRIMARY KEY,
    -- Quién busca
    role            VARCHAR(20) DEFAULT 'buyer',  -- buyer | agent
    agent_id        INTEGER,                       -- NULL si es comprador directo
    client_name     VARCHAR(100),
    client_email    VARCHAR(100),

    -- Criterios obligatorios
    city            VARCHAR(100) NOT NULL,
    operation_type  VARCHAR(20)  NOT NULL,
    property_type   VARCHAR(50)  NOT NULL,
    max_price       NUMERIC(15,2) NOT NULL,
    min_bedrooms    SMALLINT     NOT NULL,
    min_area_m2     NUMERIC(10,2) NOT NULL,

    -- Criterios opcionales
    stratum         SMALLINT,
    locality        VARCHAR(100),
    neighborhood    VARCHAR(100),
    parking         SMALLINT,
    covered_garage  BOOLEAN DEFAULT FALSE,

    -- Metadata
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    is_active       BOOLEAN DEFAULT TRUE
);

CREATE INDEX IF NOT EXISTS idx_demand_city     ON demand_searches(city);
CREATE INDEX IF NOT EXISTS idx_demand_agent    ON demand_searches(agent_id);
CREATE INDEX IF NOT EXISTS idx_demand_active   ON demand_searches(is_active);
