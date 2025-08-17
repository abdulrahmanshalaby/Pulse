import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base,sessionmaker
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")
engine = create_engine(
    DATABASE_URL,
    pool_size=20,        # number of permanent connections
    max_overflow=40,     # extra connections if needed
    pool_timeout=30,     # wait time before giving up
    pool_recycle=1800    # recycle connections every 30 min
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)




base = declarative_base()
def create_tables():
    try:
      base.metadata.create_all(engine)
      print("tables created")
    except Exception as e:
        print("tables not created:", e)