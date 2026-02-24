FROM python:3.12.8-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY weather_core.py .
COPY server.py .

CMD ["python3", "server.py"]