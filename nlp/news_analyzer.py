from __future__ import annotations


RISK_KEYWORDS = {
    "Weather Disruption": [
        "rain", "flood", "storm", "cyclone",
        "hurricane", "heatwave", "snow",
        "drought", "weather",
    ],
    "Transportation Disruption": [
        "transport", "delay", "road closed",
        "port", "shipping", "traffic",
        "logistics", "route blocked",
    ],
    "Supplier Risk": [
        "supplier failure", "supplier shutdown",
        "factory closed", "production stopped",
        "manufacturing issue",
    ],
    "Labor Disruption": [
        "strike", "protest", "worker shortage",
        "labor shortage", "union",
    ],
    "Political / Geographic Risk": [
        "war", "conflict", "sanctions",
        "political unrest", "border closure",
        "geopolitical",
    ],
    "Supply Shortage": [
        "shortage", "scarcity", "out of stock",
        "inventory shortage", "material shortage",
    ],
}


def analyze_news(text: str) -> dict:
    """
    Analyze supply-chain-related news or text
    and identify potential disruption risks.
    """

    text = text.lower()

    detected_risks = []
    matched_keywords = []

    for category, keywords in RISK_KEYWORDS.items():

        category_matches = []

        for keyword in keywords:
            if keyword in text:
                category_matches.append(keyword)
                matched_keywords.append(keyword)

        if category_matches:
            detected_risks.append({
                "category": category,
                "keywords": category_matches,
            })

    risk_count = len(matched_keywords)

    risk_score = min(risk_count * 15, 100)

    if risk_score < 25:
        risk_level = "Low"
    elif risk_score < 50:
        risk_level = "Medium"
    elif risk_score < 75:
        risk_level = "High"
    else:
        risk_level = "Critical"

    if not detected_risks:
        summary = (
            "No major supply chain disruption signals "
            "were detected in the provided text."
        )
    else:
        categories = ", ".join(
            risk["category"] for risk in detected_risks
        )

        summary = (
            f"Potential supply chain disruption signals detected "
            f"in the following areas: {categories}."
        )

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "detected_risks": detected_risks,
        "matched_keywords": matched_keywords,
        "summary": summary,
    }