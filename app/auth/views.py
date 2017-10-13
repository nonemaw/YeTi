
import time
import hashlib

from flask import render_template, redirect, request, url_for, flash, current_app, abort
from flask_login import login_user, logout_user, login_required, current_user
from itsdangerous import BadSignature, TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash
from bson import ObjectId

from . import auth
from .forms import LoginForm, RegForm, ChangeEmailForm, ChangePasswordForm
from app.db import mongo_connect, client
from app.models import User, UserUtl
from common.general import send_email, verify_password
from app.decorators import admin_required

from common import global_vars
from common.crypto import AESCipher


db = mongo_connect(client, 'ytml')


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()  # if user authenticated: update last login time
        if not current_user.is_confirmed and (request.endpoint is None or
                                              request.endpoint[:5] != 'auth.'):
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """ two possible results of redirection when handling 'POST':
        1. user is accessing unauthorized URL: flask_login will store former
           URL and keep it in dictionary 'request.args' with key 'next'
        2. if 'next' key is not existed in 'request.args' (which means user is
           accessing authorized URL), just display 'main.index' directly
    """
    form = LoginForm()
    if form.validate_on_submit():
        user_dict = db.User.find_one({'email': form.email.data})
        global_vars.company = form.company.data
        # global_vars.crypto = AESCipher()
        # global_vars.company_username = form.company_username.data
        # global_vars.company_password = global_vars.crypto.encrypt(form.company_password.data)
        # print(global_vars.company_password)
        if user_dict is not None and verify_password(user_dict.get('password'), form.password.data):
            # convert 'user_dict' to UserLogin(UserMixin) as 'current_user'
            user = UserUtl(user_dict)
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password.', category='danger')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', category='success')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegForm()
    if form.validate_on_submit():
        User(email=form.email.data, username=form.username.data,
             password=form.password.data, location=form.location.data).new()
        user_utl = UserUtl(db.User.find_one({'email': form.email.data}))
        token = user_utl.generate_token()
        send_email(user_utl.email, 'Confirm Your Account',
                   'auth/email/confirm', user=user_utl, token=token)
        flash('A confirmation email has been sent to your address: {}.'.format(user_utl.email), category='success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.load(token)  # data == {'ID': User.id}
    except BadSignature:
        return render_template('errors/bad_token.html')
    id = data.get('confirm')
    user = db.User.find_one({'_id': ObjectId(id)})
    if user is None:
        flash('The confirmation link is invalid or has expired.', category='danger')
    if user.is_confirmed:
        flash('Your account has already been confirmed.', category='danger')
        time.sleep(2)
        return redirect(url_for('main.index'))
    db.User.update_one({'_id': ObjectId(id)},
                                     {'$set': {'is_confirmed': True}})
    flash('You have confirmed your account successfully, Thank you!', category='success')
    time.sleep(2)
    return redirect(url_for('main.index'))


"""
any user with 'is_confirmed' is False will be redirected to this route
"""
@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous:
        abort(404)
    if current_user.is_confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/re_confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_token()
    send_email(current_user.email, 'Confirm Your Account',
               'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.', category='success')
    return redirect(url_for('main.index'))


@auth.route('/change_email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if verify_password(current_user.password, form.password.data):
            token = current_user.generate_email_change_token(form.email.data)
            send_email(current_user.email, 'Confirm Your New Email Address',
                       'auth/email/change_email',
                       user=current_user, token=token)
            flash('An email with instructions to confirm your new email address has been sent to you.', category='success')
            return redirect(url_for('main.index'))
        else:
            flash('Current password does not match your account.', category='danger')
    return render_template('auth/change_email.html', form=form)


@auth.route('/change_email/<token>')
@login_required
def change_email(token):
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except BadSignature:
        return render_template('errors/bad_token.html')
    id = data.get('ID')
    new_email = data.get('new_email')
    if new_email is None or\
       db.User.find_one({'email': new_email}) is not None or\
       db.User.find_one({'_id': ObjectId(id)}) is None:
        flash('The confirmation link is invalid or has expired.', category='danger')
        time.sleep(2)
        return redirect(url_for('main.index'))
    avatar_hash = hashlib.md5(new_email.encode('utf-8') +
                              str(current_user.member_since).\
                              encode('utf-8')).hexdigest()
    db.User.update_one({'_id': ObjectId(id)},
                                     {'$set': {'email': new_email,
                                               'avatar_hash': avatar_hash}})
    logout_user()
    flash('Your email address has been updated to {} successfully, please login again.'.format(current_user.email), category='success')
    return redirect(url_for('auth.login'))


@auth.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if verify_password(current_user.password, form.password.data):
            db.User.update_one({'email': current_user.email},
                                             {'$set': {'password': generate_password_hash(form.password_new.data)}})
            logout_user()
            flash('Your password has been updated, please login again.', category='success')
            return redirect(url_for('auth.login'))
        else:
            flash('Current password does not match your account.', category='danger')
    return render_template('auth/change_password.html', form=form)


# privilege test - Admin
@auth.route('/admin')
@login_required
@admin_required
def admin_only():
    return 'For Administrator only'
