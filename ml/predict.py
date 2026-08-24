from pathlib import Path
import joblib


BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "disruption_model.pkl"


def load_model():
    """Load the trained disruption prediction model."""
    model_data = joblib.load(MODEL_PATH)

    return (
        model_data["model"],
        model_data["features"],
        model_data["accuracy"],
    )


def predict_disruption(
    supplier_reliability,
    geographic_risk,
    financial_stability,
    delivery_performance,
    inventory_dependency,
    weather_risk,
):
    """Predict supply chain disruption probability."""

    model, features, accuracy = load_model()

    input_data = [[
        supplier_reliability,
        geographic_risk,
        financial_stability,
        delivery_performance,
        inventory_dependency,
        weather_risk,
    ]]

    probability = model.predict_proba(input_data)[0][1]
    prediction = model.predict(input_data)[0]

    disruption_probability = round(probability * 100, 2)

    if disruption_probability < 25:
        risk_level = "Low"
    elif disruption_probability < 50:
        risk_level = "Medium"
    elif disruption_probability < 75:
        risk_level = "High"
    else:
        risk_level = "Critical"

    if prediction == 1:
        prediction_label = "Disruption Likely"
    else:
        prediction_label = "Disruption Unlikely"

    return {
        "disruption_probability": disruption_probability,
        "prediction": prediction_label,
        "risk_level": risk_level,
        "model_accuracy": round(accuracy * 100, 2),
        "features": features,
    }