from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from app.forms import PostProblemForm, MCQOptionForm
from app.models import Problem, db
from dotenv import load_dotenv
import os

contributions_bp = Blueprint('contributions', __name__)
load_dotenv()
@contributions_bp.route('/account/contribute/problem', methods=['GET', 'POST'])
@login_required
def contribute():
    form = PostProblemForm(request.form, min_entries=6)
    # Ensure opt is not needed anymore; it's handled in PostProblemForm options.
    if form.validate_on_submit():
        title = form.title.data
        topic = form.topic.data
        content = form.content.data
        expected_answer = form.expected_answer.data   
        problem = Problem(title=title, topic=topic, answer=expected_answer, author=current_user.username)
        db.session.add(problem)
        db.session.commit()
        path = os.getenv('UPLOAD_FOLDER')+f"/{current_user.username}/Problems/{problem.id}.txt"
        with open(path, "w") as f:
            f.write(content)
        return redirect(url_for('routes.main.index'))

    return render_template('contribute.html', form=form)


