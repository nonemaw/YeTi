import hashlib
from datetime import datetime
from werkzeug.security import generate_password_hash
from flask import current_app, request
from flask_login import UserMixin, AnonymousUserMixin, current_user
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from bson import ObjectId

from app import login_manager
from common.db import mongo_connect, MongoConfig, create_dict_path
from common.meta import Meta
from common.general import merge_dict
from fuzzier.jison import Jison


# Note: all DB model class are using legacy PyMongo method `insert()` to create
# new document into collection, rather than `insert_one()`, as `insert()` will
# return new `_id` directly


class Group:
    def __init__(self, var: str, name: str):
        self.var = var
        self.name = name

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f'<Group {self.var} - {self.name}>'

    def new(self, specific_db = None) -> str:
        if specific_db:
            db = specific_db
        else:
            db = current_user.db

        document = {
            'var': self.var,
            'name': self.name,
            'sub_groups': []
        }
        legacy = db.Group.find_one({'var': self.var})
        if not legacy:
            return str(db.Group.insert(document))
        else:
            return str(legacy.get('_id'))

    @staticmethod
    def update_doc(locate: dict, update: dict, specific_db = None):
        if specific_db:
            db = specific_db
        else:
            db = current_user.db

        db.Group.update_one(locate, {'$set': update})

    @staticmethod
    def delete_doc(locate: dict, specific_db = None):
        if specific_db:
            db = specific_db
        else:
            db = current_user.db

        to_be_deleted = db.Group.find_one(locate)
        if to_be_deleted:
            sub_groups = to_be_deleted.get('sub_groups')
            db.Group.delete_one(locate)

            for sub_group_id in sub_groups:
                try:
                    SubGroup.delete_doc({'_id': ObjectId(sub_group_id)})
                except:
                    pass

    @staticmethod
    def search(locate: dict, specific_db = None) -> dict:
        if specific_db:
            db = specific_db
        else:
            db = current_user.db

        return db.Group.find_one(locate)


class SubGroup:
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f'<SubGroup {self.name}>'

    def new(self, specific_db = None) -> str:
        if specific_db:
            db = specific_db
        else:
            db = current_user.db

        document = {
            'name': self.name,
            'variables': []
        }
        legacy = db.Variables.find_one({'name': self.name})
        if not legacy:
            return str(db.SubGroup.insert(document))
        else:
            return str(legacy.get('_id'))

    @staticmethod
    def update_doc(locate: dict, update: dict, specific_db = None):
        if specific_db:
            db = specific_db
        else:
            db = current_user.db

        db.SubGroup.update_one(locate, {'$set': update})

    @staticmethod
    def delete_doc(locate: dict, specific_db = None):
        if specific_db:
            db = specific_db
        else:
            db = current_user.db

        db.SubGroup.delete_one(locate)

    @staticmethod
    def search(locate: dict, specific_db = None) -> dict:
        if specific_db:
            db = specific_db
        else:
            db = current_user.db

        return db.SubGroup.find_one(locate)


class InterfaceNode:
    def __init__(self, node: dict):
        self.node = node

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f'<InterfaceNode {self.node.get("id")} {self.node.get("text")}>'

    def get_id(self, depth: int = 0) -> tuple:
        """
        return child id and MongoDB query syntax based on depth
        """
        if depth:
            node_id = ''
            query_base = ''
            try:
                node_dict = self.node
                while depth:
                    node_dict = node_dict.get('children')[0]
                    node_id = node_dict.get('id')
                    query_base = f'children.{query_base}'
                    depth -= 1

                return f'{query_base}id', node_id

            except:
                return '', ''
        return '', ''

    def new(self, force: bool = False, depth: int = 0, specific_db = None) -> str:
        """
        normally when `new()` is called and a legacy data already exists, it
        does nothing but just return legacy data's serial number

        when option `force` is enabled, the `new()` method will try to update
        information to the data if legacy data already exists

        depth is used for controlling update depth, e.g. if I get following
        data with depth is 3:
            depth = 0     depth = 1     depth = 2     depth = 3
            {'children': [{'children': [{'children': [{'id': 'custom_page_207_0_5',
                                                       'text': 'Trust Name',
                                                       'type': 'variable'}],
                                         'id': 'client_52-2-0',
                                         'text': 'Trust Details',
                                         'type': 'root'}],
                           'id': 'client_52-2',
                           'text': 'FMD Trust SoA Wizard',
                           'type': 'root'}],
             'id': 'client_52',
             'text': 'FMD SoA Wizard',
             'type': 'root'}

        then I ONLY update/insert the content of the leaf node on depth = 3
        (when depth = 0 is the normal case)
        """
        if specific_db:
            db = specific_db
        else:
            db = current_user.db

        # TODO: FIX ME, too buggy
        legacy = db.InterfaceNode.find_one(
            {'id': self.node.get('id')})
        if not legacy:
            return str(db.InterfaceNode.insert(self.node))

        elif force and not depth:
            pushed_list = [x for x in self.node.get('children')
                           if x.get('text') not in
                           [l.get('text') for l in legacy.get('children')]
                           ]
            # `pushed_list` is a list of {child} which are not in legacy children
            # is `pushed_list` then append each {child} to legacy's children list
            if pushed_list:
                db.InterfaceNode.update_one(
                    {'id': self.node.get('id')},
                    {
                        '$set': {
                            'text': self.node.get('text'),
                            'type': self.node.get('type')},
                        '$push': {
                            'children': {'$each': pushed_list}}
                    })
            # if `pushed_list` is empty, just make current children to overwrite
            # legacy's children
            else:
                db.InterfaceNode.update_one(
                    {'id': self.node.get('id')},
                    {'$set': {
                        'text': self.node.get('text'),
                        'type': self.node.get('type'),
                        'children': self.node.get('children')
                    }})

        elif depth:
            import re
            query, child_node_id = self.get_id(depth)

            # child node is a root node
            if re.search('^client_[0-9]+', child_node_id):
                db.InterfaceNode.update_one(
                    {
                        'id': self.node.get('id'),
                        query: child_node_id
                    },
                    {'$set': {

                    }}
                )
            # child node is a leaf
            else:
                pass

        return str(legacy.get('_id'))

    @staticmethod
    def update_doc(locate: dict, update: dict, specific_db = None):
        if specific_db:
            db = specific_db
        else:
            db = current_user.db

        db.InterfaceNode.update_one(locate, {'$set': update})

    @staticmethod
    def search(locate: dict, specific_db = None) -> dict:
        if specific_db:
            db = specific_db
        else:
            db = current_user.db

        return db.InterfaceNode.find_one(locate)


class InterfaceLeafPage:
    def __init__(self, id: str, text: str, leaf_type: str, menu_path: str,
                 page: dict):
        self.id = id
        self.text = text
        self.leaf_type = leaf_type
        self.menu_path = menu_path
        self.page = page

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f'<InterfaceLeafPage {self.id}>'

    def new(self, force: bool = False, specific_db = None) -> str:
        if specific_db:
            db = specific_db
        else:
            db = current_user.db

        document = {
            'id': self.id,
            'text': self.text,
            'leaf_type': self.leaf_type,
            'menu_path': self.menu_path,
            'page': self.page
        }
        legacy = db.InterfaceLeafPage.find_one({'id': self.id})
        if not legacy:
            return str(db.InterfaceLeafPage.insert(document))
        elif force:
            db.InterfaceLeafPage.update_one(
                {'id': self.id},
                {'$set': {
                    'text': self.text,
                    'leaf_type': self.leaf_type,
                    'menu_path': self.menu_path,
                    'page': self.page
                }})

            return str(legacy.get('_id'))
        return str(legacy.get('_id'))

    @staticmethod
    def update_doc(locate: dict, update: dict, specific_db = None):
        if specific_db:
            db = specific_db
        else:
            db = current_user.db

        db.InterfaceLeafPage.update_one(locate, {'$set': update})

    @staticmethod
    def search(locate: dict, specific_db = None) -> dict:
        if specific_db:
            db = specific_db
        else:
            db = current_user.db

        return db.InterfaceLeafPage.find_one(locate)


class AnonymousUser(AnonymousUserMixin):
    """
    add permission check method to the default AnonymousUse (no login)
    """

    def can(self, permission):
        return False

    def is_administrator(self):
        return False


class Permission:
    ACCESS = 0x01
    ADMIN = 0x80


class Role:
    def __init__(self, role: dict):
        self.type = role.get('type')
        self.permission = role.get('permission')
        self.default = role.get('default')

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f'<Role {self.type}>'

    def add_role(self):
        document = {
            'type': self.type,
            'permission': self.permission,
            'default': self.default
        }
        Meta.db.Role.insert(document)

    @staticmethod
    def insert_roles():
        roles = [
            {'type': 'ACCESS',
             'permission': Permission.ACCESS,
             'default': True},
            {'type': 'ADMIN',
             'permission': 0xff,
             'default': False}]
        for role in roles:
            if not Meta.db.Role.find_one({'type': role.get('type')}):
                Meta.db.Role.insert(role)


class User:
    """
    a base class for constructing user object
    """

    def __init__(self, email: str, username: str, password: str,
                 location: str):
        self.email = email
        self.username = username
        self.password = generate_password_hash(password)
        self.location = location
        self.avatar_hash = None
        if self.email == current_app.config['SITE_ADMIN']:
            self.role = Meta.db.Role.find_one(
                {'permission': 0xff}).get('type')
        else:
            self.role = Meta.db.Role.find_one(
                {'default': True}).get('type')
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(
                self.email.encode('utf-8') +
                str(datetime.utcnow()).encode('utf-8')).hexdigest()

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f'<User {self.username}>'

    def new(self) -> str:
        document = {
            'email': self.email,
            'username': self.username,
            'password': self.password,  # store hash result
            'is_confirmed': True,  # FIXME: for test
            'role': self.role,
            'name': '',
            'location': self.location,
            'about_me': '',
            'avatar_hash': self.avatar_hash,
            'member_since': datetime.utcnow(),
            'last_login': datetime.utcnow(),
            'company': ''
        }
        return str(Meta.db.User.insert(document))

    @staticmethod
    def update_doc(locate: dict, update: dict):
        Meta.db.User.update_one(locate, {'$set': update})

    @staticmethod
    def search(locate: dict) -> dict:
        return Meta.db.User.find_one(locate)

    @staticmethod
    def save_misc(locate: dict, key: str, data: dict):
        # save non-statistic data
        if key != 'statistic':
            Meta.db.User.update_one(locate, {'$set': {key: data}})
        # save statistic data
        else:
            legacy = User.get_misc({'_id': ObjectId(current_user.id)},
                                   'statistic')
            # no legacy statistic data
            if legacy is None:
                Meta.db.User.update_one(locate, {'$set': {key: data}})
            # has existing statistic data
            else:
                new_search_history = merge_dict(legacy.get('search_history'),
                                                data.get('search_history'))
                Meta.db.User.update_one(
                    locate,
                    {
                        # '$push': {
                        #     'statistic.search_history': {
                        #         '$each': data.get('search_history')
                        #     }
                        # },
                        '$set': {
                            'statistic.search_history': new_search_history,
                            'statistic.search_count': data.get('search_count') + legacy.get('search_count'),
                            'statistic.judge_count': data.get('judge_count') + legacy.get('judge_count'),
                            'statistic.failed_count': data.get('failed_count') + legacy.get('failed_count'),
                            'statistic.success_count': data.get('success_count') + legacy.get('success_count')
                        }
                    }
                )

    @staticmethod
    def get_misc(locate: dict, key: str):
        return Meta.db.User.find_one(locate).get(key)

    @staticmethod
    def login(locate: dict, logged):
        Meta.db.User.update_one(locate, {'$set': {'logged': logged}})


class UserUtl(UserMixin):
    """
    a utility class based from UserMixin for Flask 'current_user', operating
    current logged user utilities on a global level
    """

    def __init__(self, user: dict):
        self.id = str(user.get('_id'))
        self.email = user.get('email')
        self.username = user.get('username')
        self.password = user.get('password')  # store hash result
        self.is_confirmed = user.get('is_confirmed')
        self.role = Role(Meta.db.Role.find_one({'type': user.get('role')}))
        self.name = user.get('name')
        self.location = user.get('location')
        self.about_me = user.get('about_me')
        self.avatar_hash = user.get('avatar_hash')
        self.last_login = user.get('last_login')
        self.member_since = user.get('member_since')
        self.company = user.get('company')
        self.db = Meta.db if self.company == MongoConfig.HOME else \
            mongo_connect(self.company)
        try:
            self.jison = Jison(file_name=user.get('company'))
        except:
            # if user is login into an empty company (no database)
            self.jison = Jison()

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f'<CurrentUser {self.username}>'

    def get_id(self):
        """
        used by Flask's login_user() to retrieve logged user id, for a global
        session usage. Callback function use id to load_user() for returning
        the global 'current_user'

        https://flask-login.readthedocs.io/en/latest/
        """
        return self.id

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        return '{u}/{h}?s={s}&d={d}&r={r}'.format(u=url, h=self.avatar_hash,
                                                  s=size, d=default,
                                                  r=rating)

    def can(self, permission):
        return self.role is not None and (self.role.permission & permission) \
                                         == permission

    def is_administrator(self):
        return self.can(Permission.ADMIN)

    def ping(self):
        Meta.db.User.update_one({'email': self.email},
                                {'$set': {
                                    'last_login': datetime.utcnow()}})

    def generate_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'ID': self.id})
        # token == s.dumps(data)
        # data == s.loads(token)

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'ID': self.id, 'new_email': new_email})


class Snippet():
    def __init__(self, group: str, scenario: str, code: str):
        self.group = group
        self.scenario = scenario
        self.code = code

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f'<Snippet Scenario {self.scenario}>'

    def new(self) -> tuple:
        # check duplication, OK if only group name or scenario name is same
        duplicated = False
        group_dict = Meta.db.SnippetGroup.find_one({'name': self.group})
        if group_dict:
            # group existing, check scenario name
            old_scenario_id_list = group_dict.get('scenarios')
            for id in old_scenario_id_list:
                if Meta.db.SnippetScenario.find_one(
                        {'_id': ObjectId(id)}).get('name') == self.scenario:
                    # both group and scenario are duplicated, you are in big
                    # trouble, skipped
                    duplicated = True
                    break

        if not duplicated:
            # insert new scenario
            document = {
                'name': self.scenario,
                'group': self.group,
                'code': self.code
            }
            scenario_id = str(Meta.db.SnippetScenario.insert(document))

            if group_dict:
                # update new scenario id into existing group
                group_id = str(group_dict.get('_id'))
                Meta.db.SnippetGroup.update_one({'name': self.group},
                                                {'$push': {
                                                    'scenarios': scenario_id}})
            else:
                # insert new group for the new scenario
                document = {
                    'name': self.group,
                    'scenarios': [scenario_id]
                }
                group_id = str(Meta.db.SnippetGroup.insert(document))
            return group_id, scenario_id
        else:
            return None, None

    @staticmethod
    def new_group(doc: dict) -> str:
        return str(Meta.db.SnippetGroup.insert(doc))

    @staticmethod
    def get_group_cursor(locate: dict, s_condition: list = None):
        if s_condition and isinstance(s_condition, list):
            return Meta.db.SnippetGroup.find(locate).sort(s_condition)
        return Meta.db.SnippetGroup.find(locate)

    @staticmethod
    def get_scenario_cursor(locate: dict, s_condition: list = None):
        if s_condition and isinstance(s_condition, list):
            return Meta.db.SnippetScenario.find(locate).sort(s_condition)
        return Meta.db.SnippetScenario.find(locate)

    @staticmethod
    def update_doc_group(locate: dict, update: dict):
        Meta.db.SnippetGroup.update_one(locate, {'$set': update})

    @staticmethod
    def update_doc_scenario(locate: dict, update: dict):
        Meta.db.SnippetScenario.update_one(locate, {'$set': update})

    @staticmethod
    def delete_doc_group(locate: dict):
        Meta.db.SnippetGroup.delete_one(locate)

    @staticmethod
    def delete_doc_scenario(locate: dict):
        Meta.db.SnippetScenario.delete_one(locate)

    @staticmethod
    def search_group(locate: dict) -> dict:
        return Meta.db.SnippetGroup.find_one(locate)

    @staticmethod
    def search_scenario(locate: dict) -> dict:
        return Meta.db.SnippetScenario.find_one(locate)


class Ticket():
    def __init__(self, ticket: str, description: str):
        self.ticket = ticket
        self.description = description

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f'<Ticket {self.ticket}>'

    def new(self) -> str:
        document = {
            'ticket': self.ticket,
            'description': self.ticket,
            'timestamp': datetime.utcnow(),
            'solved_timestamp': None,
            'solved': False
        }
        return str(Meta.db.Ticket.insert(document))


login_manager.anonymous_user = AnonymousUser
"""
It is not mandator but there are permission test like is_administrator() and
can() in templates which are not defined to anonymous sessions (without login)
and Errors will be raised.

In class AnonymousUser(AnonymousUserMixin) these two permission methods are
defined and by setting login_manager.anonymous_user to class 
AnonymousUser(AnonymousUserMixin) for making those operations available.

This can be tested by just commenting this line and check the Error message
"""


@login_manager.user_loader
def load_user(user_id):
    """
    This callback is used to reload the user object from the user ID stored
    in the session (as current_user)
    """
    return UserUtl(Meta.db.User.find_one({'_id': ObjectId(user_id)}))
