import sys
from pathlib import Path
from sqlite3 import Connection as sqlite3connection
from typing import Any

from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

if getattr(sys, "frozen", False):
    DIR = Path(sys.executable).parent
else:
    DIR = Path(__file__).resolve().parent.parent

DB_PATH = DIR / "qdata" / "general.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

DB_URL = f"sqlite:///./{DB_PATH.absolute()}"

engine = create_engine(DB_URL, connect_args={"check_same_thread": False})


@event.listens_for(engine, "connect")
def set_sqlite_pragma(
    dbapi_connection=sqlite3connection, connection_record=Any
) -> None:
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def ensure_config_schema() -> None:
    """Create config tables and add profile columns to legacy SQLite tables."""

    config_columns = {
        "trading_config": [
            ("name", "VARCHAR(32)"),
            ("is_demo_enabled", "BOOLEAN"),
            ("timeframe", "VARCHAR(8)"),
            ("exchange", "VARCHAR(16)"),
            ("execution_order", "VARCHAR(8)"),
            ("future_spot", "VARCHAR(8)"),
            ("list_of_interest", "JSON"),
            ("list_of_parameters", "JSON"),
        ],
        "risk_config": [
            ("name", "VARCHAR(32)"),
            ("risk_reward_ratio", "FLOAT"),
            ("acceptable_confidence", "INTEGER"),
            ("atr_multiplier", "FLOAT"),
            ("maximum_loss", "FLOAT"),
            ("percentage_of_capital_per_trade", "FLOAT"),
            ("leverage", "INTEGER"),
            ("maximum_iceberg_share", "FLOAT"),
            ("cross_isolated", "VARCHAR(10)"),
        ],
        "store": [
            ("exchange", "VARCHAR(16)"),
            ("data", "DATETIME"),
            ("balance_dt", "FLOAT"),
            ("balance_dc", "FLOAT"),
        ],
    }
    with engine.begin() as connection:
        inspector = inspect(connection)
        for table_name, columns in config_columns.items():
            if not inspector.has_table(table_name):
                continue
            existing = {column["name"] for column in inspector.get_columns(table_name)}
            primary_keys = set(
                inspector.get_pk_constraint(table_name).get("constrained_columns") or []
            )
            key_name = "exchange" if table_name == "store" else "name"
            if key_name in existing and key_name in primary_keys:
                continue

            temp_table = f"{table_name}_profile_migration"
            columns_sql = ", ".join(f'"{column}" {kind}' for column, kind in columns)
            connection.execute(text(f'DROP TABLE IF EXISTS "{temp_table}"'))
            connection.execute(
                text(
                    f'CREATE TABLE "{temp_table}" '
                    f'({columns_sql}, PRIMARY KEY ("{key_name}"))'
                )
            )

            old_rows = connection.execute(
                text(f'SELECT * FROM "{table_name}"')
            ).mappings()
            insert_columns = [column for column, _ in columns]
            placeholders = ", ".join(f":{column}" for column in insert_columns)
            quoted_columns = ", ".join('"' + column + '"' for column in insert_columns)
            insert_sql = text(
                f'INSERT INTO "{temp_table}" ({quoted_columns}) VALUES ({placeholders})'
            )
            for old_row in old_rows:
                row = {}
                for column in insert_columns:
                    source_column = column if column in existing else None
                    row[column] = (
                        old_row[source_column] if source_column in existing else None
                    )
                row[key_name] = row[key_name] or (
                    "none" if table_name == "store" else "base"
                )
                connection.execute(insert_sql, row)

            connection.execute(text(f'DROP TABLE "{table_name}"'))
            connection.execute(
                text(f'ALTER TABLE "{temp_table}" RENAME TO "{table_name}"')
            )

    Base.metadata.create_all(bind=engine)
