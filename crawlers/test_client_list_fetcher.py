widget = {"method":"dashboard.getWidgetOutput","params":[{"widgetid":1000126,"width":568,"height":-1,"sizing":1}],"id":1}

import requests
import re
from pprint import pprint as pp
from fuzzier.jison import Jison
import urllib3
from pprint import pprint
from bs4 import BeautifulSoup


company = 'ytml'
username = 'ytml2'
password = 'Passw0rdOCT'
sample_client = 'Duran Wendy'

jison = Jison()

URL_SOURCE = f'https://{company.lower()}.xplan.iress.com.au/RPC2/'
URL_SEARCH = f'https://{company.lower()}.xplan.iress.com.au/factfind/quicksearch?role=client&q={{}}'
URL_LIST = f'https://{company.lower()}.xplan.iress.com.au/factfind/search/list_entity?async=3'


links = {}
client = {}
partner = {}
joint = {}





with requests.session() as session:
    try:
        payload = {
            "userid": username,
            "passwd": password,
            "rolename": "User",
            "redirecturl": ''
        }
        ips_post = {"method":"portfolio.getMarketValueReport","params":[2846,"V0I1E2W3_A4L5L6","prod_name",False],"id":1}

        # send POST to login page, check login status
        session.post(f'https://{company.lower()}.xplan.iress.com.au/home',
                     data=payload)
        r = session.get(
            f'https://{company.lower()}.xplan.iress.com.au/dashboard/mainhtml')

        if re.search(r'permission_error|Login for User', r.text):
            raise Exception(
                'Currently there is another user using this XPLAN account.')


        session.get(URL_SEARCH.format('+'.join(sample_client.split())))
        soup = BeautifulSoup(session.get(URL_LIST).text, 'lxml')
        client_id, client_name = re.search('\(([0-9]+)\).+>([a-zA-Z, \'\"]+)<', str(soup.select('.list2 td:nth-of-type(3) a')[0])).groups()
        client_name = ''.join(client_name.split(','))
        client_url = f'https://{company.lower()}.xplan.iress.com.au/factfind/view/{client_id}?role=client'

        soup = BeautifulSoup(sample, 'lxml')
        for li in soup.select('#mf-navigatorbox > div > ul > li > div'):









        # for tr in soup.select('tr'):
        #     tds = tr.select('td')
        #     print (str(tds))
        #
        #     a = re.search('"key">(.+)</td>.+>(.+)<input', str(tr)).groups()
        #     print(a)
        #
        #     print('##############################')










        session.get(f'https://{company}.xplan.iress.com.au/home/logoff?')
    except Exception as e:
        print(e)
        session.get(f'https://{company}.xplan.iress.com.au/home/logoff?')

