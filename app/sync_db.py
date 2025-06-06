# sync_db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core import config as app_config
from contextlib import contextmanager


SYNC_DATABASE_URI = app_config.settings.DATABASE_SYNC_URI

print(f"Sync Database URI: {SYNC_DATABASE_URI}")

sync_engine = create_engine(SYNC_DATABASE_URI, pool_pre_ping=True)

SyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)


@contextmanager
def get_sync_db():
    """
    Dependency to get a synchronous database session.
    Yields a session that can be used in a synchronous context.
    """
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()
