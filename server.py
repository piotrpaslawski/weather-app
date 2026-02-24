from flask import Flask, Response

from weather_core import WeatherError, format_weather, get_coordinates, get_weather

app = Flask(__name__)


@app.route("/<path:city>")
def weather_endpoint(city: str) -> Response:
    """
    HTTP endpoint that returns a plain-text weather report for a given city.
    The `path:` converter in the route allows slashes and spaces in the city name,
    so URLs like /New York or /Nowy Jork are handled correctly.

    Args:
        city: City name captured from the URL path.

    Returns:
        A Flask Response with plain text content.
    """
    try:
        latitude, longitude, display_name = get_coordinates(city)
        weather_data = get_weather(latitude, longitude)
        result = format_weather(display_name, weather_data)
        return Response(result, status=200, mimetype="text/plain; charset=utf-8")

    except WeatherError as e:
        return Response(
            f"Even meteorologists are wrong sometimes: {e}\n",
            status=404,
            mimetype="text/plain; charset=utf-8",
        )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
