# myprog/db.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DB_URL")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

if not all([DB_URL, DB_USER, DB_PASSWORD]):
    raise ValueError("DB_URL, DB_USER, and DB_PASSWORD must be set in the environment")

SQLALCHEMY_DATABASE_URL = f"mariadb+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_URL}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
