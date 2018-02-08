from . import sio


@sio.on('DB event', namespace='/db_event')
def db_event_message(sid, message):
    sio.emit('DB Fetching', {'data': message['data']}, room=sid,
             namespace='/db_event')


@sio.on('DB event broadcast', namespace='/db_event')
def db_event_broadcast_message(sid, message):
    sio.emit('DB Fetching', {'data': message['db_event']},
             namespace='/db_event')


@sio.on('join', namespace='/db_event')
def join(sid, message):
    sio.enter_room(sid, message['room'], namespace='/db_event')
    sio.emit('DB Fetching', {'data': 'Entered room: ' + message['room']},
             room=sid, namespace='/db_event')


@sio.on('leave', namespace='/db_event')
def leave(sid, message):
    sio.leave_room(sid, message['room'], namespace='/db_event')
    sio.emit('DB Fetching', {'data': 'Left room: ' + message['room']},
             room=sid, namespace='/db_event')


@sio.on('close room', namespace='/db_event')
def close(sid, message):
    sio.emit('DB Fetching',
             {'data': 'Room ' + message['room'] + ' is closing.'},
             room=message['room'], namespace='/db_event')
    sio.close_room(message['room'], namespace='/db_event')


@sio.on('my room event', namespace='/db_event')
def send_room_message(sid, message):
    sio.emit('DB Fetching', {'data': message['data']}, room=message['room'],
             namespace='/db_event')


@sio.on('disconnect request', namespace='/db_event')
def disconnect_request(sid):
    sio.disconnect(sid, namespace='/db_event')


@sio.on('connect', namespace='/db_event')
def db_event_connect(sid, environ):
    sio.emit('DB Fetching', {'data': 'Connected', 'count': 0}, room=sid,
             namespace='/db_event')


@sio.on('disconnect', namespace='/db_event')
def db_event_disconnect(sid):
    print('Client disconnected')
