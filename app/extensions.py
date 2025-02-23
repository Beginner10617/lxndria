from flask_wtf.csrf import CSRFProtect, CSRFError
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_bcrypt import Bcrypt
from flask import url_for 
from flask_migrate import Migrate
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import base64, os, jwt
from datetime import datetime
from dateutil.relativedelta import relativedelta

load_dotenv()

WEBAPP_NAME = os.getenv('WEBAPP_NAME')
csrf = CSRFProtect()
login_manager = LoginManager()
# Get Redis URL from environment variables (set it later in Render)
REDIS_URL = os.getenv("REDIS_URL")

# Set up Flask-Limiter with Redis
if REDIS_URL:
    limiter = Limiter(
        get_remote_address,
        storage_uri=REDIS_URL
    )
else:
    limiter = Limiter(
        get_remote_address
    )
db = SQLAlchemy()
mail = Mail()
bcrypt = Bcrypt()
migrate = Migrate()

def is_number(s):
    try:
        float(s)
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
    msg = Message('Email Verification', sender=os.getenv('EMAIL_ID'), recipients=[user.email])
    msg.body = 'Hi '+user.name+'! To verify your email for '+WEBAPP_NAME+', visit the following link:\n' + verify_url + '\nPlease note that these links will expire in 24 hours.'
    msg.body = msg.body + '\n\nIf you did not create an account on '+WEBAPP_NAME+', please ignore this email, or check if someone else has used your email address to create an account.'
    mail.send(msg)

def send_email(email, subject, body, cc=[]):
    msg = Message(subject, sender=os.getenv('EMAIL_ID'), recipients=[email], cc=cc)
    msg.body = body
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

def time_ago(dt):
    now = datetime.utcnow()
    diff = relativedelta(now, dt)

    if diff.years > 0:
        return f"{diff.years} year{'s' if diff.years > 1 else ''} ago"
    elif diff.months > 0:
        return f"{diff.months} month{'s' if diff.months > 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.hours > 0:
        return f"{diff.hours} hour{'s' if diff.hours > 1 else ''} ago"
    elif diff.minutes > 0:
        return f"{diff.minutes} minute{'s' if diff.minutes > 1 else ''} ago"
    else:
        return "Just now"
    
