from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, render_template
from flask_cors import CORS

from .config import settings
from .database import SessionLocal, init_db
from .routes.departments import departments_bp
from .routes.employees import employees_bp
from .routes.payroll import payroll_bp


def create_app() -> Flask:
    """Application factory for the payroll management system."""
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")

    app = Flask(
        __name__, template_folder="templates", static_folder="static"
    )
    app.config["SECRET_KEY"] = settings.secret_key
    app.config["JSON_SORT_KEYS"] = False

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Blueprints
    app.register_blueprint(departments_bp)
    app.register_blueprint(employees_bp)
    app.register_blueprint(payroll_bp)

    @app.route("/", methods=["GET"])
    def dashboard():
        return render_template("dashboard.html")

    with app.app_context():
        init_db()

    @app.teardown_appcontext
    def remove_session(_):
        SessionLocal.remove()

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(debug=settings.flask_env == "development", port=5000)

