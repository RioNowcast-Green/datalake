import os
import pandas as pd
from app.classes.alertario import AlertaRio
from sqlalchemy import create_engine, inspect, MetaData, Table, Column, String, PrimaryKeyConstraint
from sqlalchemy.dialects.postgresql import insert

if __name__ == "__main__":
    alertario = AlertaRio()

    year = "2015"

    print("=== INICIANDO SCRAP ===")
    alertario.scrap_pluv(year)

    print("=== CONECTANDO AO BANCO ===")
    engine = create_engine(
        f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:"
        f"{os.getenv('POSTGRES_PASSWORD')}@postgres:5432/"
        f"{os.getenv('POSTGRES_DB')}",
        pool_pre_ping=True
    )

    stations = alertario.get_stations()
    print(f"Estações disponíveis: {stations}")

    metadata = MetaData()

    if not inspect(engine).has_table("TB_ALERTARIO_PLUVIOMETRIC", schema="raw"):
        table = Table(
            "TB_ALERTARIO_PLUVIOMETRIC",
            metadata,
            Column("dia", String, nullable=False),
            Column("hora", String, nullable=False),
            Column("station", String, nullable=False),
            Column("hbv", String),
            Column("15min", String),
            Column("1h", String),
            Column("4h", String),
            Column("24h", String),
            Column("96h", String),
            PrimaryKeyConstraint("dia", "hora", "hbv", "station"),
            schema="raw"
        )
        metadata.create_all(engine)
        print("Tabela criada.")
    else:
        table = Table(
            "TB_ALERTARIO_PLUVIOMETRIC",
            metadata,
            autoload_with=engine,
            schema="raw"
        )

    for station in stations:
        print(f"=== {station.upper()} -- {year} || INSERINDO DADOS NO BANCO ===")
        df = alertario.load_pluviometric_data(year_filter=year, station=station)
        df = df.where(pd.notnull(df), None)

        with engine.begin() as conn:
            inserted = 0
            skipped = 0
            for _, row in df.iterrows():
                data = row.to_dict()
                stmt = insert(table).values(**data)
                stmt = stmt.on_conflict_do_nothing(
                    index_elements=["dia", "hora", "hbv", "station"]
                )
                result = conn.execute(stmt)
                if result.rowcount > 0:
                    inserted += 1
                else:
                    skipped += 1

            print(f"  ✓ {inserted} linhas inseridas | {skipped} linhas duplicadas ignoradas")

    print("=== PROCESSO CONCLUÍDO ===")