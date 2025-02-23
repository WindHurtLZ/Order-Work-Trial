from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Env Contorl
if os.getenv("TESTING"):
    DATABASE_URL = "sqlite:///./test.db"
else:
    DATABASE_URL = os.getenv("DB_URL", "postgresql://user:password@db:5432/trading")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()