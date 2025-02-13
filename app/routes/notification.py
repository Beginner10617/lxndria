from flask import Blueprint, request, jsonify
from app.models import Notifications
from flask_login import current_user
notification_bp = Blueprint('notification', __name__)

@notification_bp.route('/notifs')
def get_notifs():
    if current_user.is_authenticated:

        notifs = Notifications.query.filter_by(username=current_user.username, read=False).order_by(Notifications.created_at.desc()).all()
        return jsonify([notif.serialize for notif in notifs])
    