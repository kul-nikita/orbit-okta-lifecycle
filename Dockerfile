# Multi-stage build: install dependencies in a builder stage and copy only the installed packages into the final runtime image

FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /install

COPY requirements.txt .
# Install runtime deps using --prefix so console entrypoints are installed under /install/bin
RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir --prefix=/install -r requirements.txt


FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOME=/home/app \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true

WORKDIR /app

# Copy installed packages and scripts from builder into /usr/local so scripts are on PATH
COPY --from=builder /install /usr/local

COPY . .

# Create app user and set ownership
RUN addgroup --system app \
    && adduser --system --home /home/app --ingroup app app \
    && chown -R app:app /app

USER app

EXPOSE 8501

# Healthcheck using python stdlib to avoid installing extra tooling
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request,sys;\ntry:\n  resp=urllib.request.urlopen('http://127.0.0.1:8501', timeout=4);\n  sys.exit(0 if getattr(resp, 'status', None)==200 else 1)\nexcept Exception:\n  sys.exit(1)"

CMD ["streamlit", "run", "src/app.py", "--server.port=8501"]
