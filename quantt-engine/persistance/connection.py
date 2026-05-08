from pathlib import Path
from sqlite3 import Connection as sqlite3connection
from typing import Any

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DIR = Path(__file__).parent
DB_PATH = DIR.parent / "qdata" / "general.db"

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
