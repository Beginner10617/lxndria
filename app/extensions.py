from flask_wtf.csrf import CSRFProtect, CSRFError
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_bcrypt import Bcrypt
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import base64, os
load_dotenv()
csrf = CSRFProtect()
login_manager = LoginManager()
limiter = Limiter(get_remote_address)
db = SQLAlchemy()
mail = Mail()
bcrypt = Bcrypt()

def is_number(s):
    try:
        float(s)  # Convert to float; works for int and float values
        return True
    except ValueError:
        return False
    
cipher = Fernet(os.getenv('FERNET_KEY').encode())

def encrypt_answer(answer):
    return cipher.encrypt(answer.encode()).decode()
def decrypt_answer(encrypted_answer):
    return cipher.decrypt(encrypted_answer.encode()).decode()
