import os
import time

import core.engine as e
from persistance.connection import Base, engine


def start():
    if os.path.exists("./general.db"):
        print("existent")
    else:
        Base.metadata.create_all(bind=engine)

    try:
        while True:
            e.avaliation_and_place()
            time.sleep(60)
    except KeyboardInterrupt:
        # This block runs when you press Ctrl + C
        print("\nLoop stopped by user.")


def stop():
    message = "Stoping bot"

    return message
