import sqlite3
import logging
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger("fraud_agent_db")

DB_PATH = Path(__file__).parent.parent / "data" / "fraud_cases.db"

def init_db():
    """Initialize the database with the fraud_cases table."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fraud_cases (
            username TEXT PRIMARY KEY,
            security_identifier TEXT,
            card_ending TEXT,
            transaction_name TEXT,
            transaction_amount TEXT,
            transaction_time TEXT,
            transaction_category TEXT,
            transaction_source TEXT,
            security_question TEXT,
            security_answer TEXT,
            status TEXT,
            outcome_note TEXT
        )
    """)
    conn.commit()
    conn.close()
    logger.info("Database initialized.")

def seed_db():
    """Seed the database with sample data if empty."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if data exists
    cursor.execute("SELECT count(*) FROM fraud_cases")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return

    sample_cases = [
        (
            "John",
            "12345",
            "4242",
            "ABC Industry",
            "$1,250.00",
            "Yesterday, 2:30 PM",
            "e-commerce",
            "alibaba.com",
            "What is your mother's maiden name?",
            "Smith",
            "pending_review",
            ""
        ),
        (
            "Alice",
            "67890",
            "1111",
            "Luxury Watches Ltd",
            "$5,000.00",
            "Today, 10:15 AM",
            "retail",
            "luxurywatches.com",
            "What was the name of your first pet?",
            "Fluffy",
            "pending_review",
            ""
        )
    ]

    cursor.executemany("""
        INSERT INTO fraud_cases (
            username, security_identifier, card_ending, transaction_name, 
            transaction_amount, transaction_time, transaction_category, 
            transaction_source, security_question, security_answer, status, outcome_note
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, sample_cases)
    
    conn.commit()
    conn.close()
    logger.info("Database seeded with sample cases.")

def get_case(username: str) -> Optional[Dict[str, Any]]:
    """Retrieve a fraud case by username."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM fraud_cases WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None

def update_case(username: str, status: str, outcome_note: str):
    """Update the status and outcome note of a fraud case."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE fraud_cases 
        SET status = ?, outcome_note = ?
        WHERE username = ?
    """, (status, outcome_note, username))
    
    conn.commit()
    conn.close()
    logger.info(f"Updated case for {username}: {status} - {outcome_note}")
