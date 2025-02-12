import os
import urllib.parse
from sqlalchemy import create_engine
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()

# ✅ URL Encode Password
password = urllib.parse.quote_plus(os.getenv("DB_PASSWORD"))

# ✅ Correct DB Connection String
DB_URL = f"postgresql://{os.getenv('DB_USER')}:{password}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

# ✅ Create SQLAlchemy engine
try:
    engine = create_engine(DB_URL, echo=True)
    conn = engine.connect()
    print("✅ Successfully connected to PostgreSQL!")
    conn.close()
except Exception as e:
    print(f"❌ Connection Error: {e}")
