from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app.forms import EditAccountForm
from werkzeug.utils import secure_filename
from app import db
from dotenv import load_dotenv
from app.models import Profile, Moderators, Report

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin-controls')
def admin():
    if not current_user.is_authenticated:
        return redirect(url_for('routes.auth.login'))
    if current_user.username != 'admin':
        return redirect(url_for('routes.account.account'))
    
    users = Profile.query.order_by(Profile.created_at.desc()).all()
    
    if request.args.get('mods') == '1':
        Users=[]
        for user in users:
            if user.is_moderator:
                Users.append(user)
        users = Users
    
    if request.args.get('promote') == '1':
        user = request.args.get('user')
        print('promoting', user)
        user_profile = Profile.query.filter_by(username=user).first()
        if user_profile is None:
            return redirect(url_for('routes.admin.admin'))
        if user_profile.is_moderator:
            return redirect(url_for('routes.admin.admin'))
        mod = Moderators(username=user)
        db.session.add(mod)
        db.session.commit()
        return redirect(url_for('routes.admin.admin'))
    if request.args.get('demote') == '1':
        user = request.args.get('user')
        print(user, type(user))
        mod = Moderators.query.filter_by(username=user).first()
        if mod is None:
            return redirect(url_for('routes.admin.admin'))
        db.session.delete(mod)
        db.session.commit()
        return redirect(url_for('routes.admin.admin'))

    return render_template('admin.html', users=users)

@admin_bp.route('/admin-controls/view')
def view_user():
    if not current_user.is_authenticated:
        return redirect(url_for('routes.auth.login'))
    if current_user.username != 'admin':
        return redirect(url_for('routes.account.account'))
    username = request.args.get('user')
    user = Profile.query.filter_by(username=username).first()
    if user is None:
        flash('User not found', 'danger')
        return redirect(url_for('routes.admin.admin'))
    reports = Report.query.filter_by(handled_by=username).order_by(Report.created_at.desc()).all()
    return render_template('mod_profile.html', user=user, reports=reports)