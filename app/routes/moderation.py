from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.forms import ReportForm, ModNotes
from app.extensions import limiter, send_email
from app.models import db, Report, Problem, Solutions, Comments, Discussion, Moderators, ProblemAttempts, User
from flask_login import current_user

moderation_bp = Blueprint('moderation', __name__)


@moderation_bp.route('/moderation', methods=['GET', 'POST'])
def moderation():
    if not current_user.is_authenticated:
        return redirect(url_for('routes.auth.login'))
    if Moderators.query.filter_by(username=current_user.username).count() == 0:
        return redirect(url_for('routes.main.index'))
    reports = Report.query.filter(Report.post_by != current_user.username, Report.handled == False).order_by(Report.created_at.desc()).all()
    
    return render_template('moderation.html', reports=reports)

@moderation_bp.route('/report/<post_id>', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def report(post_id):
    form = ReportForm()
    if form.validate_on_submit():
        report = Report(parent_id=post_id, reason=form.reason.data)
        db.session.add(report)
        db.session.commit()
        flash("Report submitted successfully!", "success")
        return redirect(url_for('routes.main.index'))
    return render_template('report.html', form=form)

@moderation_bp.route('/mod_view/<content_id>', methods=['GET', 'POST'])
def mod_view(content_id):
    if not current_user.is_authenticated:
        return redirect(url_for('routes.auth.login'))
    if Moderators.query.filter_by(username=current_user.username).count() == 0:
        return redirect(url_for('routes.main.index'))
    report_val = request.args.get('report')
    report = Report.query.get(int(report_val))
    if report.handled:
        flash("This report has already been handled", "danger")
        return redirect(url_for('routes.moderation.moderation'))
    form = ModNotes()
    if form.validate_on_submit():
        report.notes = form.notes.data
        db.session.commit()
        return redirect(url_for('routes.moderation.accept', id=report_val))
    reason = report.reason
    if content_id[0] == 'P':
        problem = Problem.query.get(int(content_id[1:]))
        content = problem.title + '\n\n' + problem.content
    elif content_id[0] == 'S':
        content = Solutions.query.get(int(content_id[1:])).content
    elif content_id[0] == 'C':
        content = Comments.query.get(int(content_id[1:])).content
    elif content_id[0] == 'D':
        content = Discussion.query.get(int(content_id[1:])).content
    return render_template('mod_view.html', content=content, reason=reason, id=report.id, notes=form, content_id=content_id)

@moderation_bp.route('/moderation/decline/<id>', methods=['GET', 'POST'])
def decline(id):
    if not current_user.is_authenticated:
        return redirect(url_for('routes.auth.login'))
    if Moderators.query.filter_by(username=current_user.username).count() == 0:
        return redirect(url_for('routes.main.index'))
    
    report = Report.query.get(int(id))
    if report.handled:
        flash("This report has already been handled", "danger")
        return redirect(url_for('routes.moderation.moderation'))
    report.handled = True
    report.handled_by = current_user.username
    report.action = 'Declined'
    db.session.commit()
    return redirect(url_for('routes.moderation.moderation'))

@moderation_bp.route('/moderation/accept/<id>', methods=['GET', 'POST'])
def accept(id):
    if not current_user.is_authenticated:
        return redirect(url_for('routes.auth.login'))
    if Moderators.query.filter_by(username=current_user.username).count() == 0:
        return redirect(url_for('routes.main.index'))
    report = Report.query.get(int(id))
    if report.handled:
        flash("This report has already been handled", "danger")
        return redirect(url_for('routes.moderation.moderation'))
    content, author = '', ''
    # Remove the post, send an email to the user, and delete the report
    parent_id = report.parent_id
    if parent_id[0] == 'P':
        Id = int(parent_id[1:])
        problem = Problem.query.filter_by(id = Id).first()
        if problem is None:
            report.handled = True
            db.session.commit()
            flash("The post has already been removed", "danger")
            return redirect(url_for('routes.moderation.moderation'))
        content = problem.title + '\n\n' + problem.content
        author = problem.author
        problem_attempts = ProblemAttempts.query.filter_by(problem_id=Id)
        for attempt in problem_attempts:
            db.session.delete(attempt)
        db.session.commit()
        solutions = Solutions.query.filter_by(problem_id=problem.id).all()
        for solution in solutions:
            comments = Comments.query.filter_by(parent_id = 'S'+str(solution.id)).all()
            for comment in comments:
                db.session.delete(comment)
            db.session.delete(solution)
        db.session.delete(problem)
        db.session.commit()

    elif parent_id[0] == 'S':
        Id = int(parent_id[1:])
        solution = Solutions.query.filter_by(id=Id).first()
        if solution is None:
            report.handled = True
            db.session.commit()
            flash("The post has already been removed", "danger")
            return redirect(url_for('routes.moderation.moderation'))
        author = solution.author
        content = solution.content
        db.session.delete(solution)
        db.session.commit()
        comments = Comments.query.filter_by(parent_id = 'S'+str(Id)).all()
        for comment in comments:
            db.session.delete(comment)
        db.session.commit()
        
    elif parent_id[0] == 'D':
        Id = int(parent_id[1:])
        discussion = Discussion.query.filter_by(id = Id).first()
        if discussion is None:
            report.handled = True
            db.session.commit()
            flash("The post has already been removed", "danger")
            return redirect(url_for('routes.moderation.moderation'))
        author = discussion.author
        content = discussion.title + '\n\n' + discussion.content
        db.session.delete(discussion)
        db.session.commit()
        comments = Comments.query.filter_by(parent_id = 'D'+str(Id)).all()
        for comment in comments:
            db.session.delete(comment)
        db.session.commit()
        
    elif parent_id[0] == 'C':
        Id = int(parent_id[1:])
        comment = Comments.query.filter_by(id=Id).first()
        if comment is None:
            report.handled = True
            db.session.commit()
            flash("The post has already been removed", "danger")
            return redirect(url_for('routes.moderation.moderation'))
        author = comment.author
        content = comment.content
        db.session.delete(comment)
        db.session.commit()
    
    # Draft and send an email to the user
    mod_email = User.query.filter_by(username=current_user.username).first().email
    email = User.query.filter_by(username=author).first().email
    subject = "Your post has been removed " + "#"+id
    body = "Hello! Your post has been removed from the website. If you have any queries, please contact the moderators."
    body = body + "\nReason: " + report.reason + "\n\nModerator Notes: " + report.notes
    body = body + "\n\nContent: \n" + content
    send_email([email], subject, body, cc=[mod_email])
    report.handled = True
    report.handled_by = current_user.username
    report.action = 'Removed'
    db.session.commit()
    return redirect(url_for('routes.moderation.moderation'))