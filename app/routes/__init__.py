from flask import Blueprint
from .auth import auth_bp
from .main import main_bp
from .account import account_bp
from .help import help_bp
from .contribute import contributions_bp
from .problem import problem_bp
from .discussion import discussion_bp
from .comments import comments_bp
from .admin import admin_bp
from .notification import notification_bp
routes_bp = Blueprint('routes', __name__)

# Register blueprints here
routes_bp.register_blueprint(auth_bp)
routes_bp.register_blueprint(main_bp)
routes_bp.register_blueprint(account_bp)
routes_bp.register_blueprint(help_bp)
routes_bp.register_blueprint(contributions_bp)
routes_bp.register_blueprint(problem_bp)
routes_bp.register_blueprint(discussion_bp) 
routes_bp.register_blueprint(comments_bp)
routes_bp.register_blueprint(admin_bp)
routes_bp.register_blueprint(notification_bp)