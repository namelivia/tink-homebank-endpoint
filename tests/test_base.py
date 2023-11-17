import os
import pytest
from fastapi.testclient import TestClient
from app.main import app

os.environ["TESTING"] = "True"
os.environ["TINK_CLIENT_ID"] = "tink_client_id"
os.environ["TINK_CLIENT_SECRET"] = "tink_client_secret"


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as client:
        yield client
