"""
Minimal smoke tests for the core backend flows: register -> login -> browse
products -> add to cart -> checkout -> event logged.

Run with:
    pytest tests/ -v

Uses an in-memory SQLite database (TestingConfig) so tests don't require a
running PostgreSQL instance.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from app import create_app
from app.config import TestingConfig
from app.extensions import db
from app.models.product import Product


@pytest.fixture
def app():
    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()
        product = Product(name="Test Widget", price=19.99, stock=10, category="Test")
        db.session.add(product)
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def register_and_login(client, email="test@example.com"):
    client.post("/api/auth/register", json={"email": email, "password": "Password123!"})
    resp = client.post("/api/auth/login", json={"email": email, "password": "Password123!"})
    return resp.get_json()["data"]["access_token"]


def test_health_check(client):
    resp = client.get("/health")
    assert resp.status_code == 200


def test_register_and_login(client):
    resp = client.post("/api/auth/register", json={"email": "a@example.com", "password": "Password123!"})
    assert resp.status_code == 201
    assert resp.get_json()["success"] is True

    resp = client.post("/api/auth/login", json={"email": "a@example.com", "password": "Password123!"})
    assert resp.status_code == 200
    assert "access_token" in resp.get_json()["data"]


def test_list_products(client):
    resp = client.get("/api/products")
    assert resp.status_code == 200
    assert resp.get_json()["data"]["total"] == 1


def test_cart_and_checkout_flow(client):
    token = register_and_login(client, "buyer@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    products = client.get("/api/products").get_json()["data"]["products"]
    product_id = products[0]["id"]

    resp = client.post("/api/cart", json={"product_id": product_id, "quantity": 2}, headers=headers)
    assert resp.status_code == 201
    assert resp.get_json()["data"]["cart"]["items"][0]["quantity"] == 2

    resp = client.post("/api/checkout", json={}, headers=headers)
    assert resp.status_code == 201
    assert resp.get_json()["data"]["order"]["total_amount"] == pytest.approx(39.98)

    # Cart should be empty after checkout.
    resp = client.get("/api/cart", headers=headers)
    assert resp.get_json()["data"]["cart"]["items"] == []


def test_event_logging(client):
    resp = client.post("/api/events", json={"session_id": "s1", "event_type": "search", "metadata": {"query": "widget"}})
    assert resp.status_code == 201
    assert resp.get_json()["data"]["event"]["event_type"] == "search"


def test_invalid_event_type_rejected(client):
    resp = client.post("/api/events", json={"session_id": "s1", "event_type": "not_a_real_event"})
    assert resp.status_code == 400
