# db/connection.py — imports from config, never reads os.environ directly
from restaurant_reviews.config import DATABASE_URL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from contextlib import contextmanager

engine = create_engine(DATABASE_URL, pool_size=5, max_overflow=10)

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

@contextmanager
def get_session():
    session = SessionLocal()
    try:
        yield session        # pause here, hand the session to the caller
        session.commit()     # resume here after the `with` block finishes
    except Exception:
        session.rollback()   # if anything went wrong, undo everything
        raise
    finally:
        session.close()      # always runs, success or failure


