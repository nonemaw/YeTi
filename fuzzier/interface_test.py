import requests
import re
import threading
import queue
from jison import Jison
from bs4 import BeautifulSoup
from common.meta import Meta
from app.models import InterfaceNode, InterfaceLeafPage
from pprint import pprint as pp

class InterfaceFetcher:
    URL_SOURCE = f'https://{Meta.company}.xplan.iress.com.au/RPC2/'
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

    interface_header = {
        'Accept': 'text/plain',
        'Accept-Encoding': 'gzip',
        'Content-Type': 'application/json',
        'referer': 'https://ytml.xplan.iress.com.au/factfind/edit_interface',
    }

    def update_name_ref(self, name_chunk: dict):
        if isinstance(name_chunk, dict):
            self.subgroup_name_ref.update(name_chunk)

    def deduce_name_ref(self, name_chunk: list):
        if isinstance(name_chunk, list):
            for name in name_chunk:
                try:
                    del self.subgroup_name_ref[name.lower()]
                except:
                    pass

    def fetch(self, specific: list = None):
        URL_LOGIN = f'https://{Meta.company}.xplan.iress.com.au/home'
        URL_HOME = f'https://{Meta.company}.xplan.iress.com.au/dashboard/mainhtml'
        URL_LOGOUT = f'https://{Meta.company}.xplan.iress.com.au/home/logoff?'


        with requests.session() as session:
            payload = {
                "userid": Meta.company_username,
                "passwd": Meta.company_password,
                "rolename": "User",
                "redirecturl": ''
            }
            header = {
                'referer': URL_LOGIN
            }
            menu_post = {
                "method": "ajax.MenuTreeAjax_rpc_load_node_gG7QNYAS_",
                "params": [{
                    "interface_type": "client",
                    "menu_path": ''
                }],
                "id": 1
            }

            # send POST to login page, check login status
            session.post(URL_LOGIN, data=payload, headers=header)
            r = session.get(URL_HOME)
            if re.search(r'permission_error|Login for User', r.text):
                raise Exception('Currently there is another user using this XPLAN account.')

            Meta.jison.load_json(session.post(self.URL_SOURCE, json=menu_post, headers=self.interface_header).json())
            menu_nodes = Meta.jison.get_object('children')

            menu = []
            for node in menu_nodes.get('children'):
                if node.get('hidden'):
                    continue

                node_type = 'root'
                if node.get('is_wizard'):
                    node_type = 'wizard'

                menu.append({
                    'id': node.get('node_id'),
                    'text': node.get('title'),
                    'type': node_type,
                    'children': []
                })

            threads = []
            _q = queue.Queue()
            for node in menu:
                menu_path = re.search('client_([0-9_\-]+)', node.get('id'))
                if menu_path:
                    menu_path = menu_path.group(1).replace('-', '/')
                    if specific and specific[0].lower() in node.get('text').lower():
                        specific.pop(0)
                        node['children'] = self.r_dump_interface(menu_path, session, specific=specific)
                        InterfaceNode(node).new(force=True, depth=len(specific))
                        break
                    elif specific:
                        continue

                    # children = self.r_dump_interface(menu_path, session)
                    # if children:
                    #     node['children'] = children
                    # else:
                    #     node['type'] = 'other'
                    threads.append(threading.Thread(target=self.r_dump_interface, args=(menu_path, session, node.get('id'), _q)))

            if threads:
                for _t in threads:
                    _t.start()
                for _t in threads:
                    _t.join()

                result_cache = {}
                while not _q.empty():
                    result_cache.update(_q.get())

                for node in menu:
                    children = result_cache.get(node.get('id'))
                    if children:
                        node['children'] = children
                    else:
                        node['type'] = 'other'
                    InterfaceNode(node).new(force=True)

            session.get(URL_LOGOUT)

    def r_dump_interface(self, menu_path: str, session: requests.sessions.Session, node_id: str = None, _q: queue.Queue = None, specific: list = None) -> list:
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
        else:
            jison = Meta.jison
        jison.load_json(session.post(self.URL_SOURCE, json=menu_post, headers=self.interface_header).json())
        local_children = jison.get_object('children')

        children = []
        # loop in `children`, acquire `sub_children` for each child
        for child in local_children.get('children'):
            if child.get('hidden'):
                continue

            text = child.get('title')
            child_id = child.get('node_id')
            child_path = re.search('client_([0-9_\-]+)', child_id)
            specific_flag = False
            sub_children = []

            if specific and specific[0].lower() in text.lower():
                specific.pop(0)
                specific_flag = True
            elif specific:
                continue

            # normal node case (id starts with `client_xxx`)
            if child_path:
                child_path = child_path.group(1).replace('-', '/')
                sub_children = self.r_dump_interface(child_path, session, _q=_q, specific=specific)

            # if current child has no children and with a valid leaf id (a leaf)
            if not sub_children and re.search('(.+)_([\d]+_[\d]+)', child_id):
                leaf_type = self.dump_leaf_page(child_id, menu_path, text, session, _q=_q)
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

        if node_id and _q is not None:
            _q.put({node_id: children})
        else:
            return children

    def dump_leaf_page(self, node_id: str, menu_path: str, text: str, session: requests.sessions.Session, _q: queue.Queue = None) -> str:
        custom_page_name, index = re.search('(.+)_([\d]+_[\d]+)', node_id).groups()
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

        if _q is not None:
            jison = Jison()
        else:
            jison = Meta.jison

        jison.load_json(session.post(self.URL_SOURCE, json=leaf_post, headers=self.interface_header).json())
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
        content = {name: []}

        if soup.find('input', {'checked': True, 'id': 'entity_types_1'}):
            content.get(name).append('individual')
        if soup.find('input', {'checked': True, 'id': 'entity_types_2'}):
            content.get(name).append('superfund')
        if soup.find('input', {'checked': True, 'id': 'entity_types_3'}):
            content.get(name).append('partnership')
        if soup.find('input', {'checked': True, 'id': 'entity_types_4'}):
            content.get(name).append('trust')
        if soup.find('input', {'checked': True, 'id': 'entity_types_5'}):
            content.get(name).append('company')
        page['leaf_basic'] = content

        # try to acquire table content if an `xplan` page
        if leaf_type == 'xplan':
            content = {'table1': [], 'table2': []}

            if name.lower() in self.subgroup_name_ref:
                page['subgroup'] = self.subgroup_name_ref.get(name.lower())

            table1_method = "ajax.XplanElementListSettingAjax_rpc_html_WEaBDM8__"
            table2_method = "ajax.XplanElementEditSettingAjax_rpc_html_HBm947gH_"
            leaf_post_xtable = {
                "method": "",
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
                        "element_name": jison.get_object('element_name').get('element_name'),
                        "render_method": "factfind"
                    }
                ],
                "id": 1
            }

            leaf_post_xtable['method'] = table1_method
            jison.load_json(session.post(self.URL_SOURCE, json=leaf_post_xtable, headers=self.interface_header).json())

            # if this `xplan` page has list with tabs
            # process table content
            table_html = jison.get_object('tabs_html', value_only=True)
            if table_html:
                list_view_html = table_html.get('_above-tabs')
                full_view_html = table_html.get('_hidden-items')

                soup = BeautifulSoup(list_view_html, 'html5lib')
                for td in soup.find_all('td', {'style': 'white-space: nowrap'}):
                    content.get('table1').append(td.findNext('td').getText())

                soup = BeautifulSoup(full_view_html, 'html5lib')
                for td in soup.find_all('td', {'style': 'white-space: nowrap'}):
                    content.get('table2').append(td.findNext('td').getText())

            # if this `xplan` page has list with checkbox or empty page
            # process `page_html`
            else:
                for input in soup.find_all('input', {'checked': 'checked', 'name': 'xstore_listfields'}):
                    content.get('table1').append(input.findNext('label').getText())

                for input in soup.find_all('input', {'checked': 'checked', 'name': 'xstore_capturefields'}):
                    content.get('table2').append(input.findNext('label').getText())

            if content.get('table1') or content.get('table2'):
                page['leaf_xplan'] = content

        # not an `xplan` page
        else:
            if leaf_type == 'group':
                content = {'group': []}

                for option in soup.find('select', {'id': 'select_fields_0'}).find_all('option'):
                    content.get('group').append(option.getText())

                page['leaf_group'] = content

            elif leaf_type == 'field':
                leaf_type = 'variable'

        page['leaf_type'] = leaf_type
        InterfaceLeafPage(node_id, text, page).new()

        return leaf_type


if __name__ == '__main__':
    password = 'Passw0rdOCT'
    from app.db import mongo_connect, client

    specific = []
    #specific = input('specific nodes (optional): ')
    if not specific:
        specific = []
    else:
        specific = [x.strip() for x in specific.split(',') if x]

    Meta.jison = Jison()
    Meta.company = 'ytml'
    Meta.company_username = 'ytml2'
    Meta.company_password = password
    Meta.db_company = Meta.db_default if Meta.company == 'ytml' else mongo_connect(
        client, Meta.company)
    Meta.interface_fetcher = InterfaceFetcher()
    Meta.interface_fetcher.fetch(specific)
