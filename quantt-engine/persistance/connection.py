import sys
from pathlib import Path
from sqlite3 import Connection as sqlite3connection
from typing import Any

from sqlalchemy import create_engine, event, inspect
from sqlalchemy.orm import DeclarativeBase, sessionmaker

if getattr(sys, "frozen", False):
    DIR = Path(sys.executable).parent
else:
    DIR = Path(__file__).resolve().parent.parent

DB_PATH = DIR / "qdata" / "general.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

DB_URL = f"sqlite:///{DB_PATH.as_posix()}"

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
    """Create missing tables and migrate the legacy order foreign keys."""

    Base.metadata.create_all(bind=engine)

    def foreign_key_pairs(connection, table_name: str) -> set[tuple[str, str, str]]:
        return {
            (row["table"], row["from"], row["to"])
            for row in connection.exec_driver_sql(
                f"PRAGMA foreign_key_list({table_name})"
            ).mappings()
        }

    expected_linked_fk = {
        ("general_orders", "parent_order_id", "id"),
        ("general_orders", "exchange", "exchange"),
    }

    # SQLite cannot alter a foreign-key constraint in place. Rebuild both
    # related tables together if they still have the old single-column
    # references. The transaction preserves existing rows and rolls back as a
    # unit if a copy or integrity check fails.
    with engine.connect() as connection:
        if not inspect(connection).has_table("general_orders") or not inspect(
            connection
        ).has_table("take_stop_orders"):
            return

        general_fks = foreign_key_pairs(connection, "general_orders")
        linked_fks = foreign_key_pairs(connection, "take_stop_orders")
        if not general_fks and linked_fks == expected_linked_fk:
            return

    raw_connection = engine.raw_connection()
    cursor = raw_connection.cursor()
    try:
        # The pragma must be changed before beginning the migration transaction.
        cursor.execute("PRAGMA foreign_keys=OFF")
        cursor.execute("BEGIN IMMEDIATE")
        cursor.execute("DROP TABLE IF EXISTS general_orders__new")
        cursor.execute("DROP TABLE IF EXISTS take_stop_orders__new")
        cursor.execute(
            """
            CREATE TABLE general_orders__new (
                id VARCHAR(32) NOT NULL,
                exchange VARCHAR(16) NOT NULL,
                entrance_exit VARCHAR(10),
                price FLOAT NOT NULL,
                amount FLOAT NOT NULL,
                side VARCHAR(10),
                symbol VARCHAR(20),
                order_type VARCHAR(20),
                time VARCHAR(32),
                previous_time VARCHAR(32),
                take_id VARCHAR(32),
                stop_id VARCHAR(32),
                PRIMARY KEY (id, exchange)
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE take_stop_orders__new (
                id VARCHAR(32) NOT NULL,
                exchange VARCHAR(16) NOT NULL,
                parent_order_id VARCHAR(32) NOT NULL,
                price FLOAT NOT NULL,
                amount FLOAT NOT NULL,
                side VARCHAR(10),
                symbol VARCHAR(20),
                order_type VARCHAR(30),
                time VARCHAR(32) UNIQUE,
                fees FLOAT,
                PRIMARY KEY (id, exchange),
                FOREIGN KEY (parent_order_id, exchange)
                    REFERENCES general_orders (id, exchange)
            )
            """
        )
        cursor.execute(
            """INSERT INTO general_orders__new
               (id, exchange, entrance_exit, price, amount, side, symbol,
                order_type, time, previous_time, take_id, stop_id)
               SELECT id, exchange, entrance_exit, price, amount, side, symbol,
                      order_type, time, previous_time, take_id, stop_id
               FROM general_orders"""
        )
        cursor.execute(
            """INSERT INTO take_stop_orders__new
               (id, exchange, parent_order_id, price, amount, side, symbol,
                order_type, time, fees)
               SELECT id, exchange, parent_order_id, price, amount, side, symbol,
                      order_type, time, fees
               FROM take_stop_orders"""
        )
        cursor.execute("DROP TABLE take_stop_orders")
        cursor.execute("DROP TABLE general_orders")
        cursor.execute("ALTER TABLE general_orders__new RENAME TO general_orders")
        cursor.execute("ALTER TABLE take_stop_orders__new RENAME TO take_stop_orders")

        violations = cursor.execute("PRAGMA foreign_key_check").fetchall()
        if violations:
            raise RuntimeError(
                f"Order schema migration found foreign-key violations: {violations[:5]}"
            )
        raw_connection.commit()
    except Exception:
        raw_connection.rollback()
        raise
    finally:
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
        raw_connection.close()

    # Recreate indexes and any other metadata-managed objects after rebuilding.
    Base.metadata.create_all(bind=engine)
