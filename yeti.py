
from gevent import monkey
monkey.patch_all()  # must be done at the very top of APP

import os
import argparse
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from app import create_app
from app.models import Role
from common.fetcher import Fetcher
from common.meta import Meta
from fuzzier.fuzzier import search


yeti = create_app(os.getenv('FLASK_CONFIG') or 'default')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', '-P', type=int, default=5000,help='Listening port (default: 5000)')
    parser.add_argument('--host', '-H', default='127.0.0.1',help='Host address (default: 127.0.0.1)')
    parser.add_argument('--debug', '-D', required=False, action='store_true', help='Debug Mode')
    parser.add_argument('--fetcher', '-F', required=False, action='store_true', help='Run Fetcher')
    parser.add_argument('--test', '-T', required=False, action='store_true', help='Test')
    args = parser.parse_args()

    Role.insert_roles()
    yeti.debug = True
    if args.debug:
        yeti.run(debug=True)

    elif args.fetcher:
        company, username, password = input('Please input company, username and password: ').split(' ')
        groups = input('Please input groups (optional): ')
        if groups:
            groups = groups.strip().split(',')
            groups = [group.strip() for group in groups]
        else:
            groups = None

        Meta.company = company
        Fetcher(username, password, group_only=groups).run()

    elif args.test:
        pattern = input('Input test pattern: ')
        search(pattern=pattern)

    else:
        http_server = WSGIServer((args.host, args.port), yeti, log=None,
                                 handler_class=WebSocketHandler)
        try:
            print("YeTi is running on http://{}:{}".format(args.host, args.port))
            http_server.serve_forever()
        except KeyboardInterrupt:
            pass
