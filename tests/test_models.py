"""Model validations (@validates) and table constraints."""

from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError

from models import Exercise, Workout, WorkoutExercise, db


# ---------- Model validations ----------

def test_exercise_name_cannot_be_blank(app):
    with pytest.raises(ValueError):
        Exercise(name="   ", category="strength")


def test_exercise_category_must_be_allowed(app):
    with pytest.raises(ValueError):
        Exercise(name="Juggling", category="circus")


def test_exercise_category_is_normalised(app):
    assert Exercise(name="Row", category=" Cardio ").category == "cardio"


def test_workout_duration_must_be_in_range(app):
    with pytest.raises(ValueError):
        Workout(date=date(2026, 1, 1), duration_minutes=0)
    with pytest.raises(ValueError):
        Workout(date=date(2026, 1, 1), duration_minutes=601)


def test_workout_notes_length_limit(app):
    with pytest.raises(ValueError):
        Workout(date=date(2026, 1, 1), duration_minutes=30, notes="x" * 501)


def test_workout_exercise_reps_must_be_positive(app):
    with pytest.raises(ValueError):
        WorkoutExercise(reps=-5)


# ---------- Table constraints ----------

def test_exercise_name_must_be_unique(app):
    db.session.add(Exercise(name="Squat", category="strength"))
    db.session.commit()
    db.session.add(Exercise(name="Squat", category="strength"))
    with pytest.raises(IntegrityError):
        db.session.commit()


def test_workout_date_cannot_be_null(app):
    db.session.add(Workout(duration_minutes=30))
    with pytest.raises(IntegrityError):
        db.session.commit()


def test_check_constraint_blocks_bad_duration(app):
    """Raw SQL skips @validates, so the CHECK constraint is the last line of defence."""
    with pytest.raises(IntegrityError):
        db.session.execute(
            db.text("INSERT INTO workouts (date, duration_minutes) VALUES ('2026-01-01', -10)")
        )


# ---------- Relationships ----------

def test_relationships(app, sample_data):
    workout = db.session.get(Workout, sample_data["workout_id"])
    exercise = db.session.get(Exercise, sample_data["exercise_id"])
    assert workout.exercises == [exercise]
    assert exercise.workouts == [workout]
    assert workout.workout_exercises[0].reps == 10


def test_deleting_workout_deletes_its_workout_exercises(app, sample_data):
    db.session.delete(db.session.get(Workout, sample_data["workout_id"]))
    db.session.commit()
    assert WorkoutExercise.query.count() == 0
    assert Exercise.query.count() == 1