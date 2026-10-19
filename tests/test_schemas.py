"""Marshmallow schema validations."""

import pytest
from marshmallow import ValidationError

from schemas import exercise_schema, workout_exercise_schema, workout_schema


def test_exercise_schema_requires_name_and_category():
    with pytest.raises(ValidationError) as err:
        exercise_schema.load({})
    assert "name" in err.value.messages
    assert "category" in err.value.messages


def test_exercise_schema_rejects_unknown_category():
    with pytest.raises(ValidationError) as err:
        exercise_schema.load({"name": "Juggling", "category": "circus"})
    assert "category" in err.value.messages


def test_workout_schema_parses_date():
    data = workout_schema.load({"date": "2026-10-19", "duration_minutes": 40})
    assert data["date"].year == 2026


def test_workout_schema_rejects_bad_date_and_duration():
    with pytest.raises(ValidationError) as err:
        workout_schema.load({"date": "yesterday", "duration_minutes": 0})
    assert set(err.value.messages) == {"date", "duration_minutes"}


def test_workout_exercise_needs_reps_and_sets_or_duration():
    with pytest.raises(ValidationError):
        workout_exercise_schema.load({"reps": 10})
    assert workout_exercise_schema.load({"reps": 10, "sets": 3})
    assert workout_exercise_schema.load({"duration_seconds": 60})


def test_workout_exercise_rejects_non_positive_values():
    with pytest.raises(ValidationError):
        workout_exercise_schema.load({"duration_seconds": 0})