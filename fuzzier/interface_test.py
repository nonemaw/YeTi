
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

menu_req = {"method": "ajax.MenuTreeAjax_rpc_load_node_gG7QNYAS_",
            "params": [{"interface_type": "client",
                        "menu_path": ""
                        }],
            "id": 1}

# TODO: assumen my id is `custom_page_207_0_5`, under father `client_52-2-0`
leaf_req = {
    "method":"ajax.PageElementSettingAjax_rpc_html_kYjvPyv3_",
    "params":[{
        "custom_page_name":"incexp",  # TODO
        "interface_type":"client",    # TODO
        "menu_path":"",
        "is_new":0,
        "field_index":0,  # TODO
        "subpage_index":0,
        "requirement":-1,
        "wrap_title":"",
        "node_type":"page_element",
        "publishable":False,
        "is_wizard_subpage":0,
        "can_import_export":False,
        "children":[],
        "is_scenario_wizard":0,
        "has_conditions":None,
        "title":"",
        "tooltip":"",
        "entity_type_condition_active":0,
        "locales":[],
        "removable":1,
        "is_wizard":0,
        "show_top_nav":0,
        "hidden":False,
        "immutable":0,
        "editable":1,
        "has_conditions_partner_page":0,
        "node_id":"",
        "url_target":"",
        "post":"",
        "partner_page_status":"none",
        "entity_type_condition":[],
        "alternative_title":"",
        "url":"",
        "hidden_xlite":False,
        "entity_type":"client",
        "element_type":"field",
        "fieldname":"",
        "mode":"edit",
        "show_default":0,
        "entity_types":[],
        "display":"regular",
        "tree":{},
        "allow_cut":True,
        "allow_paste":True,
        "current_filters":{}
    }],
    "id":1
}

def handle_leaf(node_id: str, session: requests.sessions.Session, jison: Jison) -> str:
    pass


def get_children(menu_path: str, session: requests.sessions.Session, jison: Jison) -> list:
    menu_req.get('params')[0]['menu_path'] = menu_path
    jison.load_json(session.post(TEST_URL, json=menu_req, headers=interface_header).json())

    hidden_status = jison.get_multi_object('hidden')
    children_id = jison.get_multi_object('node_id')
    children_title = jison.get_multi_object('title')

    children = []
    father = children_id[-1]

    for index, child_id in enumerate(children_id[:-1]):
        if hidden_status[index].get('hidden'):
            continue

        sub_children = []
        child_path = re.search('client_([0-9_\-]+)', child_id.get('node_id'))
        if child_path:
            child_path = child_path.group(1).replace('-', '/')
            sub_children = get_children(child_path, session, jison)

        if not sub_children:
            leaf_type = handle_leaf(child_id.get('node_id'), session, jison)
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
            "userid": 'ytml1',
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


        print(session.post(TEST_URL, json=leaf_req, headers=interface_header).json())



        session.get(URL_LOGOUT)


if __name__ == '__main__':
    password = 'Passw0rdOCT'
    test(password)
