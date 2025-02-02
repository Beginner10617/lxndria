import jwt, os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from flask_mail import Message
from flask import url_for, flash, redirect, Blueprint, request, render_template
from app import mail, db, limiter, login_manager
from app.models import User, UserStats
from app.forms import RegistrationForm, LoginForm, ResetPasswordForm, RequestResetForm
from flask_login import current_user, login_user, logout_user, login_required

auth_bp = Blueprint('auth', __name__)
WEBAPP_NAME = os.getenv('WEBAPP_NAME')
pending_users = {}
load_dotenv()

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

@auth_bp.route('/verify_email/<token>')
def verify_email(token):
    try:
        # Decode the token to get the email
        data = jwt.decode(token, 'secret_key', algorithms=['HS256'])
        email = data['email']
        
        # Mark the user's email as verified
        if email in pending_users:
            user = pending_users.pop(email)
            flash('Your email has been verified!', 'success')
            directory = user.username
            make_directory_for_user(directory)
            db.session.add(UserStats(username=user.username))
            db.session.add(user)
            print('User added', user.username)
            db.session.commit()
            return redirect(url_for('routes.auth.login'))
    except jwt.ExpiredSignatureError:
        flash('The verification link has expired', 'error')
    except jwt.InvalidTokenError:
        flash('Invalid verification link', 'error')
    return redirect(url_for('routes.auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        name = form.name.data
        password = form.password.data
        email = form.email.data
        confirm_password = form.confirm_password.data

        # Check if password is valid
        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'error')
            return redirect(url_for('routes.auth.register'))
        
        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('routes.auth.register'))

        # Check if username or email already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose another.', 'error')
            return redirect(url_for('routes.auth.register'))
        
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('Email already in use. Please choose another.', 'error')
            return redirect(url_for('routes.auth.register'))

        # Create new user
        user = User(username=username, name=name, email=email)
        user.set_password(password)
        pending_users[email]=user
        flash('Account created successfully. Please check your email to verify your account.', 'success')
        send_verification_email(user)
        return redirect(url_for('routes.auth.login'))
    elif current_user.is_authenticated:
        return redirect(url_for('routes.main.index'))
    return render_template('register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        if user and user.verify_password(password):
            print('Login successful')
            login_user(user)
            return redirect(url_for('routes.main.index'))
        flash('Invalid username or password', 'error')
    elif current_user.is_authenticated:
        return redirect(url_for('routes.main.index'))
    return render_template('login.html', form=form)

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    return redirect(url_for('routes.auth.reset_password_request'))

@auth_bp.route('/reset-password', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def reset_password_request():
    form = RequestResetForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        if user:
            send_reset_password_email(user)
            flash('Password reset link sent to your email.', 'success')
        else:
            flash('No account found with that email.', 'error')
    return render_template('reset_password_request.html', form=form)

@auth_bp.route('/reset-password-2', methods=['GET', 'POST'])
@login_required
@limiter.limit("5 per minute")
def reset_password_request_2():
    if current_user.is_authenticated:
        send_reset_password_email(current_user)
        flash('Password reset link sent to your email.', 'success')
    return redirect(url_for('routes.account.account'))

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        data = jwt.decode(token, 'secret_key', algorithms=['HS256'])
        email = data['email']
        user = User.query.filter_by(email=email).first()
        if user:
            form = ResetPasswordForm()
            if form.validate_on_submit():
                password = form.password.data
                confirm_password = form.confirm_password.data
        
                # Check if password is valid
                if len(password) < 8:
                    flash('Password must be at least 8 characters long.', 'error')
                    return redirect(url_for('routes.auth.register'))
                
                if password != confirm_password:
                    flash('Passwords do not match.', 'error')
                    return redirect(url_for('routes.auth.reset_password_token', token=token))
                user.set_password(password)
                db.session.commit()
                print('Password reset successfully')
                flash('Password reset successfully.', 'success')
                return redirect(url_for('routes.auth.login'))
            return render_template('reset_password.html', form=form, token=token)
        else:
            flash('Invalid reset link.', 'error')
            return redirect(url_for('routes.auth.login'))
    except jwt.ExpiredSignatureError:
        flash('The reset link has expired.', 'error')
    except jwt.InvalidTokenError:
        flash('Invalid reset link.', 'error')
        

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('routes.auth.login'))
'''
Actionables
1. HTML formatting of the email body.
'''