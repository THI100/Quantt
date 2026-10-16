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
    """Create config tables and migrate legacy SQLite schema columns."""

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
        "last": [
            ("nominal_key", "VARCHAR(4)"),
            ("exchange", "VARCHAR(16)"),
            ("trading_name", "VARCHAR(32)"),
            ("risk_name", "VARCHAR(32)"),
        ],
    }
    primary_keys = {
        "trading_config": "name",
        "risk_config": "name",
        "store": "exchange",
        "last": "nominal_key",
    }
    defaults = {"store": "none", "last": "last"}

    with engine.begin() as connection:
        inspector = inspect(connection)
        table_columns = {
            table: {column["name"] for column in inspector.get_columns(table)}
            for table in config_columns
            if inspector.has_table(table)
        }

        for table_name, columns in config_columns.items():
            if table_name not in table_columns:
                continue
            existing = table_columns[table_name]
            key_name = primary_keys[table_name]
            primary_key = set(
                inspector.get_pk_constraint(table_name).get("constrained_columns") or []
            )
            if key_name in existing and key_name in primary_key:
                continue

            temp_table = f"{table_name}_profile_migration"
            insert_columns = [name for name, _ in columns]
            columns_sql = ", ".join(f'"{name}" {kind}' for name, kind in columns)
            quoted_columns = ", ".join(f'"{name}"' for name in insert_columns)
            placeholders = ", ".join(f":{name}" for name in insert_columns)

            connection.execute(text(f'DROP TABLE IF EXISTS "{temp_table}"'))
            connection.execute(
                text(
                    f'CREATE TABLE "{temp_table}" ({columns_sql}, PRIMARY KEY ("{key_name}"))'
                )
            )
            insert_sql = text(
                f'INSERT INTO "{temp_table}" ({quoted_columns}) VALUES ({placeholders})'
            )
            seen_keys = set()
            for old_row in connection.execute(
                text(f'SELECT * FROM "{table_name}"')
            ).mappings():
                row = {
                    name: old_row[name] if name in existing else None
                    for name in insert_columns
                }
                row[key_name] = row[key_name] or defaults.get(table_name, "base")
                if row[key_name] in seen_keys:
                    continue
                seen_keys.add(row[key_name])
                connection.execute(insert_sql, row)

            connection.execute(text(f'DROP TABLE "{table_name}"'))
            connection.execute(
                text(f'ALTER TABLE "{temp_table}" RENAME TO "{table_name}"')
            )
            table_columns[table_name] = set(insert_columns)

        trading_columns = table_columns.get("trading_config", set())
        last_columns = table_columns.get("last", set())
        if {"name", "exchange"}.issubset(trading_columns):
            connection.execute(
                text(
                    'UPDATE "trading_config" SET "exchange" = :exchange '
                    'WHERE "exchange" IS NULL OR upper("exchange") = :legacy_value'
                ),
                {"exchange": "binance", "legacy_value": "NULL"},
            )

        if {"nominal_key", "exchange", "trading_name"}.issubset(last_columns) and {
            "name",
            "exchange",
        }.issubset(trading_columns):
            connection.execute(
                text(
                    'UPDATE "last" SET "exchange" = COALESCE('
                    '(SELECT "exchange" FROM "trading_config" '
                    'WHERE "name" = "last"."trading_name"), :exchange) '
                    'WHERE "exchange" IS NULL OR upper("exchange") = :legacy_value'
                ),
                {"exchange": "binance", "legacy_value": "NULL"},
            )

        if inspector.has_table("general_orders"):
            order_columns = {
                column["name"] for column in inspector.get_columns("general_orders")
            }
            if "exchange" not in order_columns:
                connection.execute(
                    text(
                        'ALTER TABLE "general_orders" ADD COLUMN "exchange" VARCHAR(16)'
                    )
                )

            active_exchange = None
            if {"nominal_key", "exchange"}.issubset(last_columns):
                active_exchange = connection.execute(
                    text('SELECT "exchange" FROM "last" WHERE "nominal_key" = :key'),
                    {"key": "last"},
                ).scalar_one_or_none()
            if not active_exchange and {"name", "exchange"}.issubset(trading_columns):
                active_exchange = connection.execute(
                    text(
                        'SELECT "exchange" FROM "trading_config" WHERE "name" = :name'
                    ),
                    {"name": "base"},
                ).scalar_one_or_none()
            if active_exchange:
                connection.execute(
                    text(
                        'UPDATE "general_orders" SET "exchange" = :exchange '
                        'WHERE "exchange" IS NULL OR "exchange" = \'\''
                    ),
                    {"exchange": active_exchange},
                )

    Base.metadata.create_all(bind=engine)
