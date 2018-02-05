import requests
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
    ValidationError, SelectField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from app.models import User
from common.db import MongoConfig

cities = [('New South Wales', ' New South Wales'),
          ('Australian Capital Territory', ' Australian Capital Territory'),
          ('Northern Territory', ' Northern Territory'),
          ('Queensland', ' Queensland'),
          ('South Australia', ' South Australia'),
          ('Tasmania', ' Tasmania'), ('Victoria', ' Victoria'),
          ('Western Australia', ' Western Australia')]


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    company = StringField('Company for Access (Case Insensitive)',
                          default=MongoConfig.HOME,
                          validators=[DataRequired()])
    remember_me = BooleanField(' Remember Me')
    submit = SubmitField('Login')

    def validate_company(self, field):
        """
        validate company name and initialize Meta class if validation passed
        """
        try:
            requests.session().get(
                f'https://{field.data.lower()}.xplan.iress.com.au',
                headers=dict(
                    referer=f'https://{field.data.lower()}.xplan.iress.com.au'
                )
            )
        except:
            raise ValidationError(
                f'Company name \"{field.data}\" invalid, no such XPLAN site.')


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

    def validate_email(self, field):
        if User.search({'email': field.data}):
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if User.search({'username': field.data}):
            raise ValidationError('Username already existed.')


class ChangeEmailForm(FlaskForm):
    email = StringField('Your New Email', validators=[DataRequired(),
                                                      Length(1, 64),
                                                      Email()])
    password = PasswordField('Your Current Password',
                             validators=[DataRequired()])
    submit = SubmitField('Update Email Address')

    def validate_email(self, field):
        if User.search({'email': field.data}):
            raise ValidationError('Email already registered.')


class ChangePasswordForm(FlaskForm):
    password = PasswordField('Your Current Password',
                             validators=[DataRequired()])
    password_new = PasswordField('Your New Password',
                                 validators=[DataRequired(),
                                             EqualTo('password_new2',
                                                     message='Password does not match')])
    password_new2 = PasswordField('Confirm New Password',
                                  validators=[DataRequired()])
    submit = SubmitField('Update Password')
