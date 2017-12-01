
import json
from flask import render_template, redirect, url_for, request, abort, flash, jsonify
from flask_login import current_user, login_required
from bson import ObjectId

from . import main
from .forms import EditProfileForm, EditProfileAdminForm
from app.db import mongo_connect, client
from app.models import UserUtl, Snippet
from app.decorators import admin_required
from common.pagination import PaginationSnippet
from common.meta import Meta
from common.interface_fetcher import initialize_interface, update_interface


db = mongo_connect(client, 'ytml')


@main.route('/test')
def test():
    return render_template('test.html')


@main.route('/', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        return render_template('index.html', company=Meta.company)
    else:
        return redirect(url_for('auth.login'))


@main.route('/user_profile/<id>')
def user(id):
    user_dict = db.User.find_one({'_id': ObjectId(id)})
    if not user_dict:
        return render_template('errors/missing_user.html')
    user_utl = UserUtl(user_dict)

    current_page = request.args.get('page', 1, type=int)
    pagination = PaginationSnippet(current_page)
    snippets = pagination.items

    return render_template('main/user_profile.html', user_utl=user_utl,
                                                     pagination=pagination,
                                                     snippets=snippets)


@main.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        db.User.update_one({'email': current_user.email},
                                         {'$set': {'name': form.name.data,
                                                   'location': form.location.data,
                                                   'about_me': form.about_me.data}})
        flash('Your profile has been updated successfully.', category='info')
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
        flash('The profile has been updated successfully.', category='info')
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

        if group_id and scenario_id:
            flash('New code snippet has been created successfully.', category='info')
            return redirect(url_for('main.edit_snippet', group=snippet_group, scenario=snippet_scenario))
        else:
            flash('Naming conflict, please change Group name or Scenario name.', category='danger')
            return render_template('main/create_snippet.html', snippet_code=snippet_code)
    return render_template('main/create_snippet.html', snippet_code='')


@main.route('/edit_snippet/<group>/<scenario>', methods=['GET', 'POST'])
@login_required
def edit_snippet(group, scenario):
    old_group_dict = db.SnippetGroup.find_one({'name': group})
    if not old_group_dict:
        try:
            old_group_dict = db.SnippetGroup.find_one({'_id': ObjectId(group)})
        except:
            abort(404)

    old_scenario_id_list = old_group_dict.get('scenarios')
    old_scenario_dict = {}
    old_scenario_id = ''
    old_scenario = scenario
    for id in old_scenario_id_list:
        old_scenario_dict = db.SnippetScenario.find_one({'_id': ObjectId(id)})
        if old_scenario_dict.get('name') == scenario:
            old_scenario_id = id
            break

    if not old_scenario_dict or not old_scenario_id:
        try:
            old_scenario_dict = db.SnippetScenario.find_one({'_id': ObjectId(scenario)})
            old_scenario = old_scenario_dict.get('name')
            old_scenario_id = scenario
        except:
            abort(404)

    old_code = old_scenario_dict.get('code')
    old_group = old_group_dict.get('name')
    group_id = str(old_group_dict.get('_id'))

    if request.form:
        new_code = request.form.get('code')
        new_group = request.form.get('group')
        new_scenario = request.form.get('scenario')

        if old_group_dict.get('name') != new_group:
            # case 1: group changed
            # remove old scenario id from old group, if scenario list after the operation is empty, delete the group
            old_scenario_id_list.remove(old_scenario_id)

            if not len(old_scenario_id_list):
                # if group has no scenario anymore after the removal, delete the group directly
                db.SnippetGroup.delete_one({'_id': ObjectId(group_id)})
            else:
                # otherwise update group's scenario list
                db.SnippetGroup.update_one({'_id': ObjectId(group_id)}, {'$set': {'scenarios': old_scenario_id_list}})

            new_group_dict = db.SnippetGroup.find_one({'name': new_group})
            if new_group_dict:
                # if new target group already exists
                # before group change, check whether old/new scenario name is already in target group, if conflict exists then do a rename
                new_scenario_id_list = db.SnippetGroup.find_one({'_id': ObjectId(new_group_dict.get('_id'))}).get('scenarios')

                if old_scenario != new_scenario:
                    # if scenario name changed, check new scenario name conflict
                    for id in new_scenario_id_list:
                        if db.SnippetScenario.find_one({'_id': ObjectId(id)}).get('name') == new_scenario:
                            new_scenario += '_COPY'
                            flash('A naming conflict occurs to Scenario\'s name in current Group. Current Scenario has been renamed by a suffix.', category='danger')
                            break
                else:
                    # if scenario name unchanged, check old scenario name conflict
                    for id in new_scenario_id_list:
                        if db.SnippetScenario.find_one({'_id': ObjectId(id)}).get('name') == old_scenario:
                            new_scenario = old_scenario + '_COPY'
                            flash('A naming conflict occurs to Snippet Scenario in current Group. Current Snippet Scenario has been renamed by a suffix.', category='danger')
                            break

                # move old scenario id to new group, update group_id, update scenario's group name
                db.SnippetGroup.update_one({'name': new_group}, {'$push': {'scenarios': old_scenario_id}})

            else:
                # target new group does not exist
                # create new group with the old scenario id, update group_id
                document = {
                    'name': new_group,
                    'scenarios': [old_scenario_id]
                }
                db.SnippetGroup.insert_one(document)
            db.SnippetScenario.update_one( {'_id': ObjectId(old_scenario_id)}, {'$set': {'name': new_scenario, 'group': new_group}})

        elif old_scenario != new_scenario:
            # case 2: group not changed but scenario changed
            # if group not changed but scenario changed, check new scenario naming conflict under current group
            scenario_id_list = db.SnippetGroup.find_one({'_id': ObjectId(group_id)}).get('scenarios')
            for id in scenario_id_list:
                if db.SnippetScenario.find_one({'_id': ObjectId(id)}).get('name') == new_scenario:
                    new_scenario += '_COPY'
                    flash('A naming conflict occurs to Snippet Scenario in current Group. Current Snippet Scenario has been renamed by a suffix.', category='danger')
                    break
            db.SnippetScenario.update_one({'_id': ObjectId(old_scenario_id)}, {'$set': {'name': new_scenario}})

        if old_code != new_code:
            db.SnippetScenario.update_one({'_id': ObjectId(old_scenario_id)}, {'$set': {'code': new_code}})

        flash('Code snippet has been updated successfully.', category='info')
        return redirect(url_for('main.edit_snippet', group=new_group, scenario=new_scenario))
    return render_template('main/edit_snippet.html', snippet_group=old_group, snippet_scenario=old_scenario, snippet_code=old_code)


@main.route('/delete_snippet', methods=['GET', 'POST'])
@login_required
def delete_snippet():
    snippet_group = request.form.get('group')
    snippet_scenario = request.form.get('scenario')
    if not snippet_group or not snippet_scenario:
        abort(404)

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

    flash('Code Snippet has been deleted successfully.', category='info')
    return redirect(url_for('main.index'))


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
        result = sorted(result, key=lambda item: next(iter(item.values()))[0].lower())
        return json.dumps({'scenario': result}), 200
    except:
        return json.dumps({'scenario': []}), 500


@login_required
@main.route('/initialize_interface')
def _initialize_interface():
    task = initialize_interface.delay()
    return jsonify({}), 202, {'streamer_URL': url_for('main.interface_streamer', task_id=task.id)}


@login_required
@main.route('/update_interface', methods=['GET', 'POST'])
def _update_interface():
    task = update_interface.delay(_id=request.json.get('id'))
    return jsonify({}), 202, {'streamer_URL': url_for('main.interface_streamer', task_id=task.id)}


@login_required
@main.route('/interface_streamer/<task_id>')
def interface_streamer(task_id):
    task = initialize_interface.AsyncResult(task_id)
    if task.state == 'PENDING':
        # task is pending
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        # task is running
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            # task finished, get menu data
            response['result'] = task.info.get('result')
    else:
        # task failed
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info)  # this is the exception raised
        }
    return jsonify(response)
