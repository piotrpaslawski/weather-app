from datetime import datetime

import requests


class WeatherError(Exception):
    """
    Raised when a weather or geocoding API request fails.
    """

    def __init__(self, message="Weather service is unavailable"):
        super().__init__(message)


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


def get_coordinates(city_name: str) -> tuple[float, float, str]:
    """
    Convert a city name to geographic coordinates using the Open-Meteo geocoding API.

    Args:
        city_name (str): The name of the city to look up (e.g. "Lublin").

    Returns:
        A tuple of (latitude, longitude, display_name), where display_name
        is a human-readable string like "Lublin, Poland".

    Raises:
        WeatherError: If the city is not found or the request fails.
    """
    try:
        response = requests.get(
            GEOCODING_URL,
            params={
                "name": city_name,
                "count": 1,
                "language": "pl",
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

    except requests.ConnectionError:
        raise WeatherError("No Internet connection.")
    except requests.HTTPError as e:
        raise WeatherError(f"Geocoding API server error: {e}.")
    except requests.Timeout:
        raise WeatherError("Geocoding API request timed out.")

    results = data.get("results")
    if not results:
        raise WeatherError(f"City not found: '{city_name}'.")

    city = results[0]
    display_name = city["name"]
    if country := city.get("country"):
        display_name += f", {country}"

    return city["latitude"], city["longitude"], display_name


def get_weather(latitude: float, longitude: float) -> dict:
    """
    Fetch weather forecast data for the given coordinates from Open-Meteo.

    Args:
        latitude (float): Latitude of the location.
        longitude (float): Longitude of the location.

    Returns:
        A raw dictionary with the full API response, containing
        "hourly" and "daily" keys with forecast data.
    """
    try:
        response = requests.get(
            WEATHER_URL,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "timezone": "auto",
                "hourly": ",".join(
                    [
                        "temperature_2m",
                        "precipitation_probability",
                        "snowfall",
                        "windspeed_10m",
                    ]
                ),
                "daily": ",".join(
                    [
                        "temperature_2m_max",
                        "temperature_2m_min",
                        "precipitation_probability_max",
                        "snowfall_sum",
                        "windspeed_10m_max",
                        "sunrise",
                        "sunset",
                    ]
                ),
                "forecast_days": 7,
            },
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    except requests.ConnectionError:
        raise WeatherError("No Internet connection.")
    except requests.HTTPError as e:
        raise WeatherError(f"Weather API server error: {e}.")
    except requests.Timeout:
        raise WeatherError("Weather API request timed out.")


def format_weather(city_display_name: str, data: dict) -> str:
    """
    Format raw API data into a human-readable weather report.

    Args:
        city_display_name: A readable city label, e.g. "Lublin, Polska".
        data: The raw dictionary returned by get_weather().

    Returns:
        A formatted multi-line string ready to be printed or returned
        as an HTTP response body.
    """
    lines = []

    def _row(cells: list[tuple[str, int]]) -> str:
        inner = " | ".join(f"{value:>{width}}" for value, width in cells)
        return f"| {inner} |"

    def _header_row(cells: list[tuple[str, int]]) -> str:
        inner = " | ".join(f"{value:<{width}}" for value, width in cells)
        return f"| {inner} |"

    def _divider(widths: list[int]) -> str:
        inner = "-+-".join("-" * w for w in widths)
        return f"+-{inner}-+"

    # --- Header ---
    lines.append(f"  Weather for: {city_display_name}")
    lines.append("")

    # --- Next 24 hours ---
    lines.append("NEXT 24 HOURS")
    lines.append("")

    hourly_columns = [
        ("Hour", 5),
        ("Temp", 8),
        ("Rain", 5),
        ("Snow", 7),
        ("Wind", 9),
    ]
    hourly_widths = [width for _, width in hourly_columns]

    lines.append(_header_row(hourly_columns))
    lines.append(_divider(hourly_widths))

    hourly = data["hourly"]

    for i in range(24):
        time_str = hourly["time"][i][11:]  # leaving just hour and minute
        temp = hourly["temperature_2m"][i]
        rain = hourly["precipitation_probability"][i]
        snow = hourly["snowfall"][i]
        wind = hourly["windspeed_10m"][i]

        lines.append(
            _row(
                [
                    (time_str, hourly_widths[0]),
                    (f"{temp:.1f} °C", hourly_widths[1]),
                    (f"{rain} %", hourly_widths[2]),
                    (f"{snow:.1f} cm", hourly_widths[3]),
                    (f"{wind:.1f} km/h", hourly_widths[4]),
                ]
            )
        )

    # --- 7-day forecast ---
    lines.append("")
    lines.append("7-DAY FORECAST")
    lines.append("")

    daily_columns = [
        ("Day", 10),
        ("Min", 8),
        ("Max", 8),
        ("Rain", 5),
        ("Snow", 7),
        ("Wind", 9),
        ("Sunrise", 7),
        ("Sunset", 7),
    ]
    daily_widths = [width for _, width in daily_columns]

    lines.append(_header_row(daily_columns))
    lines.append(_divider(daily_widths))

    daily = data["daily"]
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    for i in range(7):
        date = datetime.strptime(daily["time"][i], "%Y-%m-%d")
        day_name = days[date.weekday()]  # weekday(): 0=Mon, 6=Sun
        date_str = f"{day_name} {date.day:02}.{date.month:02}"

        temp_min = daily["temperature_2m_min"][i]
        temp_max = daily["temperature_2m_max"][i]
        rain = daily["precipitation_probability_max"][i]
        snow = daily["snowfall_sum"][i]
        wind = daily["windspeed_10m_max"][i]

        sunrise = daily["sunrise"][i][11:]
        sunset = daily["sunset"][i][11:]

        lines.append(
            _row(
                [
                    (date_str, daily_widths[0]),
                    (f"{temp_min:.1f} °C", daily_widths[1]),
                    (f"{temp_max:.1f} °C", daily_widths[2]),
                    (f"{rain} %", daily_widths[3]),
                    (f"{snow:.1f} cm", daily_widths[4]),
                    (f"{wind:.1f} km/h", daily_widths[5]),
                    (sunrise, daily_widths[6]),
                    (sunset, daily_widths[7]),
                ]
            )
        )

    lines.append("")
    return "\n".join(lines)
