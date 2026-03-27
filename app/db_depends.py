from sqlalchemy.orm import Session
from collections.abc import Generator

from app.database import SessionLocal

def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting a database session.
    Creates a new session for each request and closes it after processing.
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
