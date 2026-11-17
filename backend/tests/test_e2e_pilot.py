from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_live():
    r = client.get("/api/v1/health/live")
    assert r.status_code == 200
    assert r.json()["status"] == "alive"

def test_health_ready():
    r = client.get("/api/v1/health/ready")
    # may be 503 if no DB; accept either
    assert r.status_code in (200, 503)