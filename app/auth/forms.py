from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError, SelectField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo

from app.db import mongo_connect, client
from common.general import get_company_list


db = mongo_connect(client, 'ytml')
cities = [('New South Wales', 'New South Wales'),
          ('Australian Capital Territory', 'Australian Capital Territory'),
          ('Northern Territory', 'Northern Territory'),
          ('Queensland', 'Queensland'), ('South Australia', 'South Australia'),
          ('Tasmania', 'Tasmania'), ('Victoria', 'Victoria'),
          ('Western Australia', 'Western Australia')]


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    company = StringField('Company for Access (Case Insensitive)', default='ytml', validators=[DataRequired()])
    # company_username = StringField('Company\'s XPLAN Username', validators=[DataRequired()])
    # company_password = PasswordField('Company\'s XPLAN Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')


class RegForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Length(1, 64),
                                    Email()])
    username = StringField('Username',
                           validators=[DataRequired(), Length(1, 64),
                                       Regexp('^[a-zA-Z][a-zA-Z0-9_.]*$', 0,
                                              'Username must have only letters, numbers, dots or underscores')])
    password = PasswordField('Password',
                             validators=[DataRequired(), EqualTo('password2',
                                                                 message='Password does not match')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    location = SelectField('Where are you from?', choices=cities)
    submit = SubmitField('Register')

    """
    Auto-validation

    validate_xxx() is pre-defined methods in WTF_Form which used to validate
    data in form automatically. Once data is entered into the form the relating
    method will be called automatically based on field name 
    """
    def validate_email(self, field):
        if db.User.find_one({'email': field.data}):
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if db.User.find_one({'username': field.data}):
            raise ValidationError('Username already existed.')


class ChangeEmailForm(FlaskForm):
    email = StringField('Your New Email', validators=[DataRequired(),
                                                      Length(1, 64),
                                                      Email()])
    password = PasswordField('Your Current Password', validators=[DataRequired()])
    submit = SubmitField('Update Email Address')

    def validate_email(self, field):
        if db.User.find_one({'email': field.data}):
            raise ValidationError('Email already registered.')


class ChangePasswordForm(FlaskForm):
    password = PasswordField('Your Current Password', validators=[DataRequired()])
    password_new = PasswordField('Your New Password', validators=[DataRequired(), EqualTo('password_new2', message='Password does not match')])
    password_new2 = PasswordField('Confirm New Password', validators=[DataRequired()])
    submit = SubmitField('Update Password')
