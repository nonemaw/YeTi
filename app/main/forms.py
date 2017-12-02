from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, BooleanField, \
    SelectField
from wtforms.validators import Length, DataRequired, Email, Regexp, \
    ValidationError

from app.db import mongo_connect, client
from app.auth.forms import cities

roles = [('ACCESS', 'Normal User'), ('ADMIN', 'Administrator')]
db = mongo_connect(client, 'ytml')


class EditProfileForm(FlaskForm):
    name = StringField('Real Name', validators=[Length(0, 64)])
    location = SelectField('Where are you from?', choices=cities)
    about_me = TextAreaField('About Me')
    submit = SubmitField('Update')


class EditProfileAdminForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField('Username',
                           validators=[DataRequired(), Length(1, 64),
                                       Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                              'Username must start with a letter and have only letters, numbers, dots or underscores')])
    is_confirmed = BooleanField('Account Confirmed?')
    role = SelectField('Modify Role (Privilege)', choices=roles)
    name = StringField('Real Name', validators=[Length(0, 64)])
    location = SelectField('Where are you from?', choices=cities)
    about_me = TextAreaField('About Me')
    submit = SubmitField('Update')

    """
    sort in PyMongo: Collection.find().sort([('key1',1),('key2',-1), ...]).limit(<value>)
         1 for ascending sort
        -1 for descending sort
         limit() for getting first <value> documents from the sort result

    sort in MongoShell: Collection.find().sort({key1:1, key2:-1, ...}).limit(<value>)
    """

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        # self.role.choices = [(str(r.get('_id')), r.get('type')) for r in\
        #                      db.Role.find({}).sort([('type', -1)])]
        self.user = user

    def validate_email(self, field):
        user_in_db = db.User.find_one({'email': field.data})
        if user_in_db and str(user_in_db.get('_id')) != self.user.id:
            raise ValidationError('Email already registered by another user.')

    def validate_username(self, field):
        user_in_db = db.User.find_one({'username': field.data})
        if user_in_db and str(user_in_db.get('_id')) != self.user.id:
            raise ValidationError(
                'Username already registered by another user.')
