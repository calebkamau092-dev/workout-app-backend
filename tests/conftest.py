from datetime import date

import pytest

from app import create_app
from models import Exercise, Workout, WorkoutExercise, db


@pytest.fixture
def app():
    """A fresh app with an in-memory database for every test."""
    app = create_app("sqlite://")
    app.config["TESTING"] = True
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def sample_data(app):
    """One workout containing one exercise."""
    squat = Exercise(name="Squat", category="strength", equipment_needed=False)
    workout = Workout(date=date(2026, 10, 1), duration_minutes=45, notes="Leg day")
    db.session.add(WorkoutExercise(workout=workout, exercise=squat, reps=10, sets=3))
    db.session.commit()
    return {"workout_id": workout.id, "exercise_id": squat.id}