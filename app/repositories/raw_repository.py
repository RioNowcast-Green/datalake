class RawAlertarioRepository:
    
    def __init__(self, engine):
        self.engine = engine

    def create_table_if_not_exists(self):
        metadata = MetaData()

        if not inspect(self.engine).has_table("TB_ALERTARIO_PLUVIOMETRIC", schema="raw"):
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
            metadata.create_all(self.engine)
            print("Tabela criada.")
        else:
            table = Table(
                "TB_ALERTARIO_PLUVIOMETRIC",
                metadata,
                autoload_with=self.engine,
                schema="raw"
            )
        
        return table