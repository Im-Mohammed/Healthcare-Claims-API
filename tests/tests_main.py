import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app, get_db
from app.Utils.models import Base
import tempfile
import os

# Create a test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create tables
Base.metadata.create_all(bind=engine)

client = TestClient(app)

@pytest.fixture
def test_user():
    # Create a test user
    user_data = {"username": "testuser", "password": "testpass123"}
    response = client.post("/auth/signup", json=user_data)
    return user_data

@pytest.fixture
def auth_headers(test_user):
    # Login and get token
    response = client.post("/auth/login", json=test_user)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_signup():
    user_data = {"username": "newuser", "password": "password123"}
    response = client.post("/auth/signup", json=user_data)
    assert response.status_code == 201
    assert response.json()["username"] == "newuser"

def test_login(test_user):
    response = client.post("/auth/login", json=test_user)
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_create_claim(auth_headers):
    claim_data = {
        "patient_name": "John Doe",
        "diagnosis_code": "A01.1",
        "procedure_code": "12345",
        "claim_amount": 1500.50
    }
    response = client.post("/claims", json=claim_data, headers=auth_headers)
    assert response.status_code == 201
    assert response.json()["patient_name"] == "John Doe"
    assert response.json()["status"] == "PENDING"

def test_get_claims(auth_headers):
    # First create a claim
    claim_data = {
        "patient_name": "Jane Doe",
        "diagnosis_code": "B02.1",
        "procedure_code": "67890",
        "claim_amount": 2000.00
    }
    client.post("/claims", json=claim_data, headers=auth_headers)
    
    # Then fetch claims
    response = client.get("/claims", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()["claims"]) > 0

def test_update_claim_status(auth_headers):
    # Create a claim first
    claim_data = {
        "patient_name": "Bob Smith",
        "diagnosis_code": "C01.1",
        "procedure_code": "11111",
        "claim_amount": 3000.00
    }
    create_response = client.post("/claims", json=claim_data, headers=auth_headers)
    claim_id = create_response.json()["id"]
    
    # Update claim status
    update_data = {"status": "APPROVED"}
    response = client.put(f"/claims/{claim_id}", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "APPROVED"

def test_generate_report(auth_headers):
    response = client.post("/claims/report", headers=auth_headers)
    assert response.status_code == 200
    assert "task_id" in response.json()

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
