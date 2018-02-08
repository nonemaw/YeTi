from fuzzier.jison import Jison
from app.socketio import sio
from crawlers.field_fetcher import FieldFetcher
from crawlers.interface_fetcher import InterfaceFetcher
from common.db import modify_timestamp, create_timestamp


class CrawlerLoader:
    def __init__(self, company: str, f_jison: Jison = None,
                 i_jison: Jison = None, f_db=None, i_db=None):
        if not f_jison:
            f_jison = Jison()
        if not i_jison:
            i_jison = Jison()
        self.f_db = f_db
        self.i_db = i_db
        self.company = company
        self.terminate = False

        self.field_fetcher = FieldFetcher(company, f_jison, f_db)
        self.interface_fetcher = InterfaceFetcher(company, i_jison, i_db)

    def change_company(self, company: str):
        self.field_fetcher.change_company(company)
        self.interface_fetcher.change_company(company)

    def fetch(self, username: str, password: str, specific: list = None,
              group_only: str = None, operation_type: str = None):
        sio.start_background_task(self.notification, db_name=self.company)
        # self.field_fetcher.fetch(username, password, group_only=group_only)
        # self.interface_fetcher.fetch(username, password, specific=specific)
        import time
        time.sleep(20)

        # if operation_type == 'update':
        #     # modify timestamp
        #     modify_timestamp(self.f_db, ['Group', 'SubGroup', 'InterfaceNode',
        #                                  'InterfaceLeafPage'])
        #
        # elif operation_type == 'create':
        #     # create timestamp
        #     create_timestamp(self.f_db, ['Group', 'SubGroup', 'InterfaceNode',
        #                                  'InterfaceLeafPage'])
        self.stop_notify()

    def notification(self, db_name: str):
        while not self.terminate:
            sio.sleep(1)
            sio.emit('DB Fetching', {'data': 'db running', 'db_name': db_name},
                     namespace='/db_event')

    def stop_notify(self):
        self.terminate = True

    def notify_success(self):
        counter = 2
        while counter:
            sio.emit('DB Fetching', {'data': 'db running', 'status': True},
                     namespace='/db_event')
            counter -= 1

    def notify_failed(self):
        counter = 2
        while counter:
            sio.emit('DB Fetching', {'data': 'db running', 'status': False},
                     namespace='/db_event')
            counter -= 1
