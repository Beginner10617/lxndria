from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from app.models import Problem, ProblemAttempts, Profile, Solutions, Comments
from app.forms import SubmissionForm, PostProblemForm, SolutionForm, CommentForm
from app.extensions import decrypt_answer, encrypt_answer, is_number
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

    if attempts.count(): # User has attempted the problem 
        print('Attempted the problem %d times' % attempts.count())
        for attempt in attempts:
            print('Attempt:', attempt.is_correct)
            if attempt.is_correct: # User has already solved the problem
                return redirect(url_for('routes.problem.correct', problem_id=problem.id))
        return redirect(url_for('routes.problem.incorrect', problem_id=problem.id))
    
        
    if submission.validate_on_submit():
        print('Submitted')
        answer = submission.answer.data
        print(problem.encrypted_answer.strip())
        correct_answer = decrypt_answer(problem.encrypted_answer.strip())
            
        if answer == correct_answer and is_number(answer):
            problem.solved += 1
            problem.attempts += 1
            new_attempt = ProblemAttempts(username=current_user.username, problem_id=problem.id, is_correct=True)
            db.session.add(new_attempt)
            db.session.commit()
            return redirect(url_for('routes.problem.correct', problem_id=problem.id))
        elif is_number(answer):
            problem.attempts += 1
            new_attempt = ProblemAttempts(username=current_user.username, problem_id=problem.id, is_correct=False)
            db.session.add(new_attempt)
            db.session.commit()
            return redirect(url_for('routes.problem.incorrect', problem_id=problem.id))
    
        
    return render_template('problem.html', problem=problem, submission=submission, solved = 0)

@problem_bp.route('/problem/<int:problem_id>/owner', methods=['GET', 'POST'])
@login_required
def owner(problem_id):

    if not current_user.is_authenticated:
        print('Not authenticated')
        return redirect(url_for('routes.auth.login'))
    print('Problem ID:', problem_id)
    problem = Problem.query.filter_by(id=problem_id).first()
    solutions = Solutions.query.filter_by(problem_id=problem.id)
    OwnSolution = Solutions.query.filter_by(problem_id=problem_id, username=current_user.username).first()
    if OwnSolution is not None:
        posted_solution = True
        form = CommentForm()    
        solution_ids = ['S'+str(solution.id) for solution in solutions]
        comments = Comments.query.filter(Comments.parent_id.in_(solution_ids)).all()
        return render_template('own-problem.html', problem=problem, answer = decrypt_answer(problem.encrypted_answer.strip()), 
            all_solutions=solutions, posted_solution=posted_solution, form=form, comments=comments)
    else :
        posted_solution = False
    form = SolutionForm()
    if form.validate_on_submit():
        solution = Solutions(problem_id=problem.id, username=current_user.username, solution=form.solution.data)
        profile = Profile.query.filter_by(username=current_user.username).first()
        profile.solutions += 1
        db.session.add(solution)
        db.session.commit()
        return redirect(url_for('routes.problem.owner', problem_id=problem.id))
    return render_template('own-problem.html', problem=problem, answer = decrypt_answer(problem.encrypted_answer.strip()), 
        all_solutions=solutions, posted_solution=posted_solution, solution=form)
    
@problem_bp.route('/problem/<int:problem_id>/delete')
@login_required
def delete(problem_id):
    if not current_user.is_authenticated:
        print('Not authenticated')
        return redirect(url_for('routes.auth.login'))
    problem = Problem.query.filter_by(id=problem_id).first()
    profile = Profile.query.filter_by(username=current_user.username).first()
    problem_attempts = ProblemAttempts.query.filter_by(problem_id=problem.id)
    if problem.author == current_user.username:
        db.session.delete(problem)
        profile.problems_posted -= 1
        for attempt in problem_attempts:
            db.session.delete(attempt)
        db.session.commit()
        db.session.commit()
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
            problem.content = form.content.data
            problem.encrypted_answer = encrypt_answer(form.expected_answer.data)

            
            db.session.commit()
            return redirect(url_for('routes.problem.problem', problem_id=problem.id))
        return render_template('edit-problem.html', form=form)
    

@problem_bp.route('/problem/<int:problem_id>/correct')
@login_required
def correct(problem_id):
    if not current_user.is_authenticated:
        print('Not authenticated')
        return redirect(url_for('routes.auth.login'))
    # User has already solved the problem
    solution = Solutions.query.filter_by(problem_id=problem_id, username=current_user.username).first()
    problem = Problem.query.filter_by(id=problem_id).first()
    if solution is None:
        return redirect(url_for('routes.problem.solution', problem_id=problem_id))
    # User has solved the problem and submitted a solution
    all_solutions = Solutions.query.filter_by(problem_id=problem_id)
    form = CommentForm()
    solution_ids = ['S'+str(solution.id) for solution in all_solutions]
    comments = Comments.query.filter(Comments.parent_id.in_(solution_ids)).all()
    print('Comments:', comments)
    for comment in comments:
        print('Comment:', comment.content)
    return render_template('problem.html', problem=problem, solved = +1, answer = decrypt_answer(problem.encrypted_answer.strip()), 
        solved_percent = (problem.solved*100//problem.attempts), posted_solution = 1, all_solutions=all_solutions, form=form, comments=comments)

@problem_bp.route('/problem/<int:problem_id>/incorrect')
@login_required
def incorrect(problem_id):
    if not current_user.is_authenticated:
        print('Not authenticated')
        return redirect(url_for('routes.auth.login'))
    form = CommentForm()
    problem = Problem.query.filter_by(id=problem_id).first()
    all_solutions = Solutions.query.filter_by(problem_id=problem_id) 
    solution_ids = ['S'+str(solution.id) for solution in all_solutions]
    comments = Comments.query.filter(Comments.parent_id.in_(solution_ids)).all()
    return render_template('problem.html', problem=problem, solved = -1, answer = decrypt_answer(problem.encrypted_answer.strip()),
        solved_percent = (problem.solved*100//problem.attempts), posted_solution = 1, all_solutions=all_solutions, form=form, comments=comments)

@problem_bp.route('/problem/<int:problem_id>/solution', methods=['GET', 'POST'])
@login_required
def solution(problem_id):
    if not current_user.is_authenticated:
        print('Not authenticated')
        return redirect(url_for('routes.auth.login'))
    if request.method == 'GET':
        problem = Problem.query.filter_by(id=problem_id).first()
        form=SolutionForm()
        return render_template('problem.html', problem=problem, solved = +1, answer = decrypt_answer(problem.encrypted_answer.strip()), solved_percent = (problem.solved*100//problem.attempts), solution=form)
    if request.method == 'POST':
        form = SolutionForm()
        if form.validate_on_submit():
            problem = Problem.query.filter_by(id=problem_id).first()
            solution = Solutions(problem_id=problem.id, username=current_user.username, solution=form.solution.data)
            profile = Profile.query.filter_by(username=current_user.username).first()
            profile.solutions += 1
            db.session.add(solution)
            db.session.commit()
            
            return redirect(url_for('routes.problem.problem', problem_id=problem.id))
        return render_template('problem.html', problem=problem, solved = +1, answer = decrypt_answer(problem.encrypted_answer.strip()), solved_percent = (problem.solved*100//problem.attempts), solution=form)
    
@problem_bp.route('/problem/<int:problem_id>/<int:solution_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_solution(problem_id, solution_id):
    if not current_user.is_authenticated:
        print('Not authenticated')
        return redirect(url_for('routes.auth.login'))
    problem = Problem.query.filter_by(id=problem_id).first()
    if request.method == 'GET':
        solution = Solutions.query.filter_by(id=solution_id).first()
        form=SolutionForm(obj=solution)
    if request.method == 'POST':
        form = SolutionForm()
        if form.validate_on_submit():
            solution = Solutions.query.filter_by(id=solution_id).first()
            solution.solution = form.solution.data
            db.session.commit()
            return redirect(url_for('routes.problem.correct', problem_id=problem.id))
    return render_template('problem.html', problem=problem, solved = +1, answer = decrypt_answer(problem.encrypted_answer.strip()), solved_percent = (problem.solved*100//problem.attempts), solution=form, editing = 1)


@problem_bp.route('/problem/<int:problem_id>/<int:solution_id>/delete')
@login_required
def delete_solution(problem_id, solution_id):
    if not current_user.is_authenticated:
        print('Not authenticated')
        return redirect(url_for('routes.auth.login'))
    solution = Solutions.query.filter_by(id=solution_id).first()
    problem = Problem.query.filter_by(id=problem_id).first()
    if solution.username == current_user.username:
        profile = Profile.query.filter_by(username=current_user.username).first()
        profile.solutions -= 1
        db.session.delete(solution)
        db.session.commit()
        return redirect(url_for('routes.problem.correct', problem_id=problem.id))