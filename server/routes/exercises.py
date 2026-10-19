from flask import Blueprint, request

from models import Exercise, db
from schemas import exercise_detail_schema, exercise_schema, exercises_schema

exercises_bp = Blueprint("exercises", __name__)


@exercises_bp.get("/exercises")
def list_exercises():
    return exercises_schema.dump(Exercise.query.order_by(Exercise.name).all()), 200


@exercises_bp.get("/exercises/<int:id>")
def get_exercise(id):
    exercise = db.get_or_404(Exercise, id)
    return exercise_detail_schema.dump(exercise), 200


@exercises_bp.post("/exercises")
def create_exercise():
    data = exercise_schema.load(request.get_json() or {})
    exercise = Exercise(**data)
    db.session.add(exercise)
    db.session.commit()
    return exercise_schema.dump(exercise), 201


@exercises_bp.delete("/exercises/<int:id>")
def delete_exercise(id):
    exercise = db.get_or_404(Exercise, id)
    db.session.delete(exercise)
    db.session.commit()
    return "", 204