from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from app.forms import PostDiscussionForm
from app.models import Discussion, db

discussion_bp = Blueprint('discussion', __name__)

@discussion_bp.route('/account/contribute/discussion', methods=['GET', 'POST'])
@login_required
def post_discussion():
    form = PostDiscussionForm()
    if form.validate_on_submit():
        discussion = Discussion(title=form.title.data, content=form.content.data, user=current_user)
        db.session.add(discussion)
        db.session.commit()
        flash("Discussion posted successfully!", "success")
        return redirect(url_for('routes.discussion.view_discussion', discussion_id=discussion.id))
    return render_template('post-discussion.html', form=form)

@discussion_bp.route('/discussion/<int:discussion_id>')
def view_discussion(discussion_id):
    discussion = Discussion.query.get(discussion_id)
    return render_template('discussion.html', discussion=discussion)