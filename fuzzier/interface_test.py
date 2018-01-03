
import requests
import re
import os
import json
from pprint import pprint
from jison import Jison


TEST_URL = 'https://ytml.xplan.iress.com.au/RPC2/'


interface_header = {
    'Accept': 'text/plain',
    'Accept-Encoding': 'gzip',
    'Content-Type': 'application/json',
    'referer': 'https://ytml.xplan.iress.com.au/factfind/edit_interface',
}

menu_req = {
    "method": "ajax.MenuTreeAjax_rpc_load_node_gG7QNYAS_",
    "params": [{
        "interface_type": "client",
        "menu_path": ""
    }],
    "id": 1
}

"""
FMD SoA Wizard - [client_52]
    FMD SMSF SoA Wizard - [client_52-3]
        Assets & Liabilities - [client_52-3-1]
                -> `52-3-1` as `menu_path`
            Add Assets and Liabilities - [custom_page_208_1_12]
                -> `custom_page_208` as `custom_page_name`
                -> `12` as `field_index`
                -> `1` as `subpage_index`
"""
leaf_req = {
    "method":"ajax.PageElementSettingAjax_rpc_html_kYjvPyv3_",
    "params":[
        {
            "custom_page_name": "",  # TODO
            "interface_type": "client",
            "menu_path": "",         # TODO
            "field_index": 0,
            "subpage_index": 0,      # TODO
            "element_type": "",
        }
    ],
    "id":1
}

# TODO: depends on response of `leaf_req` - `title`: `Xplan`
table1_method = "ajax.XplanElementListSettingAjax_rpc_html_WEaBDM8__"
table2_method = "ajax.XplanElementEditSettingAjax_rpc_html_HBm947gH_"
leaf_req_xtable = {
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
            "element_name": "",      # TODO, from response of `leaf_req` - `element_name`
            "render_method": "factfind"
        }
    ],
    "id": 1
}

def handle_leaf(node_id: str, menu_path: str, session: requests.sessions.Session, jison: Jison) -> str:
    custom_page_name, index = re.search('(.+)_([\d]+_[\d]+)', node_id).groups()
    subpage_index, field_index = [int(i) for i in index.split('_')]

    leaf_req.get('params')[0]['menu_path'] = menu_path
    leaf_req.get('params')[0]['custom_page_name'] = custom_page_name
    leaf_req.get('params')[0]['subpage_index'] = subpage_index
    leaf_req.get('params')[0]['field_index'] = field_index

    pprint(leaf_req)


    jison.load_json(session.post(TEST_URL, json=leaf_req, headers=interface_header).json())

    print(jison.parse())



def get_children(menu_path: str, session: requests.sessions.Session, jison: Jison) -> list:
    """
    get `children` under current `menu_path`

    then acquire `sub_children` for each child in `children`
    """
    menu_req.get('params')[0]['menu_path'] = menu_path
    jison.load_json(session.post(TEST_URL, json=menu_req, headers=interface_header).json())

    # children list for current `menu_path` acquired
    hidden_status = jison.get_multi_object('hidden')
    children_id = jison.get_multi_object('node_id')
    children_title = jison.get_multi_object('title')
    children = []

    # loop in `children`, acquire `sub_children` for each child
    for index, child_id in enumerate(children_id[:-1]):
        if hidden_status[index].get('hidden'):
            continue

        child_path = re.search('client_([0-9_\-]+)', child_id.get('node_id'))
        # normal node case (id starts with `client_xxx`)
        if child_path:
            child_path = child_path.group(1).replace('-', '/')
            sub_children = get_children(child_path, session, jison)
        # leaf case (id not starts with `client_xxx`)
        else:
            sub_children = []

        # if current child has no children (a leaf)
        if not sub_children:
            leaf_type = handle_leaf(child_id.get('node_id'), menu_path, session, jison)
            if leaf_type:
                children.append({
                    'id': child_id.get('node_id'),
                    'text': children_title[index].get('title'),
                    'type': leaf_type
                })
            else:
                children.append({
                    'id': child_id.get('node_id'),
                    'text': children_title[index].get('title'),
                    'type': 'other'
                })

        # else, append `sub_children` to current child
        else:
            children.append({
                'id': child_id.get('node_id'),
                'text': children_title[index].get('title'),
                'type': 'root',
                'children': sub_children
            })

    return children


def test(password: str):
    jison = Jison()
    BASE = 'https://ytml.xplan.iress.com.au'
    URL_LOGIN = 'https://ytml.xplan.iress.com.au/home'
    URL_HOME = 'https://ytml.xplan.iress.com.au/dashboard/mainhtml'
    URL_LIST = 'https://ytml.xplan.iress.com.au/ufield/list'
    URL_WALKER = ''.join(['https://ytml.xplan.iress.com.au/ufield/list_iframe?group=', '{}'])
    URL_LOGOUT = 'https://ytml.xplan.iress.com.au/home/logoff?'


    with requests.session() as session:
        payload = {
            "userid": 'ytml2',
            "passwd": password,
            "rolename": "User",
            "redirecturl": ''
        }
        header = {
            'referer': URL_LOGIN
        }
        # send POST to login page
        session.post(URL_LOGIN, data=payload, headers=header)
        r = session.get(URL_HOME)


        if re.search(r'permission_error|Login for User', r.text): 
            # login failed
            raise Exception('Currently there is another user using this XPLAN account.')

        # jison.load_json(session.post(TEST_URL, json=menu_req, headers=interface_header).json())
        #
        # hidden_status = jison.get_multi_object('hidden')
        # top_menu_id = jison.get_multi_object('node_id')
        # top_menu_title = jison.get_multi_object('title')
        #
        # menu = []
        # for index, _id in enumerate(top_menu_id[:-1]):
        #     if hidden_status[index].get('hidden'):
        #         continue
        #
        #     menu.append({
        #         'id': _id.get('node_id'),
        #         'text': top_menu_title[index].get('title'),
        #         'type': 'root',
        #         'children': []
        #     })
        #
        # for node in menu:
        #     menu_path = re.search('client_([0-9_\-]+)', node.get('id'))
        #     if menu_path:
        #         menu_path = menu_path.group(1).replace('-', '/')
        #         node['children'] = get_children(menu_path, session, jison)
        #
        # pprint(menu)
        #
        #
        # print(json.dumps(session.post(TEST_URL, json=menu_req, headers=interface_header).json()))

        handle_leaf('custom_page_208_2_8', '52/3/2', session, jison)



        session.get(URL_LOGOUT)


if __name__ == '__main__':
    password = 'Passw0rdOCT'
    test(password)
