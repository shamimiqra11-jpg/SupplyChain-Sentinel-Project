from __future__ import annotations

from database.db import execute, fetch_all


def create_product(name: str, sku: str, category: str, supplier_id: int | None, unit_cost: float, inventory_level: int, status: str) -> int:
    return execute(
        """
        INSERT INTO products (name, sku, category, supplier_id, unit_cost, inventory_level, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (name, sku, category, supplier_id, unit_cost, inventory_level, status),
    )


def list_products() -> list[dict]:
    return fetch_all(
        """
        SELECT p.*, COALESCE(s.name, 'Unassigned') AS supplier_name
        FROM products p
        LEFT JOIN suppliers s ON s.id = p.supplier_id
        ORDER BY p.created_at DESC
        """
    )
