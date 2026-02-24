CREATE TABLE raw.tb_alertario_pluviometric (
    dia VARCHAR NOT NULL,
    hora VARCHAR NOT NULL,
    hbv VARCHAR,
    station VARCHAR NOT NULL,
    "15min" VARCHAR,
    "1h" VARCHAR,
    "4h" VARCHAR,
    "24h" VARCHAR,
    "96h" VARCHAR,
    PRIMARY KEY (dia, hora, hbv, station)
);

CREATE TABLE silver.tb_alertario_pluviometric (
    station VARCHAR NOT NULL,
    timestamp_utc TIMESTAMPTZ NOT NULL,
    rain_15min DOUBLE PRECISION,
    rain_1h DOUBLE PRECISION,
    rain_4h DOUBLE PRECISION,
    rain_24h DOUBLE PRECISION,
    rain_96h DOUBLE PRECISION,
    PRIMARY KEY (station, timestamp_utc)
);