from datetime import datetime

import requests

from django.conf import settings


def get_weather_forecast(city: str, arrival_time: datetime):
    url = "https://api.openweathermap.org/data/2.5/forecast"

    params = {
        "q": city,
        "appid": settings.WEATHER_API_KEY,
        "units": "metric",
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    forecasts = response.json()["list"]

    closest = min(
        forecasts,
        key=lambda forecast: abs(
            datetime.strptime(
                forecast["dt_txt"],
                "%Y-%m-%d %H:%M:%S",
            ) - arrival_time.replace(tzinfo=None)
        ),
    )

    return {
        "city": city,
        "forecast_time": closest["dt_txt"],
        "temperature": closest["main"]["temp"],
        "feels_like": closest["main"]["feels_like"],
        "humidity": closest["main"]["humidity"],
        "description": closest["weather"][0]["description"],
        "wind_speed": closest["wind"]["speed"],
    }