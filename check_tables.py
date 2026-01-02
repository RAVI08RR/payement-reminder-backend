
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect

load_dotenv()

db_url = os.getenv("DATABASE_URL")
print(f"Checking tables at: {db_url.split('@')[-1] if db_url else 'None'}")

try:
    engine = create_engine(db_url)
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"Tables found: {tables}")
    if "password_reset_tokens" in tables:
        print("Success: 'password_reset_tokens' table is correctly detected!")
    else:
        print("Error: 'password_reset_tokens' table NOT found.")
except Exception as e:
    print(f"Error: {e}")
