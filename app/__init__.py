from pathlib import Path

from flask import Flask

from config import Config
from app.extensions import db, login_manager


def create_app(config_class=Config):
    """
    Create and configure the Flask application.
    """

    app = Flask(
        __name__,
        instance_relative_config=True,
    )

    app.config.from_object(config_class)

    Path(app.instance_path).mkdir(
        parents=True,
        exist_ok=True,
    )

    db.init_app(app)
    login_manager.init_app(app)

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return db.session.get(
                User,
                int(user_id),
            )

        except (TypeError, ValueError):
            return None

    from app.routes.analyzer_routes import analyzer_bp
    from app.routes.auth_routes import auth_bp
    from app.routes.history_routes import history_bp
    from app.routes.main_routes import main_bp
    from app.routes.password_routes import password_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(analyzer_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(password_bp)

    from app.errors import register_error_handlers

    register_error_handlers(app)

    return app