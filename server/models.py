from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import validates

db = SQLAlchemy()

EXERCISE_CATEGORIES = ("strength", "cardio", "flexibility", "balance")


class Exercise(db.Model):
    __tablename__ = "exercises"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    category = db.Column(db.String(50), nullable=False)
    equipment_needed = db.Column(db.Boolean, nullable=False, default=False)

    # Deleting an exercise also deletes its WorkoutExercise rows.
    workout_exercises = db.relationship(
        "WorkoutExercise", back_populates="exercise", cascade="all, delete-orphan"
    )
    workouts = association_proxy("workout_exercises", "workout")

    @validates("name")
    def validate_name(self, key, name):
        if not name or not name.strip():
            raise ValueError("Exercise name cannot be empty.")
        return name.strip()

    @validates("category")
    def validate_category(self, key, category):
        category = (category or "").strip().lower()
        if category not in EXERCISE_CATEGORIES:
            raise ValueError(f"Category must be one of: {', '.join(EXERCISE_CATEGORIES)}.")
        return category

    def __repr__(self):
        return f"<Exercise {self.id} {self.name}>"


class Workout(db.Model):
    __tablename__ = "workouts"
    __table_args__ = (
        CheckConstraint("duration_minutes > 0", name="ck_workout_duration_positive"),
    )

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)

    # Deleting a workout also deletes its WorkoutExercise rows.
    workout_exercises = db.relationship(
        "WorkoutExercise", back_populates="workout", cascade="all, delete-orphan"
    )
    exercises = association_proxy("workout_exercises", "exercise")

    @validates("duration_minutes")
    def validate_duration_minutes(self, key, minutes):
        if not isinstance(minutes, int) or isinstance(minutes, bool) or not 1 <= minutes <= 600:
            raise ValueError("Workout duration must be a whole number between 1 and 600 minutes.")
        return minutes

    @validates("notes")
    def validate_notes(self, key, notes):
        if notes is not None and len(notes) > 500:
            raise ValueError("Notes cannot be longer than 500 characters.")
        return notes

    def __repr__(self):
        return f"<Workout {self.id} {self.date}>"


class WorkoutExercise(db.Model):
    __tablename__ = "workout_exercises"
    __table_args__ = (
        CheckConstraint("reps IS NULL OR reps > 0", name="ck_we_reps_positive"),
        CheckConstraint("sets IS NULL OR sets > 0", name="ck_we_sets_positive"),
        CheckConstraint(
            "duration_seconds IS NULL OR duration_seconds > 0",
            name="ck_we_duration_positive",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey("workouts.id"), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercises.id"), nullable=False)
    reps = db.Column(db.Integer)
    sets = db.Column(db.Integer)
    duration_seconds = db.Column(db.Integer)

    workout = db.relationship("Workout", back_populates="workout_exercises")
    exercise = db.relationship("Exercise", back_populates="workout_exercises")

    @validates("reps", "sets", "duration_seconds")
    def validate_positive(self, key, value):
        if value is not None and (not isinstance(value, int) or isinstance(value, bool) or value < 1):
            raise ValueError(f"{key} must be a positive whole number.")
        return value

    def __repr__(self):
        return f"<WorkoutExercise workout={self.workout_id} exercise={self.exercise_id}>"