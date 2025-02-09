from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from app.forms import PostProblemForm, MCQOptionForm
from app.models import Problem, db, Profile
from dotenv import load_dotenv
from app.extensions import encrypt_answer
import os

contributions_bp = Blueprint('contributions', __name__)
load_dotenv()
@contributions_bp.route('/account/contribute/problem', methods=['GET', 'POST'])

def contribute():

    if not current_user.is_authenticated:
        flash("You need to login to add problems!", "danger")
        return redirect(url_for('routes.auth.login'))
    form = PostProblemForm(request.form, min_entries=6)
    # Ensure opt is not needed anymore; it's handled in PostProblemForm options.
    if form.validate_on_submit():
        title = form.title.data
        topic = form.topic.data
        content = form.content.data
        expected_answer = form.expected_answer.data   
        problem = Problem(title=title, topic=topic, author=current_user.username, content=content, encrypted_answer=encrypt_answer(expected_answer))
        profile = Profile.query.filter_by(username=current_user.username).first()
        profile.problems_posted += 1
        db.session.add(problem)
        db.session.commit()
        return redirect(url_for('routes.main.index'))

    return render_template('contribute.html', form=form)


