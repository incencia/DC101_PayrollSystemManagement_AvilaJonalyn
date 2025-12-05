from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker

from .config import settings

engine = create_engine(settings.database_url, echo=False, future=True)
SessionLocal = scoped_session(
    sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
)

Base = declarative_base()


def init_db() -> None:
    """Create database tables based on the SQLAlchemy models."""
    import backend.models  # noqa: F401  # pylint: disable=import-outside-toplevel

    Base.metadata.create_all(bind=engine)


def get_session():
    """Return the scoped session for direct usage."""
    return SessionLocal()


@contextmanager
def session_scope() -> Generator:
    """Provide a transactional scope around a series of operations."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

