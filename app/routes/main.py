from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models import User
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if not current_user.is_authenticated:
        print('Not authenticated')
        return redirect(url_for('routes.auth.login'))
    print(current_user.username)
    if current_user.username == 'admin':
        return render_template('index.html', total_users=User.query.count(), admin=True)
    return redirect(url_for('routes.main.home'))

@main_bp.route('/home')
@login_required
def home():
    return render_template('home.html')