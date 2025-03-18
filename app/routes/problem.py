from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from app.models import Problem, ProblemAttempts, Profile, Solutions, Comments, Upvotes, Bookmarks, Notifications
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
   #('Problem ID:', problem_id)
    problem = Problem.query.filter_by(id=problem_id).first()
    if not current_user.is_authenticated:
        attempts = []
        pass
    elif problem.author == current_user.username:
        return redirect(url_for('routes.problem.owner', problem_id=problem.id))
    else:
        attempts = ProblemAttempts.query.filter_by(problem_id=problem.id, username=current_user.username)
    # Increment the view count of the problem
    try:
        problem.views += 1
    except:
        problem.views = 1
    db.session.commit()

    if not current_user.is_authenticated:
        pass
    elif attempts.count(): # User has attempted the problem 
       #('Attempted the problem %d times' % attempts.count())
        for attempt in attempts:
           #('Attempt:', attempt.is_correct)
            if attempt.is_correct: # User has already solved the problem
                return redirect(url_for('routes.problem.correct', problem_id=problem.id))
        return redirect(url_for('routes.problem.incorrect', problem_id=problem.id))
    
        
    if submission.validate_on_submit():
        if not current_user.is_authenticated:
            return redirect(url_for('routes.auth.login'))
       #('Submitted')
        answer = submission.answer.data
       #(problem.encrypted_answer.strip())
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
    if current_user.is_authenticated:
        bookmark = Bookmarks.query.filter_by(problem_id=problem_id, username=current_user.username).first()
    else:
        bookmark = None
    return render_template('problem.html', problem=problem, submission=submission, solved = 0, bookmarked=bookmark)

@problem_bp.route('/problem/<int:problem_id>/owner', methods=['GET', 'POST'])
def owner(problem_id):
    if not current_user.is_authenticated:
       #('Not authenticated')
        return redirect(url_for('routes.auth.login'))
    #('Problem ID:', problem_id)
    problem = Problem.query.filter_by(id=problem_id).first()
    
    solutions = Solutions.query.filter_by(problem_id=problem.id)
    OwnSolution = Solutions.query.filter_by(problem_id=problem_id, username=current_user.username).first()
    if problem.author != current_user.username:
        return redirect(url_for('routes.problem.problem', problem_id=problem.id))
    form = CommentForm()    
    solution_ids = ['S'+str(solution.id) for solution in solutions]
    comments = Comments.query.filter(Comments.parent_id.in_(solution_ids)).all()
    SolForm = SolutionForm()
       
    if OwnSolution is not None:
        posted_solution = True
       #'OwnSolution:', OwnSolution)
        return render_template('own-problem.html', problem=problem, answer = decrypt_answer(problem.encrypted_answer.strip()), 
            all_solutions=solutions, posted_solution=posted_solution, form=form, comments=comments)
    else :
        posted_solution = False
       #'No solution yet')
    
    if SolForm.validate_on_submit():
       #'solution posted', SolForm.solution.data)
        solution = Solutions(problem_id=problem.id, username=current_user.username, solution=SolForm.solution.data)
        db.session.add(solution)
        db.session.commit()
        return redirect(url_for('routes.problem.owner', problem_id=problem.id))
   #'No solution submitted')
    return render_template('own-problem.html', problem=problem, answer = decrypt_answer(problem.encrypted_answer.strip()), 
        all_solutions=solutions, posted_solution=posted_solution, solution=SolForm, form=form, comments=comments)
    
@problem_bp.route('/problem/<int:problem_id>/delete')
def delete(problem_id):
    if not current_user.is_authenticated:
       #('Not authenticated')
        return redirect(url_for('routes.auth.login'))
    problem = Problem.query.filter_by(id=problem_id).first()
    
    problem_attempts = ProblemAttempts.query.filter_by(problem_id=problem.id)
    if problem.author == current_user.username:
        for attempt in problem_attempts:
            db.session.delete(attempt)
        db.session.commit()
        solutions = Solutions.query.filter_by(problem_id=problem.id).all()
        #print('Solutions:', solutions)
        for solution in solutions:
        #   #solution.solution)
            comments = Comments.query.filter_by(parent_id = 'S'+str(solution.id)).all()
        #   #'Comments:', comments)
            for comment in comments:
        #       #comment.content)
                db.session.delete(comment)
            db.session.delete(solution)
        db.session.delete(problem)
        db.session.commit()
        return redirect(url_for('routes.main.index'))
    return redirect(url_for('routes.problem.problem', problem_id=problem.id))

@problem_bp.route('/problem/<int:problem_id>/edit', methods=['GET', 'POST'])
def edit(problem_id):
    if not current_user.is_authenticated:
       #('Not authenticated')
        return redirect(url_for('routes.auth.login'))
    problem = Problem.query.filter_by(id=problem_id).first()
    if problem.author != current_user.username:
        return redirect(url_for('routes.problem.problem', problem_id=problem.id))
        
    if request.method == 'GET':
        form=PostProblemForm(obj=problem)
        form.expected_answer.data = decrypt_answer(problem.encrypted_answer.strip())
        return render_template('edit-problem.html', problem=problem, form=form)
    if request.method == 'POST':
        form = PostProblemForm()
        if form.validate_on_submit():
            problem = Problem.query.filter_by(id=problem_id).first()
            if problem.author != current_user.username:
                return redirect(url_for('routes.problem.problem', problem_id=problem.id))
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
def correct(problem_id):
    if not current_user.is_authenticated:
       #('Not authenticated')
        return redirect(url_for('routes.auth.login'))
    problem = Problem.query.filter_by(id=problem_id).first()
    
    attempts = ProblemAttempts.query.filter_by(problem_id=problem_id, username=current_user.username)
    if attempts.count() == 0:
        return redirect(url_for('routes.problem.problem', problem_id=problem_id))
    elif attempts.first().is_correct == False:
        return redirect(url_for('routes.problem.incorrect', problem_id=problem_id))
    # User has already solved the problem
    solution = Solutions.query.filter_by(problem_id=problem_id, username=current_user.username).first()
    if solution is None:
        return redirect(url_for('routes.problem.solution', problem_id=problem_id))
    # User has solved the problem and submitted a solution
    all_solutions = Solutions.query.filter_by(problem_id=problem_id)
    form = CommentForm()
    solution_ids = ['S'+str(solution.id) for solution in all_solutions]
    comments = Comments.query.filter(Comments.parent_id.in_(solution_ids)).all()
    bookmark = Bookmarks.query.filter_by(problem_id=problem_id, username=current_user.username).first()
    
    return render_template('problem.html', problem=problem, solved = +1, answer = decrypt_answer(problem.encrypted_answer.strip()), 
        solved_percent = (problem.solved*100//problem.attempts), posted_solution = 1, all_solutions=all_solutions, form=form, 
        comments=comments, bookmarked=bookmark)

@problem_bp.route('/problem/<int:problem_id>/incorrect')
def incorrect(problem_id):
    if not current_user.is_authenticated:
       #('Not authenticated')
        return redirect(url_for('routes.auth.login'))
    problem = Problem.query.filter_by(id=problem_id).first()
    
    attempts = ProblemAttempts.query.filter_by(problem_id=problem_id, username=current_user.username)
    if attempts.count() == 0:
        return redirect(url_for('routes.problem.problem', problem_id=problem_id))
    elif attempts.first().is_correct == True:
        return redirect(url_for('routes.problem.correct', problem_id=problem_id))
    form = CommentForm()
    all_solutions = Solutions.query.filter_by(problem_id=problem_id) 
    solution_ids = ['S'+str(solution.id) for solution in all_solutions]
    comments = Comments.query.filter(Comments.parent_id.in_(solution_ids)).all()
    bookmark = Bookmarks.query.filter_by(problem_id=problem_id, username=current_user.username).first()
    
    return render_template('problem.html', problem=problem, solved = -1, answer = decrypt_answer(problem.encrypted_answer.strip()),
        solved_percent = (problem.solved*100//problem.attempts), posted_solution = 1, all_solutions=all_solutions, form=form, 
        comments=comments, bookmarked=bookmark)

@problem_bp.route('/problem/<int:problem_id>/solution', methods=['GET', 'POST'])
def solution(problem_id):
    if not current_user.is_authenticated:
       #('Not authenticated')
        return redirect(url_for('routes.auth.login'))
    problem = Problem.query.filter_by(id=problem_id).first()
    
    if request.method == 'GET':
        Solform=SolutionForm()

        all_solutions = Solutions.query.filter_by(problem_id=problem_id)
        form = CommentForm()
        solution_ids = ['S'+str(solution.id) for solution in all_solutions]
        comments = Comments.query.filter(Comments.parent_id.in_(solution_ids)).all()
        bookmark = Bookmarks.query.filter_by(problem_id=problem_id, username=current_user.username).first()
    

        return render_template('problem.html', problem=problem, solved = +1, answer = decrypt_answer(problem.encrypted_answer.strip()), solved_percent = (problem.solved*100//(problem.attempts+1)), solution=Solform
            , all_solutions=all_solutions, form=form, comments=comments, bookmarked=bookmark)
    if request.method == 'POST':

        form = SolutionForm()
        if form.validate_on_submit():
            problem = Problem.query.filter_by(id=problem_id).first()
            solution = Solutions(problem_id=problem.id, username=current_user.username, solution=form.solution.data)
            
            db.session.add(solution)
            db.session.commit()

            # Send notification to the author of the problem
            if solution.username != problem.author:
                new_notification = Notifications(
                        parent_id='S' + str(solution.id),
                        username=problem.author
                    )
                db.session.add(new_notification)
                db.session.commit()
                
            return redirect(url_for('routes.problem.problem', problem_id=problem.id))
        return render_template('problem.html', problem=problem, solved = +1, answer = decrypt_answer(problem.encrypted_answer.strip()), solved_percent = (problem.solved*100//problem.attempts), solution=form)
    
@problem_bp.route('/problem/<int:problem_id>/<int:solution_id>/edit', methods=['GET', 'POST'])
def edit_solution(problem_id, solution_id):
    if not current_user.is_authenticated:
       #('Not authenticated')
        return redirect(url_for('routes.auth.login'))
    problem = Problem.query.filter_by(id=problem_id).first()
    if solution.username != current_user.username:
        return redirect(url_for("routes.main.index"))
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
def delete_solution(problem_id, solution_id):
    if not current_user.is_authenticated:
       #('Not authenticated')
        return redirect(url_for('routes.auth.login'))
    solution = Solutions.query.filter_by(id=solution_id).first()
    problem = Problem.query.filter_by(id=problem_id).first()
    
    if solution.username == current_user.username:
        db.session.delete(solution)
        db.session.commit()
        comments = Comments.query.filter_by(parent_id = 'S'+str(solution_id)).all()
        for comment in comments:
            db.session.delete(comment)
        db.session.commit()
        return redirect(url_for('routes.problem.correct', problem_id=problem.id))
    
@problem_bp.route('/problem/<int:problem_id>/<int:solution_id>/like')
def like_solution(problem_id, solution_id):
    if not current_user.is_authenticated:
       #('Not authenticated')
        return redirect(url_for('routes.auth.login'))
    problem = Problem.query.filter_by(id=problem_id).first()
    
    solution = Solutions.query.filter_by(id=solution_id).first()
    upvote = Upvotes.query.filter_by(solution_id=solution_id, username=current_user.username).first()
    profile = Profile.query.filter_by(username=solution.username).first()
    if upvote is None and solution.username != current_user.username:
        upvote = Upvotes(solution_id=solution_id, username=current_user.username)
        db.session.add(upvote)
        solution.upvotes += 1
        profile.upvotes += 1
        db.session.commit()
    else:
        db.session.delete(upvote)
        solution.upvotes -= 1
        profile.upvotes -= 1
        db.session.commit()
    return redirect(url_for('routes.problem.problem', problem_id=problem_id))

@problem_bp.route('/problem/<int:problem_id>/bookmark')
def bookmark_problem(problem_id):
    if not current_user.is_authenticated:
       #('Not authenticated')
        return redirect(url_for('routes.auth.login'))
    problem = Problem.query.filter_by(id=problem_id).first()
    
    bookmark = Bookmarks.query.filter_by(problem_id=problem_id, username=current_user.username).first()
    if bookmark is None:
        bookmark = Bookmarks(problem_id=problem_id, username=current_user.username)
        db.session.add(bookmark)
        db.session.commit()
    else:
        db.session.delete(bookmark)
        db.session.commit()
    return redirect(url_for('routes.problem.problem', problem_id=problem_id))