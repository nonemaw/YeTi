import hashlib
from datetime import datetime
from werkzeug.security import generate_password_hash
from flask import current_app, request
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from bson import ObjectId
from app import login_manager
from common.meta import Meta


"""
Note: all DB model class are using legacy PyMongo method `insert()` to create
new document into collection, rather than `insert_one()`, as `insert()` will
return new `_id` directly but `insert_one()` returns a PyMongo insertion object
"""
class Group:
    def __init__(self, var: str, name: str):
        self.var = var
        self.name = name

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f'<Group {self.var} - {self.name}>'

    def new(self) -> str:
        document = {
            'var': self.var,
            'name': self.name,
            'sub_groups': []
        }
        legacy = Meta.db_company.Group.find_one({'var': self.var})
        if not legacy:
            return str(Meta.db_company.Group.insert(document))
        else:
            return str(legacy.get('_id'))

    @staticmethod
    def update_doc(id: str, sub_groups: list):
        Meta.db_company.Group.update_one({'_id': ObjectId(id)},
                                 {'$set': {'sub_groups': sub_groups}})

    @staticmethod
    def delete_doc(locate: dict):
        Meta.db_company.Group.delete_one(locate)

    @staticmethod
    def search(locate: dict) -> dict:
        return Meta.db_company.Group.find_one(locate)


class SubGroup:
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f'<SubGroup {self.name}>'

    def new(self) -> str:
        document = {
            'name': self.name,
            'variables': []
        }
        legacy = Meta.db_company.Variables.find_one({'name': self.name})
        if not legacy:
            return str(Meta.db_company.SubGroup.insert(document))
        else:
            return str(legacy.get('_id'))

    @staticmethod
    def update_doc(id: str, variables: list):
        Meta.db_company.SubGroup.update_one({'_id': ObjectId(id)},
                                 {'$set': {'variables': variables}})

    @staticmethod
    def delete_doc(locate: dict):
        Meta.db_company.SubGroup.delete_one(locate)

    @staticmethod
    def search(locate: dict) -> dict:
        return Meta.db_company.SubGroup.find_one(locate)


class InterfaceNode:
    def __init__(self, node: dict):
        self.node = node

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f'<InterfaceNode {self.node.get("id")} {self.node.get("text")}>'

    def new(self) -> str:
        document = self.node
        legacy = Meta.db_company.InterfaceNode.find_one({'id': self.node.get('id')})
        if not legacy:
            return str(Meta.db_company.InterfaceNode.insert(document))
        else:
            return str(legacy.get('_id'))

    @staticmethod
    def update_doc(_id: str, child: list):
        Meta.db_company.InterfaceNode.update_one({'_id': ObjectId(_id)},
                                             {'$set': {'child': child}})

    @staticmethod
    def search(locate: dict) -> dict:
        return Meta.db_company.InterfaceNode.find_one(locate)


class InterfaceLeafPage:
    def __init__(self, id: str, page: dict):
        self.id = id
        self.page = page

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f'<InterfaceLeafPage {self.id}>'

    def new(self) -> str:
        document = {
            'id': self.id,
            'page': []
        }
        legacy = Meta.db_company.InterfacePage.find_one({'id': self.id})
        if not legacy:
            return str(Meta.db_company.InterfacePage.insert(document))
        else:
            return str(legacy.get('_id'))

    @staticmethod
    def update_doc(_id: str, page: dict):
        Meta.db_company.InterfacePage.update_one({'_id': ObjectId(id)},
                                         {'$set': {'page': page}})

    @staticmethod
    def search(locate: dict) -> dict:
        return Meta.db_company.InterfacePage.find_one(locate)


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
        Meta.db_default.Role.insert(document)

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
            if not Meta.db_default.Role.find_one({'type': role.get('type')}):
                Meta.db_default.Role.insert(role)


class User:
    """
    a base class for constructing user object
    """

    def __init__(self, email: str, username: str, password: str, location: str):
        self.email = email
        self.username = username
        self.password = generate_password_hash(password)
        self.location = location
        self.avatar_hash = None
        if self.email == current_app.config['SITE_ADMIN']:
            self.role = Meta.db_default.Role.find_one({'permission': 0xff}).get('type')
        else:
            self.role = Meta.db_default.Role.find_one({'default': True}).get('type')
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(self.email.encode('utf-8') +
                                           str(datetime.utcnow()).encode(
                                               'utf-8')) \
                .hexdigest()

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
        }
        return str(Meta.db_default.User.insert(document))

    @staticmethod
    def update_doc(locate: dict, update: dict):
        Meta.db_default.User.update_one(locate, {'$set': update})

    @staticmethod
    def search(locate: dict) -> dict:
        return Meta.db_company.User.find_one(locate)


class UserUtl(UserMixin):
    """
    a utility class based from UserMixin for Flask 'current_user', operating
    current user utilities on a global level
    """
    def __init__(self, user: dict):
        """
        role: set role from string value role type to Role object, for further
        operations
        """
        self.id = str(user.get('_id'))
        self.email = user.get('email')
        self.username = user.get('username')
        self.password = user.get('password')  # store hash result
        self.is_confirmed = user.get('is_confirmed')
        self.role = Role(Meta.db_default.Role.find_one({'type': user.get('role')}))
        self.name = user.get('name')
        self.location = user.get('location')
        self.about_me = user.get('about_me')
        self.avatar_hash = user.get('avatar_hash')
        self.last_login = user.get('last_login')
        self.member_since = user.get('member_since')

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
        Meta.db_default.User.update_one({'email': self.email},
                           {'$set': {'last_login': datetime.utcnow()}})

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
        # check duplication, it's ok if only group name or scenario name is same
        duplicated = False
        group_dict = Meta.db_default.SnippetGroup.find_one({'name': self.group})
        if group_dict:
            # group existing, check scenario name
            old_scenario_id_list = group_dict.get('scenarios')
            for id in old_scenario_id_list:
                if Meta.db_default.SnippetScenario.find_one({'_id': ObjectId(id)}).get(
                        'name') == self.scenario:
                    # both group and scenario are duplicated, you are in big trouble, skipped
                    duplicated = True
                    break

        if not duplicated:
            # insert new scenario
            document = {
                'name': self.scenario,
                'group': self.group,
                'code': self.code
            }
            scenario_id = str(Meta.db_default.SnippetScenario.insert(document))

            if group_dict:
                # update new scenario id into existing group
                group_id = str(group_dict.get('_id'))
                Meta.db_default.SnippetGroup.update_one({'name': self.group}, {
                    '$push': {'scenarios': scenario_id}})
            else:
                # insert new group for the new scenario
                document = {
                    'name': self.group,
                    'scenarios': [scenario_id]
                }
                group_id = str(Meta.db_default.SnippetGroup.insert(document))
            return group_id, scenario_id
        else:
            return None, None

    @staticmethod
    def update_doc_group(locate: dict, update: dict):
        Meta.db_default.SnippetGroup.update_one(locate, {'$set': update})

    @staticmethod
    def update_doc_scenario(locate: dict, update: dict):
        Meta.db_default.SnippetScenario.update_one(locate, {'$set': update})

    @staticmethod
    def delete_doc_group(locate: dict):
        Meta.db_default.SnippetGroup.delete_one(locate)

    @staticmethod
    def delete_doc_scenario(locate: dict):
        Meta.db_default.SnippetScenario.delete_one(locate)

    @staticmethod
    def search_group(locate: dict) -> dict:
        return Meta.db_company.SnippetGroup.find_one(locate)

    @staticmethod
    def search_scenario(locate: dict) -> dict:
        return Meta.db_company.SnippetScenario.find_one(locate)


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
        return str(Meta.db_default.Ticket.insert(document))


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
    This callback is used to reload the user object from the user ID stored in the
    session (as current_user?)
    """
    user = Meta.db_default.User.find_one({'_id': ObjectId(user_id)})
    return UserUtl(user)  # this is current_user
