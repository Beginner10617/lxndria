from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from app.models import Problem, ProblemAttempts, UserStats
from app.forms import SubmissionForm, PostProblemForm
from app.extensions import decrypt_answer, encrypt_answer
from app import db
from dotenv import load_dotenv
import os
load_dotenv()
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
                return render_template('problem.html', problem=problem, submission=submission, solved = +1, answer = decrypt_answer(problem.encrypted_answer.strip()), solved_percent = (problem.solved*100//problem.attempts))
        return render_template('problem.html', problem=problem, submission=submission, solved = -1, answer = decrypt_answer(problem.encrypted_answer.strip()), solved_percent = (problem.solved*100//problem.attempts))
    
        
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
            return render_template('problem.html', problem=problem, submission=submission, solved = +1, answer = decrypt_answer(problem.encrypted_answer.strip()), solved_percent = (problem.solved*100//problem.attempts))
        else:
            problem.attempts += 1
            new_attempt = ProblemAttempts(username=current_user.username, problem_id=problem.id, is_correct=False)
            db.session.add(new_attempt)
            db.session.commit()
            return render_template('problem.html', problem=problem, submission=submission, solved = -1, answer = decrypt_answer(problem.encrypted_answer.strip()), solved_percent = (problem.solved*100//problem.attempts))
    
        
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
    problem_attempts = ProblemAttempts.query.filter_by(problem_id=problem.id)
    if problem.author == current_user.username:
        db.session.delete(problem)
        user_stats.problems_posted -= 1
        for attempt in problem_attempts:
            db.session.delete(attempt)
        db.session.commit()
        db.session.commit()
        problem_file = os.getenv('UPLOAD_FOLDER')+f"/{current_user.username}/Problems/{problem.id}.txt"
        os.remove(problem_file)
        return redirect(url_for('routes.main.index'))

@problem_bp.route('/problem/<int:problem_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(problem_id):
    if not current_user.is_authenticated:
        print('Not authenticated')
        return redirect(url_for('routes.auth.login'))
    if request.method == 'GET':
        problem = Problem.query.filter_by(id=problem_id).first()
        form=PostProblemForm(obj=problem)
        form.expected_answer.data = decrypt_answer(problem.encrypted_answer.strip())
        return render_template('edit-problem.html', problem=problem, form=form)
    if request.method == 'POST':
        form = PostProblemForm()
        if form.validate_on_submit():
            problem = Problem.query.filter_by(id=problem_id).first()
            problem.title = form.title.data
            problem.topic = form.topic.data
            problem.attempts = 0
            problem.solved = 0
            content = form.content.data
            expected_answer = form.expected_answer.data
            problem_file = os.getenv('UPLOAD_FOLDER')+f"/{current_user.username}/Problems/{problem.id}.txt"
            with open(problem_file, "w") as f:
                f.write(content + "\n <<Answer: " + encrypt_answer(expected_answer)+">>")
    
            db.session.commit()
            return redirect(url_for('routes.problem.problem', problem_id=problem.id))
        return render_template('edit-problem.html', form=form)