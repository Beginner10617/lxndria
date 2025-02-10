from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.forms import EditAccountForm
from werkzeug.utils import secure_filename
from app import db
from dotenv import load_dotenv

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin-controls')
def admin():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    if current_user.username != 'admin':
        return redirect(url_for('account.account'))
    return render_template('admin.html')