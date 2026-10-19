from flask import Flask, jsonify
from flask_migrate import Migrate
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from models import db
from routes.exercises import exercises_bp
from routes.workouts import workouts_bp


def create_app(database_uri="sqlite:///app.db"):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.json.sort_keys = False

    db.init_app(app)
    Migrate(app, db)

    app.register_blueprint(workouts_bp)
    app.register_blueprint(exercises_bp)

    # Shared error handlers so every route returns JSON errors the same way.
    @app.errorhandler(ValidationError)
    def handle_schema_error(error):
        return jsonify({"errors": error.messages}), 400

    @app.errorhandler(ValueError)
    def handle_model_error(error):
        db.session.rollback()
        return jsonify({"errors": [str(error)]}), 400

    @app.errorhandler(IntegrityError)
    def handle_integrity_error(error):
        db.session.rollback()
        return jsonify({"errors": ["Database constraint failed (e.g. duplicate name)."]}), 409

    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({"errors": ["Resource not found."]}), 404

    return app


app = create_app()

if __name__ == "__main__":
    app.run(port=5555, debug=True)