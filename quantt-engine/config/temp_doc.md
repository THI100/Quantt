from persistance.connection import SessionLocal
from persistance.models import X

    with SessionLocal() as session:
        try:
            new_config = X(
            ...
            )
            session.add(new_config)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database error saving Entry: {e}")
