# Workout Tracker API

A Flask REST API for a workout tracking application used by personal trainers. Trainers can create **workouts** and reusable **exercises**, then add exercises to workouts with the reps, sets or duration for that session.

Built with **Flask**, **Flask-SQLAlchemy**, **Flask-Migrate** and **Marshmallow**.

## Features

- Create, view and delete workouts and exercises
- Add an exercise to a workout with reps/sets or a duration
- Workout detail shows each exercise with its reps, sets and duration
- Deleting a workout or exercise also deletes its workout-exercise links
- Three layers of validation: database constraints, model validations and schema validations
- 31 pytest tests covering models, schemas and every endpoint

## Data Model

```
Workout ──< WorkoutExercise >── Exercise
            (reps, sets, duration_seconds)
```

| Model | Fields |
|-------|--------|
| **Exercise** | `id`, `name`, `category`, `equipment_needed` |
| **Workout** | `id`, `date`, `duration_minutes`, `notes` |
| **WorkoutExercise** (join table) | `id`, `workout_id`, `exercise_id`, `reps`, `sets`, `duration_seconds` |

- A workout has many exercises through WorkoutExercises.
- An exercise has many workouts through WorkoutExercises, so the same exercise can be reused across workouts.

## Validations

| Layer | Rules |
|-------|-------|
| **Table constraints** | `exercises.name` is NOT NULL and UNIQUE; `category`, `date` and `duration_minutes` are NOT NULL; CHECK constraints keep `duration_minutes`, `reps`, `sets` and `duration_seconds` above 0 |
| **Model validations** (`@validates`) | Exercise name cannot be blank; category must be one of `strength`, `cardio`, `flexibility`, `balance`; workout duration must be 1–600 minutes; notes are at most 500 characters; reps/sets/duration must be positive whole numbers |
| **Schema validations** (Marshmallow) | Required fields; `Length` on name and notes; `OneOf` on category; `Range` on durations, reps and sets; valid `YYYY-MM-DD` dates; a workout exercise must include **reps and sets**, or **duration_seconds** |

## Project Structure

```
workout-app-backend/
├── Pipfile / Pipfile.lock
├── pytest.ini
├── server/
│   ├── app.py              # App factory, blueprint registration, JSON error handlers
│   ├── models.py           # Models, relationships, table constraints, model validations
│   ├── schemas.py          # Marshmallow schemas and schema validations
│   ├── seed.py             # Resets the database with example data
│   ├── routes/
│   │   ├── workouts.py     # Workout endpoints + add exercise to workout
│   │   └── exercises.py    # Exercise endpoints
│   └── migrations/         # Flask-Migrate (Alembic) migrations
└── tests/                  # pytest suite
```

## Installation

Requires Python 3.12 and [Pipenv](https://pipenv.pypa.io/).

```bash
git clone https://github.com/calebkamau092-dev/workout-app-backend.git
cd workout-app-backend

pipenv install --dev
pipenv shell
```

Create the database and load example data:

```bash
cd server
flask db upgrade head
python seed.py
```

`seed.py` clears all tables before inserting, so you can rerun it any time to reset the data.

## Running the App

From the `server/` directory:

```bash
python app.py
```

The API runs at `http://127.0.0.1:5555`.

## Running the Tests

From the project root:

```bash
pytest -v
```

The tests use an in-memory database, so they don't touch your real data.

## API Endpoints

### Workouts

| Method | Endpoint | Description | Success |
|--------|----------|-------------|---------|
| GET | `/workouts` | List all workouts | 200 |
| GET | `/workouts/<id>` | Show one workout with its exercises, including reps/sets/duration | 200 |
| POST | `/workouts` | Create a workout | 201 |
| DELETE | `/workouts/<id>` | Delete a workout and its workout-exercise links | 204 |

### Exercises

| Method | Endpoint | Description | Success |
|--------|----------|-------------|---------|
| GET | `/exercises` | List all exercises | 200 |
| GET | `/exercises/<id>` | Show one exercise with the workouts it appears in | 200 |
| POST | `/exercises` | Create an exercise | 201 |
| DELETE | `/exercises/<id>` | Delete an exercise and its workout-exercise links | 204 |

### Workout Exercises

| Method | Endpoint | Description | Success |
|--------|----------|-------------|---------|
| POST | `/workouts/<workout_id>/exercises/<exercise_id>/workout_exercises` | Add an exercise to a workout with reps/sets or a duration | 201 |

### Error responses

| Status | When |
|--------|------|
| 400 | Invalid input (schema or model validation failed) |
| 404 | Workout or exercise not found |
| 409 | Database constraint failed, e.g. duplicate exercise name |

Errors are returned as JSON, for example:

```json
{"errors": {"category": ["Must be one of: strength, cardio, flexibility, balance."]}}
```

### Example requests

**Create an exercise**

```bash
curl -X POST http://127.0.0.1:5555/exercises \
  -H "Content-Type: application/json" \
  -d '{"name": "Lunge", "category": "strength", "equipment_needed": false}'
```

**Create a workout**

```bash
curl -X POST http://127.0.0.1:5555/workouts \
  -H "Content-Type: application/json" \
  -d '{"date": "2026-10-19", "duration_minutes": 40, "notes": "Morning session"}'
```

**Add an exercise to a workout**

```bash
curl -X POST http://127.0.0.1:5555/workouts/1/exercises/2/workout_exercises \
  -H "Content-Type: application/json" \
  -d '{"reps": 12, "sets": 3}'
```

**Response from `GET /workouts/1`**

```json
{
  "id": 1,
  "date": "2026-10-01",
  "duration_minutes": 60,
  "notes": "Leg day, felt strong.",
  "workout_exercises": [
    {
      "id": 1,
      "workout_id": 1,
      "exercise_id": 1,
      "reps": 10,
      "sets": 4,
      "duration_seconds": null,
      "exercise": {"id": 1, "name": "Squat", "category": "strength", "equipment_needed": false}
    }
  ]
}
```