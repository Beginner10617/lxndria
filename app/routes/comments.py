from flask import url_for, flash, redirect, Blueprint, request
from app import mail, db, limiter, login_manager
from app.models import Comments, Notifications, Discussion, Solutions, User
from app.forms import CommentForm
from flask_login import current_user

comments_bp = Blueprint('comments', __name__)

# Handle ONLY comment posting, editing, deletion etc
# GET requests should be handled by the respective blueprints of discussions, problems etc

@comments_bp.route("/comment", methods=["POST"])
def handle_comment():
    form = CommentForm()
    if form.validate_on_submit():
        post_id = request.form.get("post_id")  # Get post_id from the form
        post_type = request.form.get("post_type")  # Get type (post/article)
        new_comment = Comments(
            parent_id=post_type + str(post_id),
            username=current_user.username,
            content=form.content.data
        )

        db.session.add(new_comment)
        db.session.commit()
        user_to_notify = [] # List of users to notify (usernames)

        if post_type == "D":
            discussion = Discussion.query.get(int(post_id))
            if discussion is None:
                flash("Discussion not found", "danger")
                return redirect(request.referrer or url_for("index"))
            user_to_notify.append(discussion.author)

        elif post_type == "S":
            solution = Solutions.query.get(int(post_id))
            if solution is None:
                flash("Solution not found", "danger")
                return redirect(request.referrer or url_for("index"))
            user_to_notify.append(solution.username)
            user_to_notify.append(solution.problem.author)
        user_tagged = [text[1:] for text in form.content.data.split() if text.startswith("@") and (text[1:] not in user_to_notify)]
        user_tagged = list(set(user_tagged))
       #user_tagged+user_to_notify)
        for user in user_to_notify + user_tagged:
            if user == current_user.username:
                continue
            if User.query.filter_by(username=user).first() is None:
                flash(f"User {user} not found", "danger")
                continue
            if user in user_to_notify:    
                new_notification = Notifications(
                    parent_id='C' + str(new_comment.id),
                    username=user
                )
            else:
                new_notification = Notifications(
                    parent_id='C' + str(new_comment.id)+'T',
                    username=user
                )
           #new_notification.message)
            db.session.add(new_notification)

        db.session.commit()

        
    return redirect(request.referrer or url_for("post_view", post_id=post_id))

@comments_bp.route("/comment/<int:comment_id>/delete")
def delete_comment(comment_id):
    comment = Comments.query.get(comment_id)
    if comment is None:
        flash("Comment not found", "danger")
        return redirect(request.referrer or url_for("index"))

    if comment.username != current_user.username:
        flash("You do not have permission to delete this comment", "danger")
        return redirect(request.referrer or url_for("index"))

    db.session.delete(comment)
    db.session.commit()
    flash("Comment deleted", "success")
    return redirect(request.referrer or url_for("index"))
