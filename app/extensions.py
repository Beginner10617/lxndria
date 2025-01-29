from flask_wtf.csrf import CSRFProtect, CSRFError
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_bcrypt import Bcrypt

csrf = CSRFProtect()
login_manager = LoginManager()
limiter = Limiter(get_remote_address)
db = SQLAlchemy()
mail = Mail()
bcrypt = Bcrypt()