
import requests
from pymongo import MongoClient


class MongoCfg:
    HOST = 'localhost'
    PORT = 27017
    SUPER = 'superroot'
    USER = 'root'
    PWD = 'admin123'


def mongo_connect(company:str):
    try:
        requests.session().get("https://{}.xplan.iress.com.au".format(company.lower()), headers=dict(referer="https://{}.xplan.iress.com.au".format(company.lower())))
    except:
        print('Company name \"{}\" invalid, no such XPLAN site for this company.'.format(company))
        return None
    else:
        client = MongoClient(MongoCfg.HOST)
        if company.upper() == 'YTML':
            db = client['YETI']
            # db.authenticate(MongoCfg.USER, MongoCfg.PWD, source='YETI')
        else:
            db = client['YETI_' + company.upper()]
            # db.authenticate(MongoCfg.USER, MongoCfg.PWD, source='YETI_'+company.upper())
        return db
