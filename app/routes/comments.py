from flask import url_for, flash, redirect, Blueprint, render_template
from app import mail, db, limiter, login_manager
from app.models import User
from app.forms import CommentForm

comments_bp = Blueprint('comments', __name__)

# Handle ONLY comment posting, editing, deletion etc
# GET requests should be handled by the respective blueprints of discussions, problems etc