from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from app.forms import PostDiscussionForm, CommentForm
from app.models import Discussion, db, Profile, Comments, Bookmarks

discussion_bp = Blueprint('discussion', __name__)

@discussion_bp.route('/account/contribute/discussion', methods=['GET', 'POST'])
def post_discussion():
    if not current_user.is_authenticated:
        flash("You need to login to add discussions!", "danger")
        return redirect(url_for('routes.auth.login'))
    form = PostDiscussionForm()
    if form.validate_on_submit():
        discussion = Discussion(title=form.title.data, content=form.content.data, user=current_user)
        db.session.add(discussion)
        profile = Profile.query.filter_by(username=current_user.username).first()
        profile.discussions += 1
        db.session.commit()
        flash("Discussion posted successfully!", "success")
        return redirect(url_for('routes.discussion.view_discussion', discussion_id=discussion.id))
    return render_template('post-discussion.html', form=form)

@discussion_bp.route('/discussion/<int:discussion_id>')
def view_discussion(discussion_id):
    if not current_user.is_authenticated:
        flash("You need to login to view discussions!", "danger")
        return redirect(url_for('routes.auth.login'))
    
    discussion = Discussion.query.get(discussion_id)
    if current_user.username != discussion.user.username:
        try:
            discussion.views += 1
        except:
            discussion.views = 1
        bookmarked = Bookmarks.query.filter_by(username=current_user.username, discussion_id=discussion_id).first()
        db.session.commit()
    else:
        bookmarked = None
    form = CommentForm()
    comments = Comments.query.filter_by(parent_id = 'D'+str(discussion_id)).all()
    return render_template('discussion.html', discussion=discussion, comments=comments, form=form, bookmarked=bookmarked)

@discussion_bp.route('/discussion/<int:discussion_id>/delete', methods=['POST', 'GET'])
@login_required
def delete_discussion(discussion_id):
    discussion = Discussion.query.get(discussion_id)
    if discussion.user == current_user:
        db.session.delete(discussion)
        profile = Profile.query.filter_by(username=current_user.username).first()
        profile.discussions -= 1
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

@discussion_bp.route('/discussion/<int:discussion_id>/bookmark')
@login_required
def bookmark_discussion(discussion_id):
    discussion = Discussion.query.get(discussion_id)
    bookmark = Bookmarks.query.filter_by(username=current_user.username, discussion_id=discussion_id).first()
    if bookmark:
        db.session.delete(bookmark)
        db.session.commit()
        flash("Bookmark removed successfully!", "success")
    else:
        bookmark = Bookmarks(username=current_user.username, discussion_id=discussion_id)
        db.session.add(bookmark)
        db.session.commit()
        flash("Bookmark added successfully!", "success")
    return redirect(url_for('routes.discussion.view_discussion', discussion_id=discussion_id))