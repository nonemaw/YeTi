
"""
login into a specified XPLAN site, fetch all data to local database
"""
import requests
import re
from selenium import webdriver


USERNAME = 'ytmladmin'
PASSWORD = 'Passw0rdOCT'
URL_LOGIN = 'https://ytml.xplan.iress.com.au/home'
URL_LOGOUT = 'https://ytml.xplan.iress.com.au/home/logoff?'
URL_INTERFACE = 'https://ytml.xplan.iress.com.au/factfind/edit_interface'
driver = webdriver.Ie()


with requests.session() as session:
    try:
        # login payload
        payload = {
            "userid": USERNAME,
            "passwd": PASSWORD,
            "rolename": "User",
            "redirecturl": ''
        }
        # send POST to login page
        session.post(URL_LOGIN, data=payload, headers=dict(referer=URL_LOGIN))
        # try to get main list page content
        # fields = session.get(URL_INTERFACE, headers = dict(referer = URL_INTERFACE))
        fields = driver.get(URL_INTERFACE)

        if re.search(r'permission_error', fields.text):
            # login failed
            print('Currently there is another user using this XPLAN account.')
        else:


            print(fields.text)






        # logout
        session.get(URL_LOGOUT)

    except KeyboardInterrupt:
        session.get(URL_LOGOUT)

