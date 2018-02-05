from gevent import monkey
monkey.patch_all()  # must be done at the very top of APP

import os
import argparse
import socketio
from gevent.pywsgi import WSGIServer

try:
    from geventwebsocket.handler import WebSocketHandler
    websocket = True
except ImportError:
    websocket = False

from app import create_app
from app.models import Role
from common.meta import Meta


sio = socketio.Server(logger=True, async_mode='gevent')
yeti = create_app(os.getenv('FLASK_CONFIG') or 'default')
yeti.wsgi_app = socketio.Middleware(sio, yeti.wsgi_app)
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', '-P', type=int, default=5000,
                        help='Listening port (default: 5000)')
    parser.add_argument('--host', '-H', default='127.0.0.1',
                        help='Host address (default: 127.0.0.1)')
    parser.add_argument('--debug', '-D', required=False, action='store_true',
                        help='Debug Mode')
    parser.add_argument('--test', '-T', required=False, action='store_true',
                        help='Test')
    args = parser.parse_args()

    Meta.initialize()
    Role.insert_roles()
    yeti.debug = True

    # run on sync debug server
    if args.debug:
        yeti.run(debug=True)

    # feature test
    elif args.test:
        pass

    # run on gevent server
    else:
        if websocket:
            http_server = WSGIServer((args.host, args.port), yeti, log=None,
                              handler_class=WebSocketHandler)
        else:
            http_server = WSGIServer((args.host, args.port), yeti,
                                     log=None)

        try:
            print(f'YeTi is running on http://{args.host}:{args.port}')
            http_server.serve_forever()
        except KeyboardInterrupt:
            pass
