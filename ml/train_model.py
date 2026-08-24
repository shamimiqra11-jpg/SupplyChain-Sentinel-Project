from pathlib import Path
import numpy as np
import pandas as pd
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


# Project paths
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "disruption_model.pkl"


def generate_training_data(n_samples=1000):
    """
    Generate synthetic supply-chain risk data for
    training the disruption prediction model.
    """

    np.random.seed(42)

    supplier_reliability = np.random.randint(0, 101, n_samples)
    geographic_risk = np.random.randint(0, 101, n_samples)
    financial_stability = np.random.randint(0, 101, n_samples)
    delivery_performance = np.random.randint(0, 101, n_samples)
    inventory_dependency = np.random.randint(0, 101, n_samples)
    weather_risk = np.random.randint(0, 101, n_samples)

    risk_score = (
        supplier_reliability * 0.20
        + geographic_risk * 0.15
        + financial_stability * 0.20
        + delivery_performance * 0.20
        + inventory_dependency * 0.15
        + weather_risk * 0.10
    )

    noise = np.random.normal(0, 8, n_samples)
    final_score = risk_score + noise

    disruption = (final_score >= 50).astype(int)

    data = pd.DataFrame({
        "supplier_reliability": supplier_reliability,
        "geographic_risk": geographic_risk,
        "financial_stability": financial_stability,
        "delivery_performance": delivery_performance,
        "inventory_dependency": inventory_dependency,
        "weather_risk": weather_risk,
        "disruption": disruption,
    })

    return data


def train_model():
    data = generate_training_data()

    features = [
        "supplier_reliability",
        "geographic_risk",
        "financial_stability",
        "delivery_performance",
        "inventory_dependency",
        "weather_risk",
    ]

    X = data[features]
    y = data["disruption"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
    )

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)

    joblib.dump(
        {
            "model": model,
            "features": features,
            "accuracy": accuracy,
        },
        MODEL_PATH,
    )

    print("Model trained successfully!")
    print(f"Accuracy: {accuracy:.2%}")
    print(f"Model saved at: {MODEL_PATH}")


if __name__ == "__main__":
    train_model()