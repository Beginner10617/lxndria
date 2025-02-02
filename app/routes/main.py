from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models import User, Problem
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    all_problems = Problem.query.all()
    print(all_problems)
    return render_template('index.html', problems=all_problems)

@main_bp.route('/admin')
@login_required
def admin():
    if not current_user.is_authenticated:
        print('Not authenticated')
        return redirect(url_for('routes.auth.login'))
    
    if current_user.username == 'admin':
        return render_template('admin.html', total_users=User.query.count(), admin=True)
    return render_template('admin.html')