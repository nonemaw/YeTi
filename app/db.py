from pymongo import MongoClient


class MongoCfg:
    HOST = 'localhost'
    PORT = 27017
    SUPER = 'superroot'
    USER = 'root'
    PWD = 'admin123'


client = MongoClient(MongoCfg.HOST, MongoCfg.PORT)


def mongo_connect(client, company: str):
    if company.upper() == 'YTML':
        db = client['YETI']
        # db.authenticate(MongoCfg.USER, MongoCfg.PWD, source='YETI')
    else:
        db = client[f'YETI_{company.upper()}']
        # db.authenticate(MongoCfg.USER, MongoCfg.PWD, source='YETI_'+company.upper())
    return db
