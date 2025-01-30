from .auth import current_user
from app.models import Profile, User
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required
from app.forms import EditAccountForm
from werkzeug.utils import secure_filename
from app import db
import os

account_bp = Blueprint('account', __name__)

@account_bp.route('/account')
def account():
    if not current_user.is_authenticated:
        print('Not authenticated')
        return redirect(url_for('routes.auth.login'))
    profile = Profile.query.filter_by(username=current_user.username).first()
    return render_template('account.html', user=profile)

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
        print(form.profile_pic.data)
        if form.profile_pic.data:
            print(form.profile_pic.data)
            file = form.profile_pic.data
            filename = secure_filename(file.filename)
            directory = current_profile.username
            path = "app/static/User-content/Wasi/"  # This should be the path where you want to save
            print(path)
            file.save(os.path.join(path, filename))
            current_profile.profile_pic = path[len('app/static/'):]+filename
        db.session.commit()
        
        return redirect(url_for('routes.account.account'))
    return render_template('edit_account.html', form=form, user = current_profile)
