import os
import time

import core.engine as e
from config import risk, settings
from data.client import cached_client
from persistance.connection import Base, engine

client = cached_client()


def start():
    if os.path.exists("./general.db"):
        print("existent")
    else:
        Base.metadata.create_all(bind=engine)

    for symbol in settings.list_of_interest:
        client.set_leverage(risk.leverage, symbol)

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
