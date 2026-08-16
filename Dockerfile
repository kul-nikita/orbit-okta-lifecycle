FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Pass OKTA_DOMAIN / OKTA_API_TOKEN at runtime, e.g.:
#   docker build -t orbit .
#   docker run --rm --env-file .env orbit --help
CMD ["python", "-m", "src.cli"]
