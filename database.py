from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

import urllib.parse

DATABASE_URL = os.getenv("DATABASE_URL")

# Diagnostic logging to help identify connection issues on Render
# We do not log the password for security reasons.
if DATABASE_URL:
    try:
        parsed = urllib.parse.urlparse(DATABASE_URL)
        print(f"--- DB DIAGNOSTIC ---")
        print(f"Host: {parsed.hostname}")
        print(f"Port: {parsed.port or 5432}")
        print(f"Scheme: {parsed.scheme}")
        print(f"Query: {parsed.query}")
        print(f"---------------------")
    except Exception as e:
        print(f"ERROR: Could not parse DATABASE_URL: {e}")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
