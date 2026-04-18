# db/connection.py — imports from config, never reads os.environ directly
from restaurant_reviews.config import DATABASE_URL
from sqlalchemy import create_engine, text

engine = create_engine(DATABASE_URL, pool_size=5, max_overflow=10)


