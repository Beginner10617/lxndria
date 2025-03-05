from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from app.models import User, Problem, Discussion

main_bp = Blueprint('main', __name__)
@main_bp.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('routes.about.about'), code=301)
    pageNumber = request.args.get('page', default=0, type=int)
    rows = request.args.get('rows', default=10, type=int)
    table = request.args.get('table', default='problems', type=str)
    sort_by = request.args.get('sort', default='created_at', type=str)
    sort_convention = request.args.get('convention', default='desc', type=str)
    if sort_by == 'created_at':
        if sort_convention == 'asc':
            all_problems = Problem.query.order_by(Problem.created_at).all()
            all_discussions = Discussion.query.order_by(Discussion.created_at).all()
            need_solution = Problem.query.filter(Problem.needs_solution == True).order_by(Problem.created_at).all()
        else:
            all_problems = Problem.query.order_by(Problem.created_at.desc()).all()
            all_discussions = Discussion.query.order_by(Discussion.created_at.desc()).all()
            need_solution = Problem.query.filter(Problem.needs_solution == True).order_by(Problem.created_at).all()
    elif sort_by == 'Popularity':
        if sort_convention == 'asc':
            all_problems = Problem.query.order_by(Problem.popularity_value).all()
            all_discussions = Discussion.query.order_by(Discussion.popularity_value).all()
            need_solution = Problem.query.filter(Problem.needs_solution == True).order_by(Problem.created_at).all()
        else:
            all_problems = Problem.query.order_by(Problem.popularity_value.desc()).all()
            all_discussions = Discussion.query.order_by(Discussion.popularity_value.desc()).all()
            need_solution = Problem.query.filter(Problem.needs_solution == True).order_by(Problem.created_at).all()
    elif sort_by == 'Difficulty':
        if sort_convention == 'asc':
            all_problems = Problem.query.order_by(Problem.difficulty_value).all()
            all_discussions = Discussion.query.order_by(Discussion.created_at).all()
            need_solution = Problem.query.filter(Problem.needs_solution == True).order_by(Problem.created_at).all()
        else:
            all_problems = Problem.query.order_by(Problem.difficulty_value.desc()).all()
            all_discussions = Discussion.query.order_by(Discussion.created_at.desc()).all()
            need_solution = Problem.query.filter(Problem.needs_solution == True).order_by(Problem.created_at).all()
   #(all_problems)
    new_sort_convention = 'asc' if sort_convention == 'desc' else 'desc'
    return render_template('index.html', problems=all_problems, page=pageNumber, row_per_page=rows, discussions=all_discussions, table=table, need_solution=need_solution, sort_convention=new_sort_convention)

