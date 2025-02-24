from .auth import current_user
from app.models import Profile, User, Problem, Discussion, Bookmarks
from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required
from app.forms import EditAccountForm
from werkzeug.utils import secure_filename
from app import db
from dotenv import load_dotenv
import os
from app.extensions import send_email
account_bp = Blueprint('account', __name__)

load_dotenv()
@account_bp.route('/account')
def account():
    if not current_user.is_authenticated:
       #('Not authenticated')
        return redirect(url_for('routes.auth.login'))
    if request.args.get('updateEmail'):
        return redirect(url_for('routes.auth.update_email'))
    if request.args.get('delete')=='1':
        user = User.query.filter_by(username=current_user.username).first()
        email_body = f"Your account has been deleted successfully. If you didn't request this, please contact us immediately."
        send_email(user.email, "Account Deleted", email_body)
        user.__delete__()
        return redirect(url_for('routes.auth.logout'))
    profile = Profile.query.filter_by(username=current_user.username).first()
    problems = Problem.query.filter_by(author=current_user.username).order_by(Problem.created_at.desc()).all()
    discussions = Discussion.query.filter_by(author=current_user.username).order_by(Discussion.created_at.desc()).all()
    bookmarks = Bookmarks.query.filter_by(username=current_user.username).order_by(Bookmarks.created_at.desc()).all()
    return render_template('account.html', user=profile, problems=problems, stats=profile, discussions=discussions, bookmarks=bookmarks)

@account_bp.route('/account/edit', methods=['GET', 'POST'])
@login_required
def edit_account():
    form = EditAccountForm()
    current_profile = Profile.query.filter_by(username=current_user.username).first()
    user = User.query.filter_by(username=current_user.username).first()
    if form.validate_on_submit():
        if form.name.data:
            user.name = form.name.data
        if form.bio.data:
            current_profile.bio = form.bio.data
       #(form.profile_pic.data)
        if form.profile_pic.data:
           #(form.profile_pic.data)
            file = form.profile_pic.data
            filename = secure_filename(file.filename)
            directory = current_profile.username
            path = os.getenv('UPLOAD_FOLDER')+current_profile.username+"/Profile_picture/"  # This should be the path where you want to save
           #(path)
            try:
                file.save(os.path.join(path, filename))
            except FileNotFoundError:
                os.makedirs(path)
                file.save(os.path.join(path, filename))
            current_profile.profile_pic = path[len('app/static/'):]+filename
        db.session.commit()
        
        return redirect(url_for('routes.account.account'))
    return render_template('edit_account.html', form=form, user = current_profile)

@account_bp.route('/account/<string:username>')
def view_account(username):
    if not current_user.is_authenticated:
       #('Not authenticated')
        return redirect(url_for('routes.auth.login'))
    if not Profile.query.filter_by(username=username).first():
        return redirect(url_for('routes.account.account'))
    if username == current_user.username:
        return redirect(url_for('routes.account.account'))
    profile = Profile.query.filter_by(username=username).first()
    problems = Problem.query.filter_by(author=username).order_by(Problem.created_at.desc()).all()
    discussions = Discussion.query.filter_by(author=username).order_by(Discussion.created_at.desc()).all()
    return render_template('account.html', user=profile, problems=problems, stats=profile, discussions=discussions)