
import json
from flask import render_template, redirect, url_for, request, abort, flash
from flask_login import current_user, login_required
from bson import ObjectId

from . import main
from .forms import EditProfileForm, EditProfileAdminForm
from app.db import mongo_connect
from app.models import UserUtl, Snippet
from app.decorators import admin_required
from common.general import random_word


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
        db.User.update_one({'email': current_user.email},
                                         {'$set': {'name': form.name.data,
                                                   'location': form.location.data,
                                                   'about_me': form.about_me.data}})
        flash('Your profile has been updated successfully.', category='success')
        return redirect(url_for('main.user', id=current_user.id))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('main/edit_profile.html', form=form, user_utl=current_user)


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
        db.User.update_one({'email': user_dict.get('email')},
                                         {'$set': {'email': form.email.data,
                                                   'username': form.username.data,
                                                   'is_confirmed': form.is_confirmed.data,
                                                   'role': form.role.data,
                                                   'name': form.name.data,
                                                   'location': form.location.data,
                                                   'about_me': form.about_me.data}})
        flash('The profile has been updated successfully.', category='success')
        return redirect(url_for('main.user', id=user_utl.id))
    form.email.data = user_utl.email
    form.username.data = user_utl.username
    form.is_confirmed.data = user_utl.is_confirmed
    form.role.data = user_utl.role.type
    form.name.data = user_utl.name
    form.location.data = user_utl.location
    form.about_me.data = user_utl.about_me
    return render_template('main/edit_admin_profile.html', form=form, user_utl=user_utl)


@main.route('/create_snippet', methods=['GET', 'POST'])
@login_required
def create_snippet():
    if request.form:
        snippet_code = request.form.get('code')
        snippet_group = request.form.get('group')
        snippet_scenario = request.form.get('scenario')
        group_id, scenario_id = Snippet(snippet_group, snippet_scenario, snippet_code).new()

        # TODO: add condition to models when group/scenario names are same

        flash('New code snippet has been created successfully.', category='success')
        return redirect(url_for('main.edit_snippet', id_group=group_id, id_scenario=scenario_id))
    return render_template('main/create_snippet.html', snippet_code='you are editing me!')


@main.route('/edit_snippet/<id_group>/<id_scenario>', methods=['GET', 'POST'])
@login_required
def edit_snippet(id_group, id_scenario):
    old_group_dict = db.SnippetGroup.find_one({'_id': ObjectId(id_group)})
    old_scenario_dict = db.SnippetScenario.find_one({'_id': ObjectId(id_scenario)})

    if not old_group_dict or not old_scenario_dict:
        abort(404)

    old_code = old_scenario_dict.get('code')
    old_group = old_group_dict.get('name')
    old_scenario = old_scenario_dict.get('name')
    group_id = id_group

    if request.form:
        new_code = request.form.get('code')
        new_group = request.form.get('group')
        new_scenario = request.form.get('scenario')

        if old_group_dict.get('name') != new_group:
            # remove old scenario id from old group, if scenario list after the operation is empty, delete the group
            old_scenario_id_list = old_group_dict.get('scenarios')
            old_scenario_id_list.remove(id_scenario)

            if not len(old_scenario_id_list):
                db.SnippetGroup.delete_one({'_id': ObjectId(id_group)})
            else:
                db.SnippetGroup.update_one({'_id': ObjectId(id_group)}, {'$set': {'scenarios': old_scenario_id_list}})
            new_group_dict = db.SnippetGroup.find_one({'name': new_group})
            if new_group_dict:
                # before group change, check whether old/new scenario name is already in target group, if conflict exists then do a rename
                new_scenario_id_list = db.SnippetGroup.find_one({'_id': ObjectId(new_group_dict.get('_id'))}).get('scenarios')

                if old_scenario != new_scenario:
                    # check new scenario name conflict
                    for id in new_scenario_id_list:
                        if db.SnippetScenario.find_one({'_id': ObjectId(id)}).get('name') == new_scenario:
                            db.SnippetScenario.update_one( {'_id': ObjectId(id_scenario)}, {'$set': {'name': new_scenario + ' - ' + random_word()}})
                            flash('A naming conflict occurs to Snippet Scenario in current Group. Current Snippet Scenario has been renamed by a random suffix.', category='danger')
                            break
                else:
                    # check old scenario name conflict
                    for id in new_scenario_id_list:
                        if db.SnippetScenario.find_one({'_id': ObjectId(id)}).get('name') == old_scenario:
                            db.SnippetScenario.update_one( {'_id': ObjectId(id_scenario)}, {'$set': {'name': old_scenario + ' - ' + random_word()}})
                            flash('A naming conflict occurs to Snippet Scenario in current Group. Current Snippet Scenario has been renamed by a random suffix.', category='danger')
                            break

                # move old scenario id to new group, update group_id
                db.SnippetGroup.update_one({'name': new_group}, {'$push': {'scenarios': id_scenario}})
                group_id = str(new_group_dict.get('_id'))
            else:
                # create new group with the old scenario id, update group_id
                document = {
                    'name': new_group,
                    'scenarios': [id_scenario]
                }
                group_id = str(db.SnippetGroup.insert(document))

        elif old_scenario != new_scenario:
            # if group not changed but scenario changed, check new scenario naming conflict under current group
            scenario_id_list = db.SnippetGroup.find_one({'_id': ObjectId(group_id)}).get('scenarios')
            for id in scenario_id_list:
                if db.SnippetScenario.find_one({'_id': ObjectId(id)}).get('name') == new_scenario:
                    new_scenario += ' - ' + random_word()
                    flash('A naming conflict occurs to Snippet Scenario in current Group. Current Snippet Scenario has been renamed by a random suffix.', category='danger')
                    break
            db.SnippetScenario.update_one({'_id': ObjectId(id_scenario)}, {'$set': {'name': new_scenario}})

        if old_code != new_code:
            db.SnippetScenario.update_one({'_id': ObjectId(id_scenario)}, {'$set': {'code': new_code}})

        flash('Code snippet has been updated successfully.', category='success')
        return redirect(url_for('main.edit_snippet', id_group=group_id, id_scenario=id_scenario))
    return render_template('main/edit_snippet.html', snippet_group=old_group, snippet_scenario=old_scenario, snippet_code=old_code)


@main.route('/delete_snippet', methods=['GET', 'POST'])
@login_required
def delete_snippet():
    snippet_group = request.form.get('group')
    snippet_scenario = request.form.get('scenario')

    scenario_id_list = db.SnippetGroup.find_one({'name': snippet_group}).get('scenarios')
    for id in scenario_id_list:
        if db.SnippetScenario.find_one({'_id': ObjectId(id)}).get('name') == snippet_scenario:
            db.SnippetScenario.delete_one( {'_id': ObjectId(id)})
            if len(scenario_id_list) == 1:
                db.SnippetGroup.delete_one({'name': snippet_group})
            else:
                scenario_id_list.remove(id)
                db.SnippetGroup.update_one({'name': snippet_group}, {'$set': {'scenarios': scenario_id_list}})
            break

    user_dict = db.User.find_one({'_id': ObjectId(current_user.id)})
    user_utl = UserUtl(user_dict)
    flash('Code Snippet has been deleted successfully.', category='success')
    return render_template('main/user_profile.html', user_utl=user_utl)


@main.route('/acquire_snippet_group', methods=['GET', 'POST'])
@login_required
def acquire_snippet_group():
    result = []
    try:
        groups = db.SnippetGroup.find({}).sort([('name', 1)])
        for group_dict in groups:
            result.append({str(group_dict.get('_id')): group_dict.get('name')})
        return json.dumps({'group': result}), 200
    except:
        return json.dumps({'group': []}), 500


@login_required
@main.route('/acquire_snippet_scenario/<_id>', methods=['GET', 'POST'])
def acquire_snippet_scenario(_id):
    try:
        scenario_ids = db.SnippetGroup.find_one({'_id': ObjectId(_id)}).get('scenarios')
        result = []
        if scenario_ids:
            for id in scenario_ids:
                snippet = db.SnippetScenario.find_one({'_id': ObjectId(id)})
                result.append({id: [snippet.get('name'), snippet.get('code')]})
        return json.dumps({'scenario': result}), 200
    except:
        return json.dumps({'scenario': []}), 500
