from .config import Config
from .extensions import csrf, login_manager, limiter, db, mail, migrate, time_ago
from .routes import routes_bp
from flask import Flask

def create_app():
    # Create the Flask app
    app = Flask(__name__)
    # Configure the app
    app.config.from_object(Config)

    # Register the time_ago filter
    app.jinja_env.filters['time_ago'] = time_ago

    # Initialize the extensions
    csrf.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    # Register the blueprints
    app.register_blueprint(routes_bp)
    return app