
from flask import render_template, redirect, url_for, request, abort, flash
from flask_login import current_user, login_required
from bson import ObjectId

from . import main
from .forms import EditProfileForm, EditProfileAdminForm
from ..db import mongo_connect
from ..models import UserUtl
from ..decorators import admin_required


db = mongo_connect('ytml')


@main.route('/', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        return render_template('index.html')
    else:
        return redirect(url_for('auth.login'))


@main.route('/user_profile/<id>')
def user(id):
    user_dict = db.User.find_one({'_id': ObjectId(id)})
    if not user_dict:
        return render_template('errors/missing_user.html')
    user_utl = UserUtl(user_dict)
    return render_template('main/user_profile.html', user_utl=user_utl)


@main.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        db.User.update({'email': current_user.email},
                                         {'$set': {'name': form.name.data,
                                                   'location': form.location.data,
                                                   'about_me': form.about_me.data}})
        flash('Your profile has been updated.')
        return redirect(url_for('main.user', id=current_user.id))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('/main/edit_profile.html', form=form, user_utl=current_user)


@main.route('/admin_edit_profile/<id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user_dict = db.User.find_one({'_id': ObjectId(id)})
    if not user_dict:
        abort(404)
    user_utl = UserUtl(user_dict)
    form = EditProfileAdminForm(user=user_utl)
    if form.validate_on_submit():
        db.User.update({'email': user_dict.get('email')},
                                         {'$set': {'email': form.email.data,
                                                   'username': form.username.data,
                                                   'is_confirmed': form.is_confirmed.data,
                                                   'role': form.role.data,
                                                   'name': form.name.data,
                                                   'location': form.location.data,
                                                   'about_me': form.about_me.data}})
        flash('The profile has been updated.')
        return redirect(url_for('main.user', id=user_utl.id))
    form.email.data = user_utl.email
    form.username.data = user_utl.username
    form.is_confirmed.data = user_utl.is_confirmed
    form.role.data = user_utl.role.type
    form.name.data = user_utl.name
    form.location.data = user_utl.location
    form.about_me.data = user_utl.about_me
    return render_template('/main/edit_admin_profile.html', form=form, user_utl=user_utl)


@main.route('/test', methods=['GET', 'POST'])
def test():
    return render_template('test.html')