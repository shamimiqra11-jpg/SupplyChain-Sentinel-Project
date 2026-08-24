from __future__ import annotations

import requests

from database.db import execute, fetch_all, fetch_one


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Heavy drizzle",
    61: "Light rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Light snow",
    73: "Moderate snow",
    75: "Heavy snow",
    80: "Rain showers",
    81: "Moderate rain showers",
    82: "Heavy rain showers",
    95: "Thunderstorm",
    96: "Thunderstorm with hail",
    99: "Severe thunderstorm",
}


def geocode_location(location: str, country: str) -> dict:
    response = requests.get(
        GEOCODING_URL,
        params={
            "name": location,
            "count": 1,
            "language": "en",
            "format": "json",
        },
        timeout=15,
    )

    response.raise_for_status()
    results = response.json().get("results", [])

    if not results:
        raise ValueError(f"Location not found: {location}, {country}")

    item = results[0]

    return {
        "latitude": item["latitude"],
        "longitude": item["longitude"],
        "resolved_name": item.get("name", location),
        "country": item.get("country", country),
    }


def calculate_weather_risk(current: dict) -> dict:
    temperature = float(current.get("temperature_2m", 0) or 0)
    apparent = float(current.get("apparent_temperature", temperature) or temperature)
    precipitation = float(current.get("precipitation", 0) or 0)
    wind = float(current.get("wind_speed_10m", 0) or 0)
    code = int(current.get("weather_code", 0) or 0)

    score = 0
    alerts = []

    if temperature >= 40 or apparent >= 45:
        score += 45
        alerts.append("Extreme heat may disrupt workers and transportation.")
    elif temperature >= 35 or apparent >= 38:
        score += 25
        alerts.append("High heat may affect logistics and delivery reliability.")

    if precipitation >= 10:
        score += 25
        alerts.append("Heavy precipitation may cause flooding or transport delays.")
    elif precipitation >= 2:
        score += 10
        alerts.append("Rain may affect delivery schedules.")

    if wind >= 70:
        score += 35
        alerts.append("Very strong winds may disrupt logistics.")
    elif wind >= 40:
        score += 18
        alerts.append("Strong winds may create transportation delays.")

    if code in {95, 96, 99}:
        score += 45
        alerts.append("Thunderstorm conditions create significant disruption risk.")
    elif code in {65, 75, 82}:
        score += 20

    score = min(score, 100)

    if score < 20:
        level = "Low"
    elif score < 45:
        level = "Medium"
    elif score < 70:
        level = "High"
    else:
        level = "Critical"

    condition = WEATHER_CODES.get(code, f"Weather code {code}")

    if not alerts:
        alerts.append("Current weather conditions indicate low disruption risk.")

    return {
        "weather_risk_score": score,
        "weather_risk_level": level,
        "weather_condition": condition,
        "alert_message": " ".join(alerts),
    }


def get_live_weather(location: str, country: str) -> dict:
    place = geocode_location(location, country)

    response = requests.get(
        WEATHER_URL,
        params={
            "latitude": place["latitude"],
            "longitude": place["longitude"],
            "current": "temperature_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m",
            "timezone": "auto",
        },
        timeout=15,
    )

    response.raise_for_status()
    current = response.json().get("current")

    if not current:
        raise ValueError("Live weather data was unavailable.")

    risk = calculate_weather_risk(current)

    return {
        **place,
        **current,
        **risk,
    }


def save_weather_assessment(supplier_id: int, weather: dict) -> None:
    execute(
        """
        INSERT INTO weather_assessments (
            supplier_id, temperature, apparent_temperature,
            precipitation, wind_speed, weather_code,
            weather_condition, weather_risk_score,
            weather_risk_level, alert_message,
            latitude, longitude
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            supplier_id,
            weather.get("temperature_2m"),
            weather.get("apparent_temperature"),
            weather.get("precipitation"),
            weather.get("wind_speed_10m"),
            weather.get("weather_code"),
            weather["weather_condition"],
            weather["weather_risk_score"],
            weather["weather_risk_level"],
            weather["alert_message"],
            weather["latitude"],
            weather["longitude"],
        ),
    )


def latest_weather_for_supplier(supplier_id: int):
    return fetch_one(
        """
        SELECT *
        FROM weather_assessments
        WHERE supplier_id = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (supplier_id,),
    )


def weather_risk_register():
    return fetch_all(
        """
        SELECT w.*, s.name AS supplier_name, s.location, s.country
        FROM weather_assessments w
        JOIN suppliers s ON s.id = w.supplier_id
        WHERE w.id IN (
            SELECT MAX(id)
            FROM weather_assessments
            GROUP BY supplier_id
        )
        ORDER BY w.weather_risk_score DESC
        """
    )