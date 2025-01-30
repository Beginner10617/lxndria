from dotenv import load_dotenv
import os
class Config:
    load_dotenv()
    SQLALCHEMY_DATABASE_URI = 'sqlite:///default.db'
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('EMAIL_ID')
    MAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 # 16 MB
    