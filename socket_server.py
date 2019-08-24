from flask import Flask, session
from flask_socketio import SocketIO, emit
from flask_session import Session
import eventlet


app = Flask(__name__)
app.config['SECRET_KEY'] = 'not-secret'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
socketio = SocketIO(app, async_mode='eventlet', manage_session=False)
eventlet.monkey_patch()


@socketio.on('text')
def handle_editing(text):
    # Track statistics
    emit('activity', get_activity(text), broadcast=True)


def get_activity(text):
    #TODO: REPLACE
    return {'activity': 'low'}


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
        emit('end_session', {'session_done': duration}, broadcast=True)


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


if __name__ == '__main__':
    socketio.run(app)

# gunicorn --worker-class eventlet -w 1 module:app
