from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models import Problem, ProblemAttempts, UserStats
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
    attempts = ProblemAttempts.query.filter_by(problem_id=problem.id, username=current_user.username)

    if attempts.count(): # User has attempted the problem more than 3 times
        for attempt in attempts:
            if attempt.is_correct: # User has already solved the problem
                return render_template('problem.html', problem=problem, submission=submission, solved = +1, answer = decrypt_answer(problem.encrypted_answer.strip()))
        return render_template('problem.html', problem=problem, submission=submission, solved = -1, answer = decrypt_answer(problem.encrypted_answer.strip()))
    
        
    if submission.validate_on_submit():
        print('Submitted')
        answer = submission.answer.data
        print(problem.encrypted_answer.strip())
        correct_answer = decrypt_answer(problem.encrypted_answer.strip())
        if answer == correct_answer:
            problem.solved += 1
            problem.attempts += 1
            new_attempt = ProblemAttempts(username=current_user.username, problem_id=problem.id, is_correct=True)
            db.session.add(new_attempt)
            db.session.commit()
            return render_template('problem.html', problem=problem, submission=submission, solved = +1, answer = decrypt_answer(problem.encrypted_answer.strip()))
        else:
            problem.attempts += 1
            new_attempt = ProblemAttempts(username=current_user.username, problem_id=problem.id, is_correct=False)
            db.session.add(new_attempt)
            db.session.commit()
            return render_template('problem.html', problem=problem, submission=submission, solved = -1, answer = decrypt_answer(problem.encrypted_answer.strip()))
    
        
    return render_template('problem.html', problem=problem, submission=submission, solved = 0)

@problem_bp.route('/problem/<int:problem_id>/owner')
@login_required
def owner(problem_id):
    if not current_user.is_authenticated:
        print('Not authenticated')
        return redirect(url_for('routes.auth.login'))
    print('Problem ID:', problem_id)
    problem = Problem.query.filter_by(id=problem_id).first()
    return render_template('own-problem.html', problem=problem, answer = decrypt_answer(problem.encrypted_answer.strip()))

@problem_bp.route('/problem/<int:problem_id>/delete')
@login_required
def delete(problem_id):
    if not current_user.is_authenticated:
        print('Not authenticated')
        return redirect(url_for('routes.auth.login'))
    problem = Problem.query.filter_by(id=problem_id).first()
    user_stats = UserStats.query.filter_by(username=current_user.username).first()
    if problem.author == current_user.username:
        db.session.delete(problem)
        user_stats.problems_posted -= 1
        db.session.commit()
        return redirect(url_for('routes.main.index'))