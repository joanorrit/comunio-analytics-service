from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URL = "postgresql://username:password@db:5432/biwenger"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()


def db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
