from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
DATABASE_PATH = DATA_DIR / "supplychain_sentinel.db"
SCHEMA_PATH = ROOT_DIR / "database" / "schema.sql"


def get_connection() -> sqlite3.Connection:
    """Return a SQLite connection configured for dictionary-like rows."""

    DATA_DIR.mkdir(exist_ok=True)

    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row

    conn.execute("PRAGMA foreign_keys = ON")

    return conn


def init_db() -> None:
    """Create application tables and migrate existing SQLite databases."""

    with get_connection() as conn:

        # Create tables from schema.sql
        conn.executescript(SCHEMA_PATH.read_text())

        # Get existing columns from risk_assessments
        columns = {
            row["name"]
            for row in conn.execute(
                "PRAGMA table_info(risk_assessments)"
            ).fetchall()
        }

        # Required risk factor columns
        required_columns = {
            "reliability": "REAL DEFAULT 0",
            "geographic_risk": "REAL DEFAULT 0",
            "financial_stability": "REAL DEFAULT 0",
            "delivery_performance": "REAL DEFAULT 0",
            "inventory_dependency": "REAL DEFAULT 0",
        }

        # Add missing columns safely
        for column, column_type in required_columns.items():

            if column not in columns:

                conn.execute(
                    f"""
                    ALTER TABLE risk_assessments
                    ADD COLUMN {column} {column_type}
                    """
                )

        conn.commit()


def fetch_all(
    query: str,
    params: tuple[Any, ...] = ()
) -> list[dict[str, Any]]:

    with get_connection() as conn:

        rows = conn.execute(
            query,
            params
        ).fetchall()

    return [dict(row) for row in rows]


def fetch_one(
    query: str,
    params: tuple[Any, ...] = ()
) -> dict[str, Any] | None:

    with get_connection() as conn:

        row = conn.execute(
            query,
            params
        ).fetchone()

    return dict(row) if row else None


def execute(
    query: str,
    params: tuple[Any, ...] = ()
) -> int:

    with get_connection() as conn:

        cursor = conn.execute(
            query,
            params
        )

        conn.commit()

        return int(cursor.lastrowid)