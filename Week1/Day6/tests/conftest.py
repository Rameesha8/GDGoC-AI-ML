import os
import pytest
from fastapi.testclient import TestClient

# Set environment variables required by Pydantic Settings
os.environ.setdefault("API_KEY", "test-key")
os.environ.setdefault("APP_NAME", "Test API")
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("DEBUG", "false")

# Import app from Day5 package
from secrets_hygiene_practice.api import app


@pytest.fixture(scope="session")
def client():
    return TestClient(app)
