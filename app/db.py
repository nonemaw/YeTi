
import requests
from pymongo import MongoClient
from common import meta


class MongoCfg:
    HOST = 'localhost'
    PORT = 27017
    SUPER = 'superroot'
    USER = 'root'
    PWD = 'admin123'


try:
    requests.session().get(f'https://{meta.company.lower()}.xplan.iress.com.au', headers=dict(referer=f'https://{meta.company.lower()}.xplan.iress.com.au'))
except:
    print(f'Company name \"{meta.company}\" invalid, no such XPLAN site for this company.')
else:
    client = MongoClient(MongoCfg.HOST, MongoCfg.PORT)


def mongo_connect(client, company:str):
    if company.upper() == 'YTML':
        db = client['YETI']
        # db.authenticate(MongoCfg.USER, MongoCfg.PWD, source='YETI')
    else:
        db = client['YETI_' + company.upper()]
        # db.authenticate(MongoCfg.USER, MongoCfg.PWD, source='YETI_'+company.upper())
    return db