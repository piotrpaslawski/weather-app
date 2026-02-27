import sys

from weather_core import WeatherError, format_weather, get_coordinates, get_weather


def main():
    """
    The method reads the city name from CLI arguments, fetches the weather,
    and prints the formatted report to terminal.

    Usage: python3 weather.py <city name>
    """
    if len(sys.argv) < 2:
        print("To display weather for a city, run: python3 weather.py <city>")
        sys.exit(1)

    # Join all remaining args to support multi-word city names
    city_name = " ".join(sys.argv[1:])

    try:
        latitude, longitude, display_name = get_coordinates(city_name)
        weather_data = get_weather(latitude, longitude)
        result = format_weather(display_name, weather_data)
        print(result)

    except WeatherError as e:
        print(
            f"Look out the window and check the weather, because an error occurred. {e}"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
