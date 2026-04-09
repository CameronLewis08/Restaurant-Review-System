# config.py
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL: str = os.environ["DATABASE_URL"]   # KeyError = fail fast on missing config
DB_POOL_SIZE: int = int(os.environ.get("DB_POOL_SIZE", "5"))
DEBUG: bool = os.environ.get("DEBUG", "false").lower() == "true"