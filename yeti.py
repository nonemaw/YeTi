from gevent import monkey

monkey.patch_all()  # must be done at the very top of APP

import os
import argparse
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from app import create_app
from app.models import Role


yeti = create_app(os.getenv('FLASK_CONFIG') or 'default')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', '-P', type=int, default=5000,
                        help='Listening port (default: 5000)')
    parser.add_argument('--host', '-H', default='127.0.0.1',
                        help='Host address (default: 127.0.0.1)')
    parser.add_argument('--debug', '-D', required=False, action='store_true',
                        help='Debug Mode')
    parser.add_argument('--fetcher', '-F', required=False, action='store_true',
                        help='Run Fetcher')
    parser.add_argument('--ifetcher', '-IF', required=False, action='store_true',
                        help='Run Interface Fetcher')
    parser.add_argument('--search', '-S', required=False, action='store_true',
                        help='Test')
    args = parser.parse_args()

    Role.insert_roles()
    yeti.debug = True
    if args.debug:
        yeti.run(debug=True)

    # feature test
    elif args.fetcher:
        company, username, password = input(
            'Please input company, username and password: ').split(' ')
        groups = input('Please input groups (optional): ')
        if not groups:
            groups = None

        from common.fetcher import Fetcher
        from common.meta import Meta
        from fuzzier.jison import Jison
        from app.db import mongo_connect, client

        Meta.company = company
        Meta.company_username = username
        Meta.company_password = password
        Meta.db_company = Meta.db_default if Meta.company == 'ytml' else mongo_connect(
            client, Meta.company)
        Meta.jison = Jison(file_name=Meta.company)
        Meta.fetcher = Fetcher()
        Meta.fetcher.fetch(groups)

    # feature test
    elif args.ifetcher:
        company, username, password = input(
            'Please input company, username and password: ').split(',')
        specific = input('Please input specific nodes (optional): ')
        if not specific:
            specific = []
        else:
            specific = [x.strip() for x in specific.split(',') if x]

        from common.interface_fetcher import InterfaceFetcher
        from common.meta import Meta
        from fuzzier.jison import Jison
        from app.db import mongo_connect, client

        Meta.company = company
        Meta.company_username = username
        Meta.company_password = password
        Meta.db_company = Meta.db_default if Meta.company == 'ytml' else mongo_connect(
            client, Meta.company)
        Meta.jison = Jison(file_name=Meta.company)
        Meta.interface_fetcher = InterfaceFetcher()
        Meta.interface_fetcher.fetch(specific=specific)

    # feature test
    elif args.search:
        from fuzzier.fuzzier import search
        pattern = input('Input search pattern for test: ')
        search(pattern=pattern)

    else:
        http_server = WSGIServer((args.host, args.port), yeti, log=None,
                                 handler_class=WebSocketHandler)
        try:
            print(
                "YeTi is running on http://{}:{}".format(args.host, args.port))
            http_server.serve_forever()
        except KeyboardInterrupt:
            pass
