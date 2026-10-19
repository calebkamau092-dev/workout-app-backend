from marshmallow import Schema, ValidationError, fields, validate, validates_schema

from models import EXERCISE_CATEGORIES


class ExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    category = fields.Str(required=True, validate=validate.OneOf(EXERCISE_CATEGORIES))
    equipment_needed = fields.Bool(load_default=False)


class WorkoutSchema(Schema):
    id = fields.Int(dump_only=True)
    date = fields.Date(required=True)
    duration_minutes = fields.Int(required=True, strict=True, validate=validate.Range(min=1, max=600))
    notes = fields.Str(allow_none=True, validate=validate.Length(max=500))


class WorkoutExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    workout_id = fields.Int(dump_only=True)
    exercise_id = fields.Int(dump_only=True)
    reps = fields.Int(allow_none=True, strict=True, validate=validate.Range(min=1))
    sets = fields.Int(allow_none=True, strict=True, validate=validate.Range(min=1))
    duration_seconds = fields.Int(allow_none=True, strict=True, validate=validate.Range(min=1))
    exercise = fields.Nested(ExerciseSchema, dump_only=True)

    @validates_schema
    def validate_reps_or_duration(self, data, **kwargs):
        """An entry needs either reps and sets (e.g. squats) or a duration (e.g. plank)."""
        has_reps = data.get("reps") is not None and data.get("sets") is not None
        has_duration = data.get("duration_seconds") is not None
        if not has_reps and not has_duration:
            raise ValidationError("Provide reps and sets, or duration_seconds.")


class WorkoutDetailSchema(WorkoutSchema):
    """A workout with each exercise and its reps/sets/duration."""

    workout_exercises = fields.Nested(WorkoutExerciseSchema, many=True, dump_only=True)


class ExerciseDetailSchema(ExerciseSchema):
    """An exercise with the workouts it appears in."""

    workouts = fields.Nested(WorkoutSchema, many=True, dump_only=True)


exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True)
exercise_detail_schema = ExerciseDetailSchema()

workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)
workout_detail_schema = WorkoutDetailSchema()

workout_exercise_schema = WorkoutExerciseSchema()