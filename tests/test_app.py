import os
import sys

# Ensure src is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from fastapi.testclient import TestClient
from app import app, activities

client = TestClient(app)


def test_root_redirect():
    res = client.get("/", follow_redirects=False)
    assert res.status_code in (301, 302, 303, 307, 308)
    assert res.headers["location"] == "/static/index.html"


def test_get_activities():
    res = client.get("/activities")
    assert res.status_code == 200
    data = res.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_success():
    activity = "Chess Club"
    email = "testuser@example.com"
    original = activities[activity]["participants"].copy()

    try:
        res = client.post(f"/activities/{activity}/signup", params={"email": email})
        assert res.status_code == 200
        assert email in res.json()["message"]
        # Ensure participant was added to the in-memory activities
        assert email in activities[activity]["participants"]
    finally:
        # Restore original participants to avoid side effects
        activities[activity]["participants"] = original


def test_signup_nonexistent_activity():
    res = client.post("/activities/NoSuchActivity/signup", params={"email": "x@y.com"})
    assert res.status_code == 404
