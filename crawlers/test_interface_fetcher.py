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

menu_post = {
    "method": "ajax.MenuTreeAjax_rpc_load_node_gG7QNYAS_",
    "params": [{
        "interface_type": "client",
        "menu_path": ''
    }],
    "id": 1
}


class MenuFetcher(Fetcher):
    def __init__(self, company: str, jison: Jison = None, db=None,
                 max_repeat: int = 3, sleep_time: int = 0):
        super().__init__(max_repeat, sleep_time)
        self.jison = jison
        self.company = company.lower()
        self.db = db

    def change_db(self, db):
        self.db = db

    def r_dump_interface(self, menu_path: str,
                         session: requests.sessions.Session,
                         node_id: str = None,
                         debug: bool = False) -> list:
        """
        get `children` under current `menu_path`

        then acquire `sub_children` for each child in `children`

        `_q` is a queue for thread, indicating method is running as a thread
        """
        menu_post = {
            "method": "ajax.MenuTreeAjax_rpc_load_node_gG7QNYAS_",
            "params": [{
                "interface_type": "client",
                "menu_path": menu_path
            }],
            "id": 1
        }

        if _q is not None:
            jison = Jison()
            cookies = session.cookies.get_dict()
            jison.load(requests.post(self.URL_SOURCE,
                                     json=menu_post,
                                     headers=interface_header,
                                     cookies=cookies).json())
        else:
            jison = self.jison
            jison.load(session.post(self.URL_SOURCE,
                                    json=menu_post,
                                    headers=interface_header).json())
        local_children = jison.get_object('children', value_only=True)

        children = []
        # loop in `children`, acquire `sub_children` for each child
        for child in local_children:
            if child.get('hidden'):
                continue

            text = child.get('title')
            child_id = child.get('node_id')
            child_path = re.search('client_([0-9_\-]+)', child_id)
            specific_flag = False
            sub_children = []

            if debug:
                print(text)

            # normal node case (id starts with `client_xxx`)
            if child_path:
                child_path = child_path.group(1).replace('-', '/')
                sub_children = self.r_dump_interface(child_path, session)

            # if current child has no child and with a valid leaf id (a leaf)
            if not sub_children and re.search('(.+)_([\d]+_[\d]+)', child_id):
                leaf_type = self.dump_leaf_page(child_id, menu_path, text,
                                                session)
                if leaf_type in ['gap', 'title', 'text']:
                    continue

                children.append({
                    'id': child_id,
                    'text': text,
                    'type': leaf_type
                })
            # if current child has no children but with an invalid leaf id
            elif not sub_children:
                children.append({
                    'id': child_id,
                    'text': text,
                    'type': 'other'
                })
            # else, append `sub_children` to current child
            else:
                children.append({
                    'id': child_id,
                    'text': text,
                    'type': 'root',
                    'children': sub_children
                })

            if specific_flag:
                return children

        else:
            return children

    def dump_leaf_page(self, node_id: str, menu_path: str, text: str,
                       session) -> str:
        custom_page_name, index = re.search('(.+)_([\d]+_[\d]+)',
                                            node_id).groups()
        subpage_index, field_index = [int(i) for i in index.split('_')]
        leaf_post = {
            "method": "ajax.PageElementSettingAjax_rpc_html_kYjvPyv3_",
            "params": [
                {
                    "custom_page_name": custom_page_name,
                    "interface_type": "client",
                    "menu_path": menu_path,
                    "field_index": field_index,
                    "subpage_index": subpage_index,
                    "element_type": "",
                }
            ],
            "id": 1
        }

        jison = self.jison
        jison.load(session.post(f'https://{self.company.lower()}.xplan.iress.com.au/RPC2/',
                                json=leaf_post,
                                headers=self.interface_header).json())

        leaf_type = jison.get_object('title', value_only=True).lower()

        if leaf_type in ['gap', 'title', 'text']:
            return leaf_type

        if leaf_type == 'xplan':
            page_html = jison.get_multi_object('html')[2].get('html')
        else:
            page_html = jison.get_multi_object('html')[0].get('html')

        page = {}
        soup = BeautifulSoup(page_html, 'html5lib')
        # basic information for each page
        try:
            name = soup.find('option', {'selected': True}).getText()
            if re.findall('\[(.+?)\] (.+)', name):
                name = '--'.join(re.findall('\[(.+?)\] (.+)', name)[0])
        except:
            name = '(Empty)'
        if name == 'no':
            name = '(Empty)'
        if name == 'Client':
            name = text
        content = {'entities': []}

        if soup.find('input', {'checked': True, 'id': 'entity_types_1'}):
            content.get('entities').append('individual')
        if soup.find('input', {'checked': True, 'id': 'entity_types_2'}):
            content.get('entities').append('superfund')
        if soup.find('input', {'checked': True, 'id': 'entity_types_3'}):
            content.get('entities').append('partnership')
        if soup.find('input', {'checked': True, 'id': 'entity_types_4'}):
            content.get('entities').append('trust')
        if soup.find('input', {'checked': True, 'id': 'entity_types_5'}):
            content.get('entities').append('company')
        page['leaf_basic'] = content

        # try to acquire table content if an `xplan` page
        if leaf_type == 'xplan':
            content = {'table1': [], 'table2': []}

            if name.lower() in self.subgroup_name_ref:
                content['subgroup'] = self.subgroup_name_ref.get(name.lower())

            table1_method = "ajax.XplanElementListSettingAjax_rpc_html_WEaBDM8__"
            table2_method = "ajax.XplanElementEditSettingAjax_rpc_html_HBm947gH_"
            leaf_post_xtable = {
                "method": None,
                "params": [
                    {
                        "has_partner": False,
                        "domain": "factfind",
                        "guid": "00000000-0000-0000-0000-000000000000",
                        "cover_type": "",
                        "coa_access": False,
                        "entity_type": 0,
                        "locale": "AU",
                        "custom_page_name": "",
                        "editable": False,
                        "subpage_index": 0,
                        "partnerid": 0,
                        "mode": "edit",
                        "extra_params": "",
                        "field_index": 7,
                        "is_partner": False,
                        "entityid": 0,
                        "list_name": "",
                        "element_name": jison.get_object('element_name',
                                                         value_only=True),
                        "render_method": "factfind"
                    }
                ],
                "id": 1
            }

            leaf_post_xtable['method'] = table1_method
            if _q is not None:
                jison.load(
                    requests.post(f'https://{self.company.lower()}.xplan.iress.com.au/RPC2/',
                                  json=leaf_post_xtable,
                                  headers=self.interface_header,
                                  cookies=session.cookies.get_dict()).json())
            else:
                jison.load(
                    session.post(f'https://{self.company.lower()}.xplan.iress.com.au/RPC2/',
                                 json=leaf_post_xtable,
                                 headers=self.interface_header).json())

            # if this `xplan` page has list with tabs
            # process table content
            table_html = jison.get_object('tabs_html', value_only=True)
            if table_html:
                list_view_html = table_html.get('_above-tabs')
                full_view_html = table_html.get('_hidden-items')

                soup = BeautifulSoup(list_view_html, 'html5lib')
                for td in soup.find_all('td',
                                        {'style': 'white-space: nowrap'}):
                    content.get('table1').append(td.findNext('td').getText())

                soup = BeautifulSoup(full_view_html, 'html5lib')
                for td in soup.find_all('td',
                                        {'style': 'white-space: nowrap'}):
                    content.get('table2').append(td.findNext('td').getText())

            # if this `xplan` page has list with checkbox or empty page
            # process `page_html`
            else:
                for input in soup.find_all('input', {'checked': 'checked',
                                                     'name': 'xstore_listfields'}):
                    content.get('table1').append(
                        input.findNext('label').getText())

                for input in soup.find_all('input', {'checked': 'checked',
                                                     'name': 'xstore_capturefields'}):
                    content.get('table2').append(
                        input.findNext('label').getText())

            if content.get('table1') or content.get('table2'):
                page['leaf_xplan'] = content

        # not an `xplan` page
        else:
            if leaf_type == 'group':
                content = {'group': []}

                for option in soup.find('select',
                                        {'id': 'select_fields_0'}).find_all(
                    'option'):
                    content.get('group').append(option.getText())

                page['leaf_group'] = content

            elif leaf_type == 'field':
                leaf_type = 'variable'

        InterfaceLeafPage(node_id, name, leaf_type, menu_path, page).new(
            specific_db=self.db)

        return leaf_type


    def fetch(self, url: str, data: dict, session):
        """
        entry point task content: (0, prc2_url, data={'type': 'main_req', 'save': False}, 0, 0)
        """

        # if save is 'True', skip operation and return data directly
        if data.get('save'):
            return 1, data, (200, '', '')

        # return main menu names
        if data.get('type') == 'menu_req':
            interface_header = {
                'Content-Type': 'application/json',
                'referer': f'https://{self.company.lower()}.xplan.iress.com.au/factfind/edit_interface',
            }

            main_json = session.post(url,
                                     json=menu_post,
                                     headers=interface_header).json()

            new_data = {'type': data.get('type'), 'menu': main_json, 'save': False}
            return 1, new_data, (200, '', '')

        if data.get('type') == 'node_req':
            node = data.get('node')
            menu_path = data.get('menu_path')
            children = self.r_dump_interface(menu_path, session, debug=True)


























        # get the page of whole list of groups, or
        # get the page of target group, send to task_queue_p
        if data.get('type') == 'field_page' or data.get('type') == 'group_page':
            response = session.get(url, timeout=(3.05, 10))
            return 1, data, (response.status_code, response.url, response.text)

        # if the type is Multi or Choice, then get the page of choices
        elif data.get('type') == 'var_page':
            var_type = data.get('var_type')
            if var_type == 'Multi' or var_type == 'Choice':
                session.get(url)
                response = session.get(f'https://{self.company}.xplan.iress.com.au/ufield/list_options', timeout=(3.05, 10))
                return 1, data, (response.status_code, response.url, response.text)
            else:
                return 1, data, (200, '', '')

        else:
            raise Exception(f'Invalid data type: type={data.get("type")}')


class MenuParser(Parser):
    def __init__(self, company: str, max_deep: int = 2):
        super().__init__(max_deep)
        self.company = company
        self.jison = Jison()

    def parse(self, priority: int, url: str, data: dict, deep: int, content: tuple):
        *_, html_text = content
        urls = []

        # menu_req -> node_req
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
                        'type': node_type
                    },
                    'menu_path': menu_path,
                    'type': 'node_req',
                    'save': False
                }

                urls.append((
                    f'https://{self.company.lower()}.xplan.iress.com.au/RPC2/',
                    new_data,
                    priority + 1))

            stamp = ('', '')
            return 1, urls, stamp

        # node_req -> child_req


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


