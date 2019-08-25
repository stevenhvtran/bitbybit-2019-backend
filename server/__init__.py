import eventlet
eventlet.monkey_patch()

from flask import Flask, session
from flask_socketio import emit
from flask_session import Session
from flask_cors import CORS
from flask_socketio import SocketIO
from datetime import datetime
import requests
from server import android_compat

socketio = SocketIO()


def log_activity(changed_words):
    requests.post('http://note-by-note.herokuapp.com/activity', json={
        'changed_words': changed_words
    })


@socketio.on('text')
def handle_editing(data):
    emit('debug', data, broadcast=True)

    # Track statistics
    activity = get_activity(data['text'])
    session['prev_activity'] = activity
    emit('activity', activity, broadcast=True)


def word_count(text):
    words = text.split()
    count = dict()

    for word in words:
        if word in count.keys():
            count[word] += 1
        else:
            count[word] = 1

    return count


def get_activity(text):
    edit_time = datetime.now()
    if session.get('prev_edit_time') is None:
        session['prev_edit_time'] = datetime.now()

    if session.get('prev_text') is None:
        session['prev_text'] = {}

    prev_edit_time = session['prev_edit_time']
    time_elapsed = (edit_time - prev_edit_time).seconds

    # If previous time text difference was examined was in last two minutes,
    # return previous activity reading
    if time_elapsed < 10:
        return session['prev_activity']

    # Count the differences in words
    count = word_count(text)
    prev_count = session['prev_text']
    changed_words = 0
    for word in count.keys():
        if word in prev_count.keys():
            if count[word] > prev_count[word]:
                changed_words += count[word] - prev_count[word]
        else:
            changed_words += count[word]

    # Update the text history
    session['prev_text'] = count
    session['prev_edit_time'] = edit_time

    # Log changed words
    log_activity(changed_words)

    if changed_words >= 8:
        return 'high'
    elif changed_words >= 3:
        return 'medium'
    elif changed_words > 0:
        return 'low'
    else:
        return 'none'


@socketio.on('start_session')
def handle_start_session(data):
    emit('debug', data, broadcast=True)

    firebase = android_compat.get_db()
    firebase.child('start_session').set(data['duration'])


@socketio.on('end_session')
def handle_end_session():
    session['remaining_time'] = 0
    session['ended'] = True


@socketio.on('break')
def handle_break(data):
    emit('debug', data, broadcast=True)

    session['break_issued'] = True
    db = android_compat.get_db()
    db.child('break').update(data['duration'])


@socketio.on('connect')
def connect():
    print('Client Connected')


@socketio.on('disconnect')
def disconnect():
    print('Client disconnected')


@socketio.on('debug')
def handle_debug(data):
    print("DEBUG: ", data)


def stream_break_handler(message):
    if session.get('break_issued') is None or (session.get('break_issued') is not None and session.get('break_issued') is False):
        duration = message['data']
        if duration > 0:
            emit('break', {'duration': duration}, broadcast=True)


def end_session_handler(message):
    if session.get('end_issued') is None or (session.get('end_issued') is not None and session.get('end_issued') is False):
        emit('end_session', 'okay', broadcast=True)
        session['remaining_time'] = 0
        session['ended'] = True


def create_app():
    """
    Creates the Flask app using an application factory setup
    :return: The app as a Flask object
    """
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'not-secret'
    app.config['SESSION_TYPE'] = 'filesystem'
    Session(app)
    CORS(app)
    socketio.init_app(app, async_mode='eventlet', manage_session=False,
                      cors_allowed_origins='*')

    with app.app_context():
        db = android_compat.get_db()
        db.child('break').stream(stream_break_handler)
        db.child('end_session').stream(end_session_handler)
        session['db'] = db

    return app
