from __future__ import annotations

from database.db import execute, fetch_all


def create_supplier(name: str, location: str, country: str, product_category: str, contact_information: str, status: str) -> int:
    return execute(
        """
        INSERT INTO suppliers (name, location, country, product_category, contact_information, status)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (name, location, country, product_category, contact_information, status),
    )


def list_suppliers() -> list[dict]:
    return fetch_all("SELECT * FROM suppliers ORDER BY created_at DESC")
