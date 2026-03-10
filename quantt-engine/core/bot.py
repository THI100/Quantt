import os

import core.engine as e
from persistance.connection import Base, engine


def start():
    if os.path.exists("./general.db"):
        print("existent")
    else:
        Base.metadata.create_all(bind=engine)

    e.avaliation_and_place()


def stop():
    message = "Stoping bot"

    return message
