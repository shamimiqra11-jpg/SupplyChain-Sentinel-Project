from __future__ import annotations

from database.db import execute, fetch_all


def create_purchase_order(po_number: str, supplier_id: int, product_id: int, quantity: int, order_date: str, expected_delivery: str, status: str, total_value: float) -> int:
    return execute(
        """
        INSERT INTO purchase_orders (po_number, supplier_id, product_id, quantity, order_date, expected_delivery, status, total_value)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (po_number, supplier_id, product_id, quantity, order_date, expected_delivery, status, total_value),
    )


def list_purchase_orders() -> list[dict]:
    return fetch_all(
        """
        SELECT po.*, s.name AS supplier_name, p.name AS product_name
        FROM purchase_orders po
        JOIN suppliers s ON s.id = po.supplier_id
        JOIN products p ON p.id = po.product_id
        ORDER BY po.created_at DESC
        """
    )
