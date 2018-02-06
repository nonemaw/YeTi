from pymongo import MongoClient
from datetime import datetime


class MongoConfig:
    HOME = 'YTML'
    HOST = 'localhost'
    PORT = 27017
    SUPER = 'superroot'
    USER = 'root'
    PWD = 'admin123'


def mongo_connect(db_name: str,):
    client = MongoClient(MongoConfig.HOST, MongoConfig.PORT)
    if db_name.upper() == MongoConfig.HOME:
        db = client['YETI']
        # db.authenticate(MongoCfg.USER, MongoCfg.PWD, source='YETI')
    else:
        db = client[f'YETI_{db_name.upper()}']
        # db.authenticate(MongoCfg.USER, MongoCfg.PWD, source='YETI_'+company.upper())

    return db


def build_timestamp(old_time=None):
    time = datetime.now()
    if old_time is None:
        return time

    str_gap_time = []

    if isinstance(old_time, datetime):
        diff = time - old_time
        days, seconds = diff.days, diff.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60

        if days:
            if days > 1:
                str_gap_time.append(f'{days} Days')
            else:
                str_gap_time.append('1 Day')
            if 24 > hours > 1:
                str_gap_time.append(f'{hours} Hours')
            elif hours == 24:
                str_gap_time.append('0 Hour')
            else:
                str_gap_time.append('1 Hour')
            if 60 > minutes > 1:
                str_gap_time.append(f'{minutes} Minutes ago')
            elif minutes == 60:
                str_gap_time.append('0 Minute ago')
            else:
                str_gap_time.append('1 Minute ago')
        elif hours:
            if hours > 1:
                str_gap_time.append(f'{hours} Hours')
            else:
                str_gap_time.append('1 Hour')
            if 60 > minutes > 1:
                str_gap_time.append(f'{minutes} Minutes ago')
            elif minutes == 60:
                str_gap_time.append('0 Minute ago')
            else:
                str_gap_time.append('1 Minute ago')
        elif minutes:
            if minutes > 1:
                str_gap_time.append(f'{minutes} Minutes ago')
            else:
                str_gap_time.append('1 Minute')
        if not days and not hours and not minutes:
            str_gap_time.append('A few seconds ago')

        return ' '.join(str_gap_time)


def build_str_time(time) -> str:
    if isinstance(time, datetime):
        return time.strftime("%d/%m/%Y %H:%M")


def create_dict_path(data: dict, path_dict: dict = None) -> dict:
    """
    create a mongodb update path for a dictionary
    """
    if path_dict is None:
        path_dict = {}
    for key, value in data.items():
        if not isinstance(value, dict):
            path_dict[key] = value
            continue
        for _key, _value in value.items():
            create_dict_path({f'{key}.{_key}': _value}, path_dict)

    return path_dict


def empty_collection(db, collection, force: bool = False) -> bool:
    """
    empty collection but keep `timestamp`
    """
    try:
        # drop collection
        if force:
            if isinstance(collection, str):
                db.drop_collection(collection)
            elif isinstance(collection, list):
                for c in collection:
                    db.drop_collection(c)
        # empty collection
        else:
            if isinstance(collection, str):
                db[collection].delete_many({
                    'type': {'$ne': '_timestamp'}
                })
            elif isinstance(collection, list):
                for c in collection:
                    db[c].delete_many({
                        'type': {'$ne': '_timestamp'}
                    })
    except:
        return False

    return True


def drop_db(db_name) -> bool:
    try:
        with MongoClient(MongoConfig.HOST, MongoConfig.PORT) as client:
            client.drop_database(db_name)
            return True
    except:
        return False


def create_timestamp(db, collection) -> tuple:
    """
    add `timestamp` for new collection
    """
    try:
        now = build_timestamp()

        if isinstance(collection, str):
            db[collection].insert_one({
                'type': '_timestamp',
                'creation': now,
                'modification': now
            })
        elif isinstance(collection, list):
            for c in collection:
                db[c].insert_one({
                    'type': '_timestamp',
                    'creation': now,
                    'modification': now
                })
    except:
        return None, None

    return now, now


def modify_timestamp(db, collection) -> bool:
    """
    change the time of `modification`
    """
    try:
        if isinstance(collection, str):
            db[collection].update_one(
                {'type': '_timestamp'},
                {
                    '$set': {
                        'modification': build_timestamp()
                    }
                }
            )
        elif isinstance(collection, list):
            for c in collection:
                db[c].update_one(
                    {'type': '_timestamp'},
                    {
                        '$set': {
                            'modification': build_timestamp()
                        }
                    }
                )
    except:
        return False

    return True


def get_collection_timestamp(db, collection: str) -> tuple:
    """
    return collection's `timestamp`'s creation time and last modification time
    """
    try:
        time_dict = db[collection].find_one({'type': '_timestamp'})
        if time_dict is None:
            time1, time2 = create_timestamp(db, collection)
        else:
            time1, time2 = time_dict.get('creation'), time_dict.get(
                'modification')

        return build_str_time(time1), build_timestamp(time2)

    except:
        return None, None


def acquire_db_summary(collection_keywords: list = None):
    """
    return a list of db with collections and timestamps
    """
    with MongoClient(MongoConfig.HOST, MongoConfig.PORT) as client:
        import re

        dbs = client.database_names()
        db_list = []
        collection_dict = {}
        for index, db in enumerate(dbs):
            if 'yeti' in db.lower():
                if collection_keywords:
                    collections = [c for c in client[db].collection_names()
                                   if any(key in c for key in collection_keywords)]
                else:
                    collections = client[db].collection_names()

                for c in collections:
                    collection_dict[c] = get_collection_timestamp(client[db], c)

                if '_' in db:
                    db_list.append({re.sub('YETI_', '', db): collection_dict})
                else:
                    db_list.append({MongoConfig.HOME: collection_dict})
                collection_dict = {}

    return db_list
