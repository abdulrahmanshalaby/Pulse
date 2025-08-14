import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base,sessionmaker
# from dotenv import load_dotenv()
# load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)




base = declarative_base()
def create_tables():
    try:
      base.metadata.create_all(engine)
      print("tables created")
    except:
        print("tables not created") 