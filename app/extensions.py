from flask_wtf.csrf import CSRFProtect, CSRFError
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_bcrypt import Bcrypt
from flask import url_for 
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import base64, os, jwt

load_dotenv()

WEBAPP_NAME = os.getenv('WEBAPP_NAME')
csrf = CSRFProtect()
login_manager = LoginManager()
# Get Redis URL from environment variables (set it later in Render)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Set up Flask-Limiter with Redis
limiter = Limiter(
    get_remote_address,
    storage_uri=REDIS_URL
)
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

def send_verification_email(user):
    token_for_verification = jwt.encode({'email': user.email, 'exp': datetime.utcnow() + timedelta(hours=24)}, 'secret_key', algorithm='HS256')
    verify_url = url_for('routes.auth.verify_email', token=token_for_verification, _external=True)
    token_for_deletion = jwt.encode({'email': user.email, 'exp': datetime.utcnow() + timedelta(hours=24)}, 'secret_key', algorithm='HS256')
    msg = Message('Email Verification', sender=os.getenv('EMAIL_ID'), recipients=[user.email])
    msg.body = 'Hi '+user.name+'! To verify your email for '+WEBAPP_NAME+', visit the following link:\n' + verify_url + '\nPlease note that these links will expire in 24 hours.'
    mail.send(msg)

def send_reset_password_email(user):
    token_for_reset = jwt.encode({'email': user.email, 'exp': datetime.utcnow() + timedelta(hours=24)}, 'secret_key', algorithm='HS256')
    reset_url = url_for('routes.auth.reset_password', token=token_for_reset, _external=True)
    msg = Message('Password Reset', sender=os.getenv('EMAIL_ID'), recipients=[user.email])
    msg.body = 'Hi '+user.name+'! To reset your password for '+WEBAPP_NAME+', visit the following link:\n' + reset_url + '\nPlease note that these links will expire in 24 hours.'
    mail.send(msg)

def make_directory_for_user(directory):
    path = os.getenv('UPLOAD_FOLDER')+directory+"/"
    os.makedirs(path, exist_ok=True)
    os.makedirs(path+"Profile_picture/", exist_ok=True)
    os.makedirs(path+"Problems/", exist_ok=True)
    os.makedirs(path+"Discussions/", exist_ok=True)
