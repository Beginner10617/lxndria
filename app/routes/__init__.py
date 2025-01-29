from flask import Blueprint
from .auth import auth_bp
from .main import main_bp

routes_bp = Blueprint('routes', __name__)

# Register blueprints here
routes_bp.register_blueprint(auth_bp)
routes_bp.register_blueprint(main_bp)