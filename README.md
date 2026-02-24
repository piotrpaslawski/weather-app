# Weather App

A simple weather forecast app using the [Open-Meteo](https://open-meteo.com/) API.

Shows:
- hour-by-hour temperature, rain chance, snowfall and wind speed for the next 24 hours
- daily min/max temperature, rain chance, snowfall, wind speed and sunrise/sunset for the next 7 days

## Usage

You can use just like you prefere :)

### CLI

```bash
python3 weather.py Lublin
python3 weather.py New York
```

### HTTP server

```bash
python3 server.py
```

Then open in browser or with `curl`:

```
http://localhost:8000/Lublin
```
```bash
curl localhost:8000/Lublin
```

## Running with Docker

```bash
docker build -t weather-app .
docker run -d --name weather --restart unless-stopped -p 8000:8000 weather-app
```

Then open `http://<localhost>:8000/<city>` in your browser.

## Requirements

- Python 3.12+
- requests
- flask

```bash
pip install -r requirements.txt
```

## Project structure

```
weather_core.py   # core logic: geocoding, fetching and formatting weather data
weather.py        # CLI entry point
server.py         # HTTP server entry point (Flask)
Dockerfile        # Docker image definition
```