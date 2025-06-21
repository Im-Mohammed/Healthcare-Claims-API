# tests/test_report.py
def test_generate_report_and_check_status(client):
    # Login
    login = client.post("/auth/login", json={"username": "testuser", "password": "testpass123"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Trigger report generation
    report = client.post("/claims/report", headers=headers)
    assert report.status_code == 200
    task_id = report.json()["task_id"]

    # Immediately check status (should be pending or processing)
    status = client.get(f"/claims/report/{task_id}", headers=headers)
    assert status.status_code == 200
    assert status.json()["status"] in ["PENDING", "PROCESSING", "COMPLETED"]
