
import requests
import re
import os

def test(password: str):
    BASE = 'https://ytml.xplan.iress.com.au'
    URL_LOGIN = 'https://ytml.xplan.iress.com.au/home'
    URL_HOME = 'https://ytml.xplan.iress.com.au/dashboard/mainhtml'
    URL_LIST = 'https://ytml.xplan.iress.com.au/ufield/list'
    URL_WALKER = ''.join(['https://ytml.xplan.iress.com.au/ufield/list_iframe?group=', '{}'])
    URL_LOGOUT = 'https://ytml.xplan.iress.com.au/home/logoff?'

    TEST_URL = 'https://ytml.xplan.iress.com.au/RPC2/'

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

        cookie = session.cookies.get_dict()
        for key in cookie:
            c1 = key
            c2 = cookie.get(key)


        test_data = {"interface_type":"client","menu_path":"1"}
        test_header = {
            'Accept': 'text/plain',
            'Accept-Encoding': 'gzip',
            'Content-Type': 'application/json',
            'referer': 'https://ytml.xplan.iress.com.au/factfind/edit_interface',
            'cookie': f'{c1}={c2}'
        }

        import json
        response = session.post(TEST_URL, json=test_data, headers=test_header)

        print(response.json())












        session.get(URL_LOGOUT)

if __name__ == '__main__':
    password = input('password: ')
    password = 'Passw0rdOCT'
    test(password)