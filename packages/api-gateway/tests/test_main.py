import pytest
from fastapi.testclient import TestClient
from api_gateway.main import app
from api_gateway.security import API_KEY

client = TestClient(app)

def test_read_root_unauthorized():
    response = client.get("/api/companies")
    assert response.status_code == 403

def test_read_root_wrong_key():
    response = client.get("/api/companies", headers={"X-API-Key": "wrong_key"})
    assert response.status_code == 401

def test_get_companies():
    response = client.get("/api/companies", headers={"X-API-Key": API_KEY})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_company():
    response = client.get("/api/companies/AAPL", headers={"X-API-Key": API_KEY})
    assert response.status_code == 200
    assert response.json()["company"]["ticker"] == "AAPL"

def test_get_analysis_screen():
    response = client.get("/api/analysis/screen", headers={"X-API-Key": API_KEY})
    assert response.status_code == 200
    assert "companies" in response.json()

def test_get_bulk_analysis():
    response = client.get("/api/analysis/bulk/some_job_id", headers={"X-API-Key": API_KEY})
    assert response.status_code == 200
    assert response.json()["id"] == "some_job_id"

def test_post_bulk_analysis():
    response = client.post("/api/analysis/bulk", headers={"X-API-Key": API_KEY}, json={"tickers": ["AAPL", "GOOG"]})
    assert response.status_code == 200
    assert response.json()["status"] == "PENDING" 