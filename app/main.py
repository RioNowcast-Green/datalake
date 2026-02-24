import os
import pandas as pd
from app.classes.alertario import AlertaRio
from sqlalchemy import create_engine, inspect, MetaData, Table, Column, String, PrimaryKeyConstraint, text
from sqlalchemy.dialects.postgresql import insert

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR, EVENT_SCHEDULER_STARTED

from pytz import timezone

from datetime import datetime


def alertario(year):
    alertario = AlertaRio()

    print("=== INICIANDO SCRAP ===")
    alertario.scrap_pluv(year)

    print("=== CONECTANDO AO BANCO ===")
    engine = create_engine(
        f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:"
        f"{os.getenv('POSTGRES_PASSWORD')}@postgres:5432/"
        f"{os.getenv('POSTGRES_DB')}",
        pool_pre_ping=True
    )

    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS raw"))

    stations = alertario.get_stations()
    print(f"Estações disponíveis: {stations}")

    metadata = MetaData()

    if not inspect(engine).has_table("TB_ALERTARIO_PLUVIOMETRIC", schema="raw"):
        table = Table(
            "TB_ALERTARIO_PLUVIOMETRIC",
            metadata,
            Column("dia", String, nullable=False),
            Column("hora", String, nullable=False),
            Column("hbv", String),
            Column("station", String, nullable=False),
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

def job_listener(event):
    global run_counter
    run_counter += 1

    job = scheduler.get_job("alertario_job")
    next_run = job.next_run_time

    print("\n==============================")
    print(f"🔁 Run #{run_counter}")
    print("🕒 Executado em:", datetime.now(tz))
    print("⏭ Próxima execução:", next_run)
    print("==============================\n")



if __name__ == "__main__":

    tz = timezone("America/Sao_Paulo")
    td_year = datetime.now(tz).year

    scheduler = BlockingScheduler(timezone=tz)

    alertario(str(td_year))

    scheduler.add_job(
        alertario,
        trigger="interval",
        minutes=30,
        args=[str(td_year)],
        id="alertario_job",
        max_instances=1,
        coalesce=True
    )

    scheduler.add_listener(
        job_listener,
        EVENT_JOB_EXECUTED | EVENT_JOB_ERROR
    )

    print("🚀 Scheduler iniciado...")
    scheduler.start()