# Week2/Day8/Dockerfile
FROM python:3.11-slim

# Good defaults
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

WORKDIR /app

# Copy only the src folder from Week1/Day5
COPY Week1/Day5/src /app/src

# Install dependencies
RUN python -m pip install --upgrade pip \
    && python -m pip install "fastapi[standard]" pydantic-settings

EXPOSE 8000

# Run the FastAPI app
CMD ["uvicorn", "secrets_hygiene_practice.api:app", "--host", "0.0.0.0", "--port", "8000"]
