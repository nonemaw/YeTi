
import requests
import re

url = "https://ytml.xplan.iress.com.au/ufield/edit/entity/advice_dp_cont_funds_from"
url2 = "https://ytml.xplan.iress.com.au/ufield/list_options"
test = {"method":"response.report_loadtime","params":[1234,"/ufield/edit/entity/adviser_type"],"id":1}

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






session = login('ytml2', 'Passw0rdOCT', 'ytml')
prc2 = session.post('https://ytml.xplan.iress.com.au/RPC2/', json=test)
print(prc2)



# text = session.get(url2).text
#
# print(text)
#
# from bs4 import BeautifulSoup
# soup = BeautifulSoup(text, 'lxml')
# option_table = soup.find({'id': 'list_table'})
#
#





logout(session, 'ytml')
