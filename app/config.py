from dotenv import load_dotenv
import os
class Config:
    load_dotenv()
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,  # Automatically reconnect if NeonDB sleeps
        "pool_size": 5,         # Maintain 5 persistent connections
        "max_overflow": 10,     # Allow up to 10 extra connections
        "pool_timeout": 30,     # Wait 30s for connection before erroring
        "pool_recycle": 1800,   # Refresh connection every 30 minutes
    }
    
    MAIL_SERVER = os.getenv('EMAIL_SERVER')
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('EMAIL_ID')
    MAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
    
    SECRET_KEY = os.getenv('SECRET_KEY')
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 # 16 MB
    PREFERRED_URL_SCHEME = os.getenv('PREFERRED_URL_SCHEME', 'https') 
    