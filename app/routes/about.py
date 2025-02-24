from flask import Blueprint, render_template
import os
about_bp = Blueprint('about', __name__)

@about_bp.route('/about')
def about():
    return render_template('about.html', email=os.getenv('EMAIL_ID'))
