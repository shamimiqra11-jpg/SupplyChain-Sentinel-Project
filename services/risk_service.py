from __future__ import annotations

from database.db import fetch_all, fetch_one, execute


FACTOR_LABELS = {
    "reliability": "Supplier Reliability",
    "geographic_risk": "Geographic Concentration Risk",
    "financial_stability": "Financial Stability",
    "delivery_performance": "Delivery Performance",
    "inventory_dependency": "Inventory Dependency",
}


FACTOR_WEIGHTS = {
    "reliability": 0.25,
    "geographic_risk": 0.20,
    "financial_stability": 0.20,
    "delivery_performance": 0.20,
    "inventory_dependency": 0.15,
}


def calculate_risk(factors: dict) -> dict:
    """
    Calculate weighted supplier risk score.
    Factor values should be between 0 and 100.
    Higher values indicate higher risk.
    """

    factors = {
        "reliability": float(factors.get("reliability", 0)),
        "geographic_risk": float(factors.get("geographic_risk", 0)),
        "financial_stability": float(factors.get("financial_stability", 0)),
        "delivery_performance": float(factors.get("delivery_performance", 0)),
        "inventory_dependency": float(factors.get("inventory_dependency", 0)),
    }

    contributions = {
        factor: round(value * FACTOR_WEIGHTS[factor], 2)
        for factor, value in factors.items()
    }

    risk_score = round(sum(contributions.values()), 2)

    if risk_score < 25:
        risk_level = "Low"
    elif risk_score < 50:
        risk_level = "Medium"
    elif risk_score < 75:
        risk_level = "High"
    else:
        risk_level = "Critical"

    highest_factor = max(contributions, key=contributions.get)

    explanation = (
        f"The supplier has a {risk_level.lower()} overall risk level. "
        f"The largest risk contributor is "
        f"{FACTOR_LABELS[highest_factor]}."
    )

    mitigation_actions = {
        "reliability": "Improve supplier monitoring and consider backup suppliers.",
        "geographic_risk": "Diversify suppliers across different geographic regions.",
        "financial_stability": "Review supplier financial health and reduce dependency.",
        "delivery_performance": "Monitor delivery delays and establish contingency plans.",
        "inventory_dependency": "Increase safety stock or identify alternative suppliers.",
    }

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "factors": factors,
        "contributions": contributions,
        "highest_factor": highest_factor,
        "explanation": explanation,
        "recommendation": mitigation_actions[highest_factor],
    }


def save_risk_assessment(supplier_id: int, assessment: dict) -> None:
    factors = assessment.get("factors", {})

    execute(
        """
        INSERT INTO risk_assessments (
            supplier_id,
            risk_score,
            risk_level,
            reliability,
            geographic_risk,
            financial_stability,
            delivery_performance,
            inventory_dependency
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            supplier_id,
            assessment["risk_score"],
            assessment["risk_level"],
            factors.get("reliability", 0),
            factors.get("geographic_risk", 0),
            factors.get("financial_stability", 0),
            factors.get("delivery_performance", 0),
            factors.get("inventory_dependency", 0),
        ),
    )


def supplier_history(supplier_id: int):
    return fetch_all(
        """
        SELECT *
        FROM risk_assessments
        WHERE supplier_id = ?
        ORDER BY created_at DESC
        """,
        (supplier_id,),
    )


def latest_risk_register():
    return fetch_all(
        """
        SELECT
            r.*,
            s.name AS supplier_name,
            s.country,
            s.location
        FROM risk_assessments r
        JOIN suppliers s ON r.supplier_id = s.id
        WHERE r.id IN (
            SELECT MAX(id)
            FROM risk_assessments
            GROUP BY supplier_id
        )
        ORDER BY r.risk_score DESC
        """
    )


def dashboard_metrics() -> dict:
    total_suppliers = (
        fetch_one("SELECT COUNT(*) AS count FROM suppliers")
        or {"count": 0}
    )

    high_risk_suppliers = (
        fetch_one(
            """
            SELECT COUNT(*) AS count
            FROM risk_assessments
            WHERE risk_level IN ('High', 'Critical')
            """
        )
        or {"count": 0}
    )

    active_pos = (
        fetch_one(
            """
            SELECT COUNT(*) AS count
            FROM purchase_orders
            WHERE status IN ('Open', 'In Transit')
            """
        )
        or {"count": 0}
    )

    recent_alerts = fetch_all(
        """
        SELECT *
        FROM risk_assessments
        ORDER BY created_at DESC
        LIMIT 5
        """
    )

    health = max(0, 100 - (int(high_risk_suppliers["count"]) * 10))

    return {
        "health": health,
        "total_suppliers": total_suppliers["count"],
        "high_risk_suppliers": high_risk_suppliers["count"],
        "active_purchase_orders": active_pos["count"],
        "recent_alerts": recent_alerts,
    }