import requests
import re
from pprint import pprint as pp
from fuzzier.jison import Jison


company = 'ytml'
username = 'ytmladmin'
password = 'Passw0rdOCT'
jison = Jison()
URL_SOURCE = f'https://{company.lower()}.xplan.iress.com.au/RPC2/'
interface_header = {
    'Content-Type': 'application/json',
    'referer': f'https://{company.lower()}.xplan.iress.com.au/portfolio/list_position',
}

with requests.session() as session:
    payload = {
        "userid": username,
        "passwd": password,
        "rolename": "User",
        "redirecturl": ''
    }
    ips_post = {"method":"portfolio.getMarketValueReport","params":[2846,"V0I1E2W3_A4L5L6","prod_name",False],"id":1}

    # send POST to login page, check login status
    session.post(f'https://{company}.xplan.iress.com.au/home',
                 data=payload)
    r = session.get(
        f'https://{company}.xplan.iress.com.au/dashboard/mainhtml')

    if re.search(r'permission_error|Login for User', r.text):
        raise Exception(
            'Currently there is another user using this XPLAN account.')

    jison.load(session.post(URL_SOURCE,
                            json=ips_post,
                            headers=interface_header).json())


    pp(jison.parse())


    session.get(f'https://{company}.xplan.iress.com.au/home/logoff?')

