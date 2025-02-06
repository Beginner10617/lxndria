from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from app.forms import PostDiscussionForm
from app.models import Discussion, db, UserStats

discussion_bp = Blueprint('discussion', __name__)

@discussion_bp.route('/account/contribute/discussion', methods=['GET', 'POST'])
@login_required
def post_discussion():
    form = PostDiscussionForm()
    if form.validate_on_submit():
        discussion = Discussion(title=form.title.data, content=form.content.data, user=current_user)
        db.session.add(discussion)
        user_stats = UserStats.query.filter_by(username=current_user.username).first()
        user_stats.discussions += 1
        db.session.commit()
        flash("Discussion posted successfully!", "success")
        return redirect(url_for('routes.discussion.view_discussion', discussion_id=discussion.id))
    return render_template('post-discussion.html', form=form)

@discussion_bp.route('/discussion/<int:discussion_id>')
def view_discussion(discussion_id):
    discussion = Discussion.query.get(discussion_id)
    return render_template('discussion.html', discussion=discussion)

@discussion_bp.route('/discussion/<int:discussion_id>/delete', methods=['POST', 'GET'])
@login_required
def delete_discussion(discussion_id):
    discussion = Discussion.query.get(discussion_id)
    if discussion.user == current_user:
        db.session.delete(discussion)
        user_stats = UserStats.query.filter_by(username=current_user.username).first()
        user_stats.discussions -= 1
        db.session.commit()
        flash("Discussion deleted successfully!", "success")
    else:
        flash("You can't delete someone else's discussion!", "danger")
    return redirect(url_for('routes.account.account', discussion_id=discussion_id))

@discussion_bp.route('/discussion/<int:discussion_id>/edit', methods=['POST', 'GET'])
@login_required
def edit_discussion(discussion_id):
    discussion = Discussion.query.get(discussion_id)
    if discussion.user != current_user:
        flash("You can't edit someone else's discussion!", "danger")
        return redirect(url_for('routes.account.account', discussion_id=discussion_id))
    form = PostDiscussionForm(obj=discussion)
    if form.validate_on_submit():
        discussion.title = form.title.data
        discussion.content = form.content.data
        db.session.commit()
        flash("Discussion edited successfully!", "success")
        return redirect(url_for('routes.discussion.view_discussion', discussion_id=discussion.id))
    return render_template('post-discussion.html', form=form)