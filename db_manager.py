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
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mcc_registry (
            vendor TEXT PRIMARY KEY,
            mcc TEXT,
            platform_type TEXT,
            mapped_category TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_transaction(vendor, category, amount, recommended_card, miles_earned):
    if not amount:
        amount = 0.0
    
    timestamp = datetime.now().isoformat()
    
    # 1. Try Supabase
    client = get_supabase_client()
    if client:
        try:
            data = {
                "timestamp": timestamp,
                "vendor": vendor,
                "category": category,
                "amount": float(amount),
                "recommended_card": recommended_card,
                "miles_earned": int(miles_earned)
            }
            client.table("transactions").insert(data).execute()
            return
        except Exception as e:
            print(f"Supabase log failed, falling back to SQLite: {e}")

    # 2. Fallback to SQLite
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO transactions (timestamp, vendor, category, amount, recommended_card, miles_earned)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (timestamp, vendor, category, amount, recommended_card, miles_earned))
    conn.commit()
    conn.close()

def fetch_all_transactions():
    # 1. Try Supabase
    client = get_supabase_client()
    if client:
        try:
            response = client.table("transactions").select("*").order("timestamp", desc=True).execute()
            df = pd.DataFrame(response.data)
            if not df.empty:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df
        except Exception as e:
            print(f"Supabase fetch failed, falling back to SQLite: {e}")

    # 2. Fallback to SQLite
    conn = sqlite3.connect(DB_NAME)
    try:
        df = pd.read_sql_query("SELECT * FROM transactions ORDER BY timestamp DESC", conn)
    except:
        df = pd.DataFrame()
    conn.close()
    if not df.empty:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

def delete_transaction(tx_id):
    # 1. Try Supabase
    client = get_supabase_client()
    if client:
        try:
            # tx_id might be string from DataFrame or int
            client.table("transactions").delete().eq("id", tx_id).execute()
            return
        except Exception as e:
            print(f"Supabase delete failed: {e}")

    # 2. Fallback to SQLite
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions WHERE id = ?", (tx_id,))
    conn.commit()
    conn.close()

def delete_all_transactions():
    # 1. Try Supabase
    client = get_supabase_client()
    if client:
        try:
            # Delete all rows (requires where clause in Supabase usually, or use RPC)
            # In Supabase UI, you'd usually enable 'allow destructive' or use a catch-all filter
            client.table("transactions").delete().neq("vendor", "FORCE_DELETE_ALL_MAGIC_STRING_123").execute()
            return
        except Exception as e:
            print(f"Supabase nuke failed: {e}")

    # 2. Fallback to SQLite
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions")
    conn.commit()
    conn.close()

# ══════════════════════════════════════════════════════════════
# MCC REGISTRY (SELF-BUILDING DB)
# ══════════════════════════════════════════════════════════════

def get_all_mcc_mappings():
    """Returns a dictionary of all vendor mappings (used for fuzzy matching)."""
    # 1. Try Supabase
    client = get_supabase_client()
    if client:
        try:
            response = client.table("mcc_registry").select("*").execute()
            # return dict: {vendor_lower: matched_category}
            return {row["vendor"]: row["mapped_category"] for row in response.data}
        except Exception as e:
            print(f"Supabase mcc_registry fetch failed, falling back to SQLite: {e}")
            
    # 2. Fallback to SQLite
    conn = sqlite3.connect(DB_NAME)
    try:
        df = pd.read_sql_query("SELECT vendor, mapped_category FROM mcc_registry", conn)
        mapping = dict(zip(df['vendor'], df['mapped_category']))
    except:
        mapping = {}
    conn.close()
    return mapping

def save_mcc_mapping(vendor_name: str, mcc: str, platform_type: str, category: str):
    """Saves a newly researched vendor -> MCC -> Category mapping to Supabase/SQLite."""
    vendor_lower = vendor_name.strip().lower()
    
    # 1. Try Supabase
    client = get_supabase_client()
    if client:
        try:
            data = {
                "vendor": vendor_lower,
                "mcc": mcc,
                "platform_type": platform_type,
                "mapped_category": category
            }
            # upsert handles primary key conflicts gracefully
            client.table("mcc_registry").upsert(data, on_conflict="vendor").execute()
            print(f"[Supabase] Saved MCC mapping for {vendor_lower} -> {category}")
            return
        except Exception as e:
            print(f"Supabase mcc_registry save failed, falling back to SQLite: {e}")

    # 2. Fallback to SQLite
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO mcc_registry (vendor, mcc, platform_type, mapped_category)
        VALUES (?, ?, ?, ?)
    ''', (vendor_lower, mcc, platform_type, category))
    conn.commit()
    conn.close()
    print(f"[SQLite] Saved MCC mapping for {vendor_lower} -> {category}")
