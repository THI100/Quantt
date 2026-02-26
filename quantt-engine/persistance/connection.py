from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DB_URL = "sqlite:///./my_database.db"

# Create the Engine
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Base class for models to inherit from
class Base(DeclarativeBase):
    pass
