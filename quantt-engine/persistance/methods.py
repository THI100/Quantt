from persistance.connection import Base, SessionLocal, engine
from persistance.models import GeneralOrders, Profiles, Results, TakeStopOrders

# Create the tables
Base.metadata.create_all(bind=engine)

# Start a session
db = SessionLocal()


def search():

    u = 0

    return u


def add():

    a = 0

    return a


def update():

    z = 0

    return z


def delete():

    x = 0

    return x
