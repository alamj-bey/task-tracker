# Minimal image for the Task Tracker FastAPI backend
FROM python:3.12-slim

WORKDIR /app

# Install dependencies first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only what the backend needs to run.
# frontend/ and tests/ are intentionally excluded via .dockerignore --
# this image serves the API only, not the static frontend or test suite.
COPY app/ ./app/

# Run as a non-root user rather than the default root
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
