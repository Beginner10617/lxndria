from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.forms import ReportForm
from app.extensions import limiter
from app.models import db, Report, Discussion, Problem, Solutions, Comments

moderation_bp = Blueprint('moderation', __name__)


@moderation_bp.route('/moderation', methods=['GET', 'POST'])
def moderation():
    return render_template('moderation.html')

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