FROM python:3.11-slim

WORKDIR /app

# Copy Day10 source code
COPY Week2/Day10/src /app/src

# Upgrade pip and install dependencies
RUN python -m pip install --upgrade pip && python -m pip install \
    "fastapi[standard]" \
    pydantic-settings \
    "psycopg[binary]" \
    sqlalchemy \
    alembic \
    qdrant-client
RUN apt-get update && apt-get install -y gcc libpq-dev
RUN python -m pip install --upgrade pip
RUN python -m pip install sqlalchemy psycopg2-binary alembic

# Start FastAPI
ENV PYTHONPATH=/app/Week2/Day10/src
CMD ["uvicorn", "Week2.Day10.src.secrets_hygiene_practice.api:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
