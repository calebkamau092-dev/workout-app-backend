"""Endpoint status codes and responses."""


# ---------- Workouts ----------

def test_list_workouts(client, sample_data):
    response = client.get("/workouts")
    assert response.status_code == 200
    assert len(response.get_json()) == 1


def test_get_workout_includes_exercises_with_reps(client, sample_data):
    response = client.get(f"/workouts/{sample_data['workout_id']}")
    data = response.get_json()
    assert response.status_code == 200
    entry = data["workout_exercises"][0]
    assert entry["reps"] == 10
    assert entry["exercise"]["name"] == "Squat"


def test_get_missing_workout_returns_404(client):
    assert client.get("/workouts/999").status_code == 404


def test_create_workout(client):
    response = client.post("/workouts", json={"date": "2026-10-19", "duration_minutes": 50})
    assert response.status_code == 201
    assert response.get_json()["date"] == "2026-10-19"


def test_create_workout_with_invalid_data_returns_400(client):
    response = client.post("/workouts", json={"date": "2026-10-19", "duration_minutes": -1})
    assert response.status_code == 400
    assert "duration_minutes" in response.get_json()["errors"]


def test_delete_workout(client, sample_data):
    response = client.delete(f"/workouts/{sample_data['workout_id']}")
    assert response.status_code == 204
    assert client.get(f"/workouts/{sample_data['workout_id']}").status_code == 404


# ---------- Exercises ----------

def test_list_exercises(client, sample_data):
    response = client.get("/exercises")
    assert response.status_code == 200
    assert response.get_json()[0]["name"] == "Squat"


def test_get_exercise_includes_workouts(client, sample_data):
    response = client.get(f"/exercises/{sample_data['exercise_id']}")
    assert response.status_code == 200
    assert response.get_json()["workouts"][0]["notes"] == "Leg day"


def test_create_exercise(client):
    response = client.post("/exercises", json={"name": "Lunge", "category": "strength"})
    assert response.status_code == 201
    assert response.get_json()["equipment_needed"] is False


def test_create_duplicate_exercise_returns_409(client, sample_data):
    response = client.post("/exercises", json={"name": "Squat", "category": "strength"})
    assert response.status_code == 409


def test_delete_exercise(client, sample_data):
    assert client.delete(f"/exercises/{sample_data['exercise_id']}").status_code == 204
    assert client.get("/exercises").get_json() == []


# ---------- Adding an exercise to a workout ----------

def test_add_exercise_to_workout(client, sample_data):
    exercise = client.post("/exercises", json={"name": "Plank", "category": "balance"}).get_json()
    url = f"/workouts/{sample_data['workout_id']}/exercises/{exercise['id']}/workout_exercises"
    response = client.post(url, json={"duration_seconds": 60})
    assert response.status_code == 201
    assert response.get_json()["exercise"]["name"] == "Plank"
    workout = client.get(f"/workouts/{sample_data['workout_id']}").get_json()
    assert len(workout["workout_exercises"]) == 2


def test_add_exercise_requires_reps_or_duration(client, sample_data):
    url = f"/workouts/{sample_data['workout_id']}/exercises/{sample_data['exercise_id']}/workout_exercises"
    assert client.post(url, json={}).status_code == 400


def test_add_exercise_to_missing_workout_returns_404(client, sample_data):
    url = f"/workouts/999/exercises/{sample_data['exercise_id']}/workout_exercises"
    assert client.post(url, json={"reps": 5, "sets": 2}).status_code == 404