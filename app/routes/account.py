from .auth import current_user
from flask import Blueprint, render_template, redirect, url_for
account_bp = Blueprint('account', __name__)

@account_bp.route('/account')
def account():
    print('Account')
    if not current_user.is_authenticated:
        print('Not authenticated')
        return redirect(url_for('routes.auth.login'))
    return render_template('account.html')