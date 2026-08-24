from __future__ import annotations


def calculate_simulation(
    delivery_delay: int,
    cost_increase: float,
    demand_increase: float,
    inventory_level: float,
    weather_severity: str,
) -> dict:

    # Delivery delay impact
    delay_impact = min(delivery_delay * 2.5, 30)

    # Cost impact
    cost_impact = min(cost_increase * 1.5, 25)

    # Demand impact
    demand_impact = min(demand_increase * 1.2, 20)

    # Lower inventory means higher risk
    inventory_impact = max(0, (100 - inventory_level) * 0.25)

    # Weather impact
    weather_scores = {
        "Low": 5,
        "Medium": 12,
        "High": 22,
        "Critical": 30,
    }

    weather_impact = weather_scores.get(weather_severity, 0)

    overall_score = min(
        round(
            delay_impact
            + cost_impact
            + demand_impact
            + inventory_impact
            + weather_impact,
            1,
        ),
        100,
    )

    if overall_score < 25:
        risk_level = "Low"
    elif overall_score < 50:
        risk_level = "Medium"
    elif overall_score < 75:
        risk_level = "High"
    else:
        risk_level = "Critical"

    # Financial impact estimate
    financial_impact = round(
        (cost_increase * 1000) + (delivery_delay * 500),
        2,
    )

    # Recommendations
    recommendations = []

    if delivery_delay > 10:
        recommendations.append(
            "Identify alternative suppliers or expedite transportation."
        )

    if cost_increase > 15:
        recommendations.append(
            "Review supplier contracts and evaluate alternative sourcing options."
        )

    if demand_increase > 20:
        recommendations.append(
            "Increase production planning and maintain additional safety stock."
        )

    if inventory_level < 30:
        recommendations.append(
            "Inventory is critically low. Increase replenishment immediately."
        )

    if weather_severity in ["High", "Critical"]:
        recommendations.append(
            "Monitor weather disruptions and prepare alternative logistics routes."
        )

    if not recommendations:
        recommendations.append(
            "Current scenario shows manageable disruption risk. Continue monitoring."
        )

    return {
        "overall_score": overall_score,
        "risk_level": risk_level,
        "delivery_impact": round(delay_impact, 1),
        "cost_impact": round(cost_impact, 1),
        "demand_impact": round(demand_impact, 1),
        "inventory_impact": round(inventory_impact, 1),
        "weather_impact": round(weather_impact, 1),
        "financial_impact": financial_impact,
        "recommendations": recommendations,
    }