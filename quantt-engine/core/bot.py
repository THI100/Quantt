import os

from persistance.connection import Base, engine


def start():
    if os.path.exists("./general.db"):
        print("existent")
    else:
        Base.metadata.create_all(bind=engine)


def stop():
    message = "Stoping bot"

    return message
