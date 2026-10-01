FROM python:3.11-slim

WORKDIR /app

# System deps needed to build psycopg2
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=run.py \
    PYTHONUNBUFFERED=1

EXPOSE 5000

# gunicorn is used in place of the Flask dev server for a production-appropriate container
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "3", "run:app"]
