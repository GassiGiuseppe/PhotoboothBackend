# syntax=docker/dockerfile:1
FROM python:3.12-slim

# Make Python friendlier in containers
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install Python deps first (cache-friendly)
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy app code and SQL schemas
COPY app ./app
# COPY schema ./schema

# Expose FastAPI port
EXPOSE 8000

# Environment (override in compose/prod as needed)
# DATABASE_URL example: postgresql+asyncpg://app:secret@db:5432/photoindex
ENV DATABASE_URL="" \
    GCS_BUCKET="" \
    GCS_PREFIX="photos/" \
    SIGNED_URL_TTL="3600"

# Run the API
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
