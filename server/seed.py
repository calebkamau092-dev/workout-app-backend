#!/usr/bin/env python3

from datetime import date

from app import app
from models import Exercise, Workout, WorkoutExercise, db

with app.app_context():
    print("Clearing old data...")
    WorkoutExercise.query.delete()
    Workout.query.delete()
    Exercise.query.delete()

    print("Creating exercises...")
    squat = Exercise(name="Squat", category="strength", equipment_needed=False)
    bench = Exercise(name="Bench Press", category="strength", equipment_needed=True)
    plank = Exercise(name="Plank", category="balance", equipment_needed=False)
    running = Exercise(name="Treadmill Run", category="cardio", equipment_needed=True)
    stretch = Exercise(name="Hamstring Stretch", category="flexibility", equipment_needed=False)
    db.session.add_all([squat, bench, plank, running, stretch])

    print("Creating workouts...")
    leg_day = Workout(date=date(2026, 10, 1), duration_minutes=60, notes="Leg day, felt strong.")
    upper_body = Workout(date=date(2026, 10, 3), duration_minutes=45, notes="Upper body and core.")
    cardio = Workout(date=date(2026, 10, 5), duration_minutes=30, notes=None)
    db.session.add_all([leg_day, upper_body, cardio])

    print("Adding exercises to workouts...")
    db.session.add_all([
        WorkoutExercise(workout=leg_day, exercise=squat, reps=10, sets=4),
        WorkoutExercise(workout=leg_day, exercise=stretch, duration_seconds=120),
        WorkoutExercise(workout=upper_body, exercise=bench, reps=8, sets=3),
        WorkoutExercise(workout=upper_body, exercise=plank, duration_seconds=60),
        WorkoutExercise(workout=cardio, exercise=running, duration_seconds=1500),
        WorkoutExercise(workout=cardio, exercise=stretch, duration_seconds=90),
    ])

    db.session.commit()
    print("Done seeding!")