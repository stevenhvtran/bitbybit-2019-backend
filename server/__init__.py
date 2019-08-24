import eventlet
eventlet.monkey_patch()

from flask import Flask, session
from flask_socketio import emit
from flask_session import Session
from flask_cors import CORS
from flask_socketio import SocketIO

socketio = SocketIO()


@socketio.on('text')
def handle_editing(text):
    # Track statistics
    emit('activity', get_activity(text), broadcast=True)


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
    count = word_count(text)
    prev_count = session['prev_text']
    changed_words = 0
    for word in count.keys():
        if word in prev_count.keys():
            if count[word] > prev_count[word]:
                changed_words += count[word] - prev_count[word]
        else:
            changed_words += count[word]

    session['prev_text'] = count

    if changed_words >= 55:
        return 'high'
    elif changed_words >= 20:
        return 'medium'
    elif changed_words > 0:
        return 'low'
    else:
        return 'none'


@socketio.on('start_session')
def handle_start_session(duration):
    session['ended'] = False
    session['remaining_time'] = duration

    # Keep Socket responsive by sleeping for 2 minutes at a time
    while session['remaining_time'] > 0:
        if session['remaining_time'] > 120:
            session['remaining_time'] -= 120
            eventlet.sleep(120)
        else:
            session['remaining_time'] = 0
            eventlet.sleep(session['remaining_time'])

    if not session['ended']:
        emit('end_session', 'done', broadcast=True)


@socketio.on('end_session')
def handle_end_session():
    session['remaining_time'] = 0
    session['ended'] = True


@socketio.on('break')
def handle_break(duration):
    session['remaining_time'] += duration


@socketio.on('connect')
def test_connect():
    emit('my response', {'data': 'Connected'})


@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')

# Server is hosted on localhost:5000


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
    return app

