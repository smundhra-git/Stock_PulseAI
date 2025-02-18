from dotenv import load_dotenv
import os
from psycopg2 import sql
import psycopg2
import pandas as pd
import yfinance as yf
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from fastapi import HTTPException
from datetime import datetime, timedelta
from pymongo import MongoClient
from urllib.parse import quote_plus

load_dotenv()
# Load MongoDB Credentials from .env
MONGO_USERNAME = os.getenv("MONGODB_USERNAME", "").strip()  # Ensure it's a string
MONGO_PASSWORD = os.getenv("MONGODB_PASSWORD", "").strip()  # Ensure it's a string
MONGO_HOST = os.getenv("MONGODB_HOST", "localhost").strip()
MONGO_PORT = os.getenv("MONGODB_PORT", "27017").strip()
MONGO_DB = os.getenv("MONGODB_DB", "stock_pulse_ai").strip()
# Add these constants at the top with other imports
MONGODB_DB = "sec_filings"
MONGODB_COLLECTION = "filings"

# Ensure credentials are properly formatted
if not MONGO_USERNAME or not MONGO_PASSWORD:
    raise ValueError("❌ MONGO_USERNAME or MONGO_PASSWORD is missing from the .env file!")

# Encode Username & Password (Fix InvalidURI Issue)
ENCODED_USERNAME = quote_plus(str(MONGO_USERNAME))
ENCODED_PASSWORD = quote_plus(str(MONGO_PASSWORD))

MONGO_URI = f"mongodb://{ENCODED_USERNAME}:{ENCODED_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}"

def get_mongo_collection():
    """Returns the MongoDB collection for storing SEC filings."""
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    return db["sec_filings"]


# Database connection parameters
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}

# MongoDB Configuration
MONGO_URI = os.getenv("MONGO_URI")  # Connection string format


def get_db_connection():
    """Establishes and returns a PostgreSQL database connection."""
    return psycopg2.connect(**DB_CONFIG)

