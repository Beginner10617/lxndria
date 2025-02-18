from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.forms import ReportForm
from app.extensions import limiter

moderation_bp = Blueprint('moderation', __name__)


@moderation_bp.route('/moderation', methods=['GET', 'POST'])
def moderation():
    return render_template('moderation.html')

@moderation_bp.route('/report/<post_id>', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def report(post_id):
    if request.method == 'POST':
        pass
    form = ReportForm()
    return render_template('report.html', form=form)