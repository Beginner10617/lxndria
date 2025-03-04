import jwt
from dotenv import load_dotenv
from flask import url_for, flash, redirect, Blueprint, render_template
from app import mail, db, limiter, login_manager
from app.models import User
from app.forms import RegistrationForm, LoginForm, ResetPasswordForm, RequestResetForm, UpdateEmailForm
from flask_login import current_user, login_user, logout_user, login_required
from app.extensions import send_verification_email, send_reset_password_email, make_directory_for_user, send_email

auth_bp = Blueprint('auth', __name__)
pending_users = {}
load_dotenv()

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
            db.session.add(user)
           #('User added', user.username)
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
        username = form.username.data.strip()
        name = form.name.data.strip()
        password = form.password.data.strip()
        email = form.email.data
        confirm_password = form.confirm_password.data.strip()

        # Check if password is valid
        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'error')
            return redirect(url_for('routes.auth.register'))
        
        # Check if username is valid
        if username.startswith('_'):
            flash('Username cannot start with an underscore.', 'error')
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
#@limiter.limit("5 per minute")
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        password = form.password.data.strip()
        user = User.query.filter_by(username=username).first()
        if user and user.verify_password(password):
           #('Login successful')
            login_user(user)
            if username == 'admin':
                return redirect(url_for('routes.admin.admin'))
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
@limiter.limit("5 per minute")
def reset_password_request_2():
    if not current_user.is_authenticated:
        return redirect(url_for('routes.auth.login'))
    else:
        send_reset_password_email(current_user)
        flash('Password reset link sent to your email.', 'success')
    
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
               #('Password reset successfully')
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
def logout():
    if not current_user.is_authenticated:
        return redirect(url_for('routes.auth.login'))
    logout_user()
    return redirect(url_for('routes.auth.login'))

@auth_bp.route('/updateEmail', methods=['GET', 'POST'])
def update_email():
    update_email_form = UpdateEmailForm()
    if update_email_form.validate_on_submit():
        email = update_email_form.email.data
        password = update_email_form.password.data
        user = User.query.filter_by(username=current_user.username).first()
        if user and user.verify_password(password):
            existing_email = User.query.filter_by(email=email).first()
            if existing_email:
                flash('Email already in use. Please choose another.', 'error')
                return redirect(url_for('routes.auth.update_email'))
            previous_email = user.email
            user.email = email
            db.session.commit()
            flash('Email updated successfully.', 'success')
            message = f'Your email has been updated to {email}.'
            send_email('Email Updated', message, previous_email)
            return redirect(url_for('routes.account.account'))
        flash('Invalid password', 'error')
    return render_template('update_email.html', form=update_email_form)