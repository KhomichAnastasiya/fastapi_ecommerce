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


# --------------- Async Session -------------------------

from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session_maker

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Provides an asynchronous SQLAlchemy session for working
    with the PostgreSQL database.
    """
    async with async_session_maker() as session:
        yield session
