import socketio

sio = socketio.Server(logger=True, async_mode='gevent')

from . import db_event