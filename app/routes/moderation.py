from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.forms import ReportForm
from app.extensions import limiter, decrypt_answer
from app.models import db, Report, Appeals, Problem, Solutions, Comments, Discussion, Flagged_Content
from flask_login import current_user

moderation_bp = Blueprint('moderation', __name__)


@moderation_bp.route('/moderation', methods=['GET', 'POST'])
def moderation():
    reports = Report.query.filter(Report.post_by != current_user.username).order_by(Report.created_at.desc()).all()
    appeals = Appeals.query.all()

    return render_template('moderation.html', reports=reports, appeals=appeals)

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
    report_val = request.args.get('report')
    report = Report.query.get(int(report_val))
    reason = report.reason
    if content_id[0] == 'P':
        problem = Problem.query.get(int(content_id[1:]))
        content = problem.title + '\n\n' + problem.content + '\n\nAnswer : ' + decrypt_answer(problem.encrypted_answer)
    elif content_id[0] == 'S':
        content = Solutions.query.get(int(content_id[1:]))
    elif content_id[0] == 'C':
        content = Comments.query.get(int(content_id[1:]))
    elif content_id[0] == 'D':
        content = Discussion.query.get(int(content_id[1:]))
    return render_template('mod_view.html', content=content, reason=reason, id=report.id)

@moderation_bp.route('/moderation/decline/<id>', methods=['GET', 'POST'])
def decline(id):
    report = Report.query.get(int(id))
    db.session.delete(report)
    db.session.commit()
    return redirect(url_for('routes.moderation.moderation'))

@moderation_bp.route('/moderation/accept/<id>', methods=['GET', 'POST'])
def accept(id):
    report = Report.query.get(int(id))
    flag = Flagged_Content(parent_id=report.parent_id, reason=report.reason, flagged_by=current_user.username)
    db.session.add(flag)
    db.session.delete(report)
    db.session.commit()
    return redirect(url_for('routes.moderation.moderation'))