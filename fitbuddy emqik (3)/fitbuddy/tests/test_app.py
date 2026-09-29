import pytest
from fastapi.testclient import TestClient

from app import config, database, routes
from app.main import app


@pytest.fixture()
def client(tmp_path, monkeypatch):
    """Fresh temp database and no Gemini key, so tests never hit the network."""
    monkeypatch.setattr(database, "DATABASE_PATH", tmp_path / "test.db")
    monkeypatch.setattr(config, "GEMINI_API_KEY", None)
    monkeypatch.setattr(config, "ADMIN_TOKEN", "secret-token")
    with TestClient(app) as test_client:  # runs lifespan -> init_db()
        yield test_client


PROFILE = {"name": "Asha", "age": 28, "height_cm": 165, "weight_kg": 60, "goal": "Build strength"}


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_index_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "FitBuddy" in response.text


def test_profile_validation(client):
    response = client.post("/profiles", json={"name": "", "age": 12})
    assert response.status_code == 422


def test_create_and_read_profile(client):
    created = client.post("/profiles", json=PROFILE)
    assert created.status_code == 201
    profile_id = created.json()["id"]
    fetched = client.get(f"/profiles/{profile_id}")
    assert fetched.status_code == 200
    assert fetched.json()["name"] == "Asha"
    assert client.get("/profiles/9999").status_code == 404


def test_ai_plan_falls_back_without_key(client):
    profile_id = client.post("/profiles", json=PROFILE).json()["id"]
    response = client.post(f"/profiles/{profile_id}/ai-plan")
    assert response.status_code == 200
    body = response.json()
    assert body["source"] == "local-fallback"
    assert "Monday" in body["plan"]


def test_rule_based_workout_plan(client):
    profile_id = client.post("/profiles", json=PROFILE).json()["id"]
    response = client.post(f"/profiles/{profile_id}/workout-plan")
    assert response.status_code == 200
    assert len(response.json()["exercises"]) == 4


def test_nutrition_fallback(client):
    profile_id = client.post("/profiles", json=PROFILE).json()["id"]
    body = client.get(f"/profiles/{profile_id}/nutrition").json()
    assert len(body["daily_habits"]) == 3
    assert set(body["meal_ideas"]) == {"breakfast", "lunch", "snack", "dinner"}


def test_feedback_and_admin(client):
    profile_id = client.post("/profiles", json=PROFILE).json()["id"]
    response = client.post(
        "/feedback", json={"profile_id": profile_id, "rating": 4, "message": "Nice plan"}
    )
    assert response.status_code == 201
    assert response.json()["updated_plan"] is None

    assert client.get("/admin/users").status_code == 401
    assert client.get("/admin/users", headers={"X-Admin-Token": "wrong"}).status_code == 401
    ok = client.get("/admin/users", headers={"X-Admin-Token": "secret-token"})
    assert ok.status_code == 200
    users = ok.json()["users"]
    assert users[0]["feedback"][0]["message"] == "Nice plan"


def test_feedback_rating_validation(client):
    response = client.post("/feedback", json={"rating": 9, "message": "x"})
    assert response.status_code == 422


def test_feedback_updates_plan_with_ai(client, monkeypatch):
    monkeypatch.setattr(config, "GEMINI_API_KEY", "fake")
    monkeypatch.setattr(routes, "update_workout_plan", lambda *a, **k: "UPDATED PLAN")
    profile_id = client.post("/profiles", json=PROFILE).json()["id"]
    database.save_fitness_plan(profile_id, "Asha", "OLD PLAN")
    body = client.post(
        "/feedback", json={"profile_id": profile_id, "rating": 2, "message": "Too hard"}
    ).json()
    assert body["updated_plan"] == "UPDATED PLAN"
    assert database.get_latest_fitness_plan(profile_id) == "UPDATED PLAN"


def test_nutrition_json_parsing():
    from app.gemini_flash_generator import _extract_json

    parsed = _extract_json('```json\n{"guidance": "x"}\n```')
    assert parsed == {"guidance": "x"}
