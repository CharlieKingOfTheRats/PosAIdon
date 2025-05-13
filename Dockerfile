  FROM python:3.10-slim

  WORKDIR /app

  COPY requirements.txt .

  RUN pip install --no-cache-dir -r requirements.txt

  COPY . .

  EXPOSE 8000

  CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8000"]

FROM python:3.10-slim

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
