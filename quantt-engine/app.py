from persistance.connection import Base, SessionLocal, engine
from persistance.models import User

# Create the tables in the database (Only needs to run once)
Base.metadata.create_all(bind=engine)

# Start a session
db = SessionLocal()

try:
    # Create a new user
    new_user = User(username="codemasters", email="hello@example.com")
    db.add(new_user)
    db.commit()
    print("User saved!")
finally:
    db.close()
