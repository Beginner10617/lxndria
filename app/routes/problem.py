from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models import Problem
from app.forms import SubmissionForm
problem_bp = Blueprint('problem', __name__)

@problem_bp.route('/account/problem/<int:problem_id>')
def problem(problem_id):
    submission = SubmissionForm()
    
    print('Problem ID:', problem_id)
    if not current_user.is_authenticated:
        print('Not authenticated')
        return redirect(url_for('routes.auth.login'))
    problem = Problem.query.filter_by(id=problem_id).first()
    return render_template('problem.html', problem=problem, submission=submission)