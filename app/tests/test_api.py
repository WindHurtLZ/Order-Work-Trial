from fastapi.testclient import TestClient
from app.main import app
from app.database.database import engine
from app.database.models import Base
import pytest

@pytest.fixture(scope="module")
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def client(test_db):
    return TestClient(app)

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_create_order(client):
    order_data = {
        "symbol": "NVDA",
        "price": 140.0,
        "quantity": 1,
        "order_type": "limit"
    }
    response = client.post("/api/orders", json=order_data)
    assert response.status_code == 201
    assert "id" in response.json()

def test_get_orders(client):
    response = client.get("/api/orders")
    assert response.status_code == 200
    assert isinstance(response.json(), list)