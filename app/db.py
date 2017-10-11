
import requests
from pymongo import MongoClient
from common import global_vars


class MongoCfg:
    HOST = 'localhost'
    PORT = 27017
    SUPER = 'superroot'
    USER = 'root'
    PWD = 'admin123'


try:
    requests.session().get("https://{}.xplan.iress.com.au".format(global_vars.company.lower()), headers=dict(referer="https://{}.xplan.iress.com.au".format(global_vars.company.lower())))
except:
    print('Company name \"{}\" invalid, no such XPLAN site for this company.'.format(global_vars.company))
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