import sqlite3
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv

# Load env for Supabase credentials
load_dotenv(override=True)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Check if Supabase is configured
USE_SUPABASE = bool(SUPABASE_URL and SUPABASE_KEY and "your-project" not in SUPABASE_URL)

DB_NAME = "transactions.db"

def get_supabase_client():
    if not USE_SUPABASE:
        return None
    try:
        from supabase import create_client
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"Supabase connection error: {e}")
        return None

def init_db():
    """Initializes local SQLite for fallback."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            vendor TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            recommended_card TEXT NOT NULL,
            miles_earned INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def log_transaction(vendor, category, amount, recommended_card, miles_earned):
    if not amount:
        amount = 0.0
    
