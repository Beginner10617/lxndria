from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models import Problem
from app.forms import SubmissionForm
from app.extensions import decrypt_answer
from app import db
problem_bp = Blueprint('problem', __name__)

@problem_bp.route('/problem/<int:problem_id>', methods=['GET', 'POST'])
def problem(problem_id):
    submission = SubmissionForm()
    print('Problem ID:', problem_id)
    if not current_user.is_authenticated:
        print('Not authenticated')
        return redirect(url_for('routes.auth.login'))
    problem = Problem.query.filter_by(id=problem_id).first()
    if problem.author == current_user.username:
        return redirect(url_for('routes.problem.owner', problem_id=problem.id))
    if submission.validate_on_submit():
        print('Submitted')
        answer = submission.answer.data
        print(problem.encrypted_answer.strip())
        correct_answer = decrypt_answer(problem.encrypted_answer.strip())
        if answer == correct_answer:
            problem.solved += 1
            problem.attempts += 1
            db.session.commit()
            return redirect(url_for('routes.main.index'))
        else:
            problem.attempts += 1
            db.session.commit()
            return redirect(url_for('routes.main.index'))
        
    return render_template('problem.html', problem=problem, submission=submission)

@problem_bp.route('/problem/<int:problem_id>/owner')
@login_required
def owner(problem_id):
    if not current_user.is_authenticated:
        print('Not authenticated')
        return redirect(url_for('routes.auth.login'))
    print('Problem ID:', problem_id)
    problem = Problem.query.filter_by(id=problem_id).first()
    return render_template('own-problem.html', problem=problem, answer = decrypt_answer(problem.encrypted_answer.strip()))