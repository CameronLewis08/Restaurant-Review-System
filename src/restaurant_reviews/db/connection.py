# db/connection.py — imports from config, never reads os.environ directly
from config import DATABASE_URL
from sqlalchemy import create_engine

engine = create_engine(DATABASE_URL)