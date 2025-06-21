# tests/test_auth.py
def test_signup_and_login(client):
    # Signup
    response = client.post("/auth/signup", json={
        "username": "testuser",
        "password": "testpass123"
    })
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

    # Login
    response = client.post("/auth/login", json={
        "username": "testuser",
        "password": "testpass123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
