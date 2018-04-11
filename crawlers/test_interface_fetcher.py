import requests
import re
import json
import threading
import queue
import copy
from datetime import datetime
from fuzzier.jison import Jison
from bs4 import BeautifulSoup
from app.models import InterfaceNode, InterfaceLeafPage

from crawlers.core.workers import Fetcher, Parser, Saver
from crawlers.core.thread_pool import ThreadPool
from crawlers.core.config import get_url_legal


subgroup_name_ref = {
    'telephone/email list': 'Contact',
    'address list': 'Address',
    'employment': 'Employment',
    'dependent': 'Dependent',
    'goals': 'Goals',
    'income': 'Cashflow',
    'expense': 'Cashflow',
    'asset list': 'Balance Sheet-Asset',
    'liability list': 'Balance Sheet-Liability',
    'existing funds': 'Superannuation-Plans',
    'retirement income': 'Retirement Income',
    'bank details': 'Bank',
    'insurance group': 'Insurance Group',
    'insurance group by cover': 'Insurance Group',
    'general insurance policies': 'Risk',
    'medical insurance': 'Medical Insurance',
}



""" data structure sample:
NODE:
"id": client_10
"text": FMD Wizard
"type": root
"children": [
    "id": client_10-12
    "text": FMD SMSF
    "type": root
    "children": [
        "id": client_10-12-5
        "text": SMSF Name
        "type": variable/group/xplan
    ]
]

LEAF:
"id": cachflow_0_6
"text": Expense
"leaf_type": xplan
"menu_path": 4/0
"page": {
    "leaf_basic": ...
    "leaf_xplan": ...
}

"""


class MenuFetcher(Fetcher):
    def __init__(self, company: str, jison: Jison = None, db=None,
                 max_repeat: int = 3, sleep_time: int = 0):
        super().__init__(max_repeat, sleep_time)
        self.jison = jison
        self.company = company.lower()
        self.db = db

    def change_db(self, db):
        self.db = db

    def fetch(self, url: str, data: dict, session):
        """
        entry point task content: (0, prc2_url, data={'type': 'main_req', 'save': False}, 0, 0)
        """

        # if save is 'True', skip operation and return data directly
        if data.get('save'):
            return 1, data, (200, '', '')

        # return main menu names
        if data.get('type') == 'menu_req':
            menu_post = {
                "method": "ajax.MenuTreeAjax_rpc_load_node_gG7QNYAS_",
                "params": [{
                    "interface_type": "client",
                    "menu_path": ''
                }],
                "id": 1
            }
            interface_header = {
                'Content-Type': 'application/json',
                'referer': f'https://{self.company.lower()}.xplan.iress.com.au/factfind/edit_interface',
            }

            main_json = session.post(url,
                                     json=menu_post,
                                     headers=interface_header).json()

            new_data = {'type': data.get('type'), 'menu': main_json, 'save': False}
            return 1, new_data, (200, '', '')

        # return each menu (node)'s children list
        if data.get('type') == 'child_req':
            menu_path = data.get('menu_path')

            menu_post = {
                "method": "ajax.MenuTreeAjax_rpc_load_node_gG7QNYAS_",
                "params": [{
                    "interface_type": "client",
                    "menu_path": menu_path
                }],
                "id": 1
            }
            interface_header = {
                'Content-Type': 'application/json',
                'referer': f'https://{self.company.lower()}.xplan.iress.com.au/factfind/edit_interface',
            }

            self.jison.load(session.post(url,
                                         json=menu_post,
                                         headers=interface_header).json())

            local_children = self.jison.get_object('children', value_only=True)
            children = []
            for child in local_children:
                if child.get('hidden'):
                    continue

                text = child.get('title')
                child_id = child.get('node_id')
                child_path = re.search('client_([0-9_\-]+)', child_id)
                specific_flag = False
                sub_children = []

                if child_path:
                    child_path = child_path.group(1).replace('-', '/')
                    sub_children =










        # dump each leaf's content
        if data.get('type') == 'leaf_req':
            pass








class MenuParser(Parser):
    def __init__(self, company: str, max_deep: int = 2):
        super().__init__(max_deep)
        self.company = company
        self.jison = Jison()

    def parse(self, priority: int, url: str, data: dict, deep: int, content: tuple):
        *_, html_text = content
        url = f'https://{self.company.lower()}.xplan.iress.com.au/RPC2/'
        urls = []

        # menu_req -> child_req
        # store each menu and change the data type to 'child_req'
        if data.get('type') == 'menu_req':
            self.jison.load(data.get('menu'))
            menu_nodes = self.jison.get_object('children', value_only=True)
            for node in menu_nodes:
                menu_path = re.search('client_([0-9_\-]+)', node.get('id'))
                if not menu_path:
                    continue

                if node.get('hidden'):
                    continue

                menu_path = menu_path.group(1).replace('-', '/')
                node_type = 'root'
                if node.get('is_wizard'):
                    node_type = 'wizard'

                new_data = {
                    'node': {
                        'id': node.get('node_id'),
                        'text': node.get('title'),
                        'type': node_type,
                        'children': []
                    },
                    'menu_path': menu_path,
                    'type': 'child_req',
                    'save': False
                }

                urls.append((
                    url,
                    new_data,
                    priority + 1))

            return 1, urls, ('', '')

        if data.get('type') == 'child_req':
            if data.get('local_children_json'):
                """ received data sample:
                    data = {
                        'node': {
                            'id': xxx,
                            'text': xxx,
                            'type': xxx,
                            'children': []
                        },
                        'local_children_json': 'local_children_json',
                        'menu_path': xxx,
                        'type': 'child_req',
                        'save': False
                    }
                """
                self.jison.load(data.get('local_children_json'))

                local_children = self.jison.get_object('children', value_only=True)
                for child in local_children:
                    if child.get('hidden'):
                        continue

                    text = child.get('title')
                    child_id = child.get('node_id')
                    child_path = re.search('client_([0-9_\-]+)', child_id)
                    specific_flag = False
                    sub_children = []

                    if child_path:
                        child_path = child_path.group(1).replace('-', '/')

                    new_data = copy.deepcopy(data)
                    del new_data['local_children_json']







        return 0, [], ()


class MenuSaver(Saver):
    def __init__(self, pipe):
        super().__init__(pipe)
        if isinstance(self.pipe, str):
            self.pipe = f'{self.pipe}.json'

    def save(self, url: str, data, stamp: tuple):
        if isinstance(self.pipe, str):
            with open(self.pipe, 'a') as F:
                F.write(f'{data},\n')

        else:
            try:
                # assume this is a db access instance, e.g. pymongo clientconnect
                pass

            except:
                pass

        return True


def login(username: str, password: str, company: str):
    session = requests.session()
    payload = {
        "userid": username,
        "passwd": password,
        "rolename": "User",
        "redirecturl": ''
    }
    session.post(f'https://{company}.xplan.iress.com.au/home',
                 data=payload,
                 headers={'referer': f'https://{company}.xplan.iress.com.au/home'})
    field_page = session.get(f'https://{company}.xplan.iress.com.au/ufield/list').text
    if re.search(r'permission_error|Login for User', field_page):
        raise Exception(
            'Currently there is another user using this XPLAN account.')

    return session

def logout(session, company: str):
    session.get(f'https://{company}.xplan.iress.com.au/home/logoff?')


if __name__ == "__main__":
    company = 'ytml'
    username = 'ytml2'
    password = 'Passw0rdOCT'
    session = login(username, password, company)

    url = f'https://{company}.xplan.iress.com.au/ufield/list'
    fetcher = MenuFetcher(company)
    parser = MenuParser(company)
    saver = MenuSaver(pipe='tttttttttttt')
    filter = None

    spider = ThreadPool(fetcher, parser, saver, filter, fetcher_num=1)
    spider.run(url, initial_data=json.dumps({'type': 'main_req'}), priority=0, deep=0, session=session)

    logout(session, company)


