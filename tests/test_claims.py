# tests/test_claims.py
def test_create_and_get_claim(client):
    # First login to get token
    login = client.post("/auth/login", json={"username": "testuser", "password": "testpass123"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create Claim
    claim_data = {
        "patient_name": "John Doe",
        "diagnosis_code": "D123",
        "procedure_code": "P456",
        "claim_amount": 1000.50
    }
    create = client.post("/claims", headers=headers, json=claim_data)
    assert create.status_code == 200
    claim_id = create.json()["id"]

    # Get Claim by ID
    get_claim = client.get(f"/claims/{claim_id}", headers=headers)
    assert get_claim.status_code == 200
    assert get_claim.json()["patient_name"] == "John Doe"
