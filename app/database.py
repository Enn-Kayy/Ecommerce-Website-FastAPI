import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql://postgres:naman@localhost:5432/Naman"

# sync engine (SQLAlchemy core)
engine = create_engine(DATABASE_URL, future=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# FastAPI dependency


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()