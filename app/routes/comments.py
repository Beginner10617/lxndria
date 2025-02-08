from flask import url_for, flash, redirect, Blueprint, request
from app import mail, db, limiter, login_manager
from app.models import Comments
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

        # Redirect back to the correct page
        if post_type == "post":
            return redirect(url_for("post_view", post_id=post_id))
        elif post_type == "article":
            return redirect(url_for("article_view", article_id=post_id))
    
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
