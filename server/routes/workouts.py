from flask import Blueprint, request

from models import Exercise, Workout, WorkoutExercise, db
from schemas import (
    workout_detail_schema,
    workout_exercise_schema,
    workout_schema,
    workouts_schema,
)

workouts_bp = Blueprint("workouts", __name__)


@workouts_bp.get("/workouts")
def list_workouts():
    return workouts_schema.dump(Workout.query.order_by(Workout.date).all()), 200


@workouts_bp.get("/workouts/<int:id>")
def get_workout(id):
    workout = db.get_or_404(Workout, id)
    return workout_detail_schema.dump(workout), 200


@workouts_bp.post("/workouts")
def create_workout():
    data = workout_schema.load(request.get_json() or {})
    workout = Workout(**data)
    db.session.add(workout)
    db.session.commit()
    return workout_schema.dump(workout), 201


@workouts_bp.delete("/workouts/<int:id>")
def delete_workout(id):
    workout = db.get_or_404(Workout, id)
    db.session.delete(workout)
    db.session.commit()
    return "", 204


@workouts_bp.post("/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises")
def add_exercise_to_workout(workout_id, exercise_id):
    workout = db.get_or_404(Workout, workout_id)
    exercise = db.get_or_404(Exercise, exercise_id)
    data = workout_exercise_schema.load(request.get_json() or {})
    workout_exercise = WorkoutExercise(workout=workout, exercise=exercise, **data)
    db.session.add(workout_exercise)
    db.session.commit()
    return workout_exercise_schema.dump(workout_exercise), 201