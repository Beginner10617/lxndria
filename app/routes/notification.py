from flask import Blueprint, request, jsonify, redirect, url_for, render_template
from app.models import Notifications
from flask_login import current_user
from app import db
notification_bp = Blueprint('notification', __name__)

@notification_bp.route('/notifs')
def get_notifs():
    if current_user.is_authenticated:

        notifs = Notifications.query.filter_by(username=current_user.username, read=False).order_by(Notifications.created_at.desc()).all()
        
        return jsonify([notif.serialize for notif in notifs if notif.message != '404'])
    return jsonify({'error': 'User not authenticated'})
    
@notification_bp.route('/markread')
def mark_read():
    if not current_user.is_authenticated:
        return jsonify({'error': 'User not authenticated'})
    if request.args.get("all"):
        notifs = Notifications.query.filter_by(username=current_user.username, read=False).all()
        for notif in notifs:
            notif.read = True
        db.session.commit()
        return jsonify({'success': 'All marked as read'})
    hash_value = request.args.get("hash")
   #'hash=', hash_value)
    if hash_value.startswith("comment-"):
        parent_ids = ['C'+hash_value[8:], 'C'+hash_value[8:]+'T']
        for parent_id in parent_ids:
            notif = Notifications.query.filter_by(parent_id=parent_id, read=False).first()
            if notif is None:
                return jsonify({})
            notif.read = True
            db.session.commit()
    elif hash_value.startswith("solution-"):
        parent_id = 'S'+hash_value[9:]
        notif = Notifications.query.filter_by(parent_id=parent_id, read = False).first()
        if notif is None:
            return jsonify({'error': 'Notification not found'})
        notif.read = True
        db.session.commit()
    return jsonify({'success': 'Marked as read'})

@notification_bp.route('/notifications')
def get_notifications():
    if not current_user.is_authenticated:
        return redirect(url_for('routes.auth.login'))
    notifs = Notifications.query.filter_by(username=current_user.username).order_by(Notifications.created_at.desc()).all()
    notifications = []
    for notif in notifs:
        if notif.message == '404':
            continue
        notifications.append(notif)
    return render_template('notifications.html', notifications=notifications)