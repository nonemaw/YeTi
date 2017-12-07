import json
import re

from flask import request
from flask_login import login_required
from bson import ObjectId

from . import code
from app.db import mongo_connect, client
from common.code_tools import cleanup_mess, format
import fuzzier.fuzzier as fuzzier

db = mongo_connect(client, 'ytml')


@login_required
@code.route('/code_formatting', methods=['GET', 'POST'])
def code_formatting():
    received_json = request.json
    if received_json:
        code = cleanup_mess(
            received_json.get('code').replace('\r\n', '\n').split('\n'))

        if received_json.get('message') == 'indent':
            code = '\n'.join(format(code, message='indent'))
            return json.dumps({'code': code}), 200

        elif received_json.get('message') == 'dedent':
            for index, line in enumerate(code):
                code[index] = re.sub(r'^\s+', '', line)
            code = '\n'.join(code)
            return json.dumps({'code': code}), 200

        elif received_json.get('message') == 'format':
            code = '\n'.join(format(code, message='format'))
            return json.dumps({'code': code}), 200

        elif received_json.get('message') in ['client', 'partner', 'joint',
                                              'trust', 'superfund', 'company',
                                              'partnership']:
            code = '\n'.join(format(code, entity=received_json.get('message')))
            return json.dumps({'code': code}), 200

        else:
            return json.dumps({'code': code}), 200

    return json.dumps({'code': ''}), 500


@login_required
@code.route('/acquire_group', methods=['GET', 'POST'])
def group():
    result = []
    try:
        groups = db.Group.find({}).sort([('name', 1)])
        for group_dict in groups:
            result.append({group_dict.get('var'): group_dict.get('name')})
        return json.dumps({'group': result}), 200
    except:
        return json.dumps({'group': []}), 500


@login_required
@code.route('/acquire_subgroup/<var>', methods=['GET', 'POST'])
def subgroup(var):
    """
    :param var: the 'var' name of parent group
    :return:
    """
    try:
        subgroup_ids = db.Group.find_one({'var': var}).get('sub_groups')
        result = []
        if subgroup_ids:
            for id in subgroup_ids:
                result.append({id: db.SubGroup.find_one(
                    {'_id': ObjectId(id)}).get('name')})
        return json.dumps({'subgroup': result}), 200
    except:
        return json.dumps({'subgroup': []}), 500


@login_required
@code.route('/acquire_variable/<id>', methods=['GET', 'POST'])
def variable(id):
    """
    :param var: the 'var' name of parent group
    :return:
    """
    try:
        variables = db.SubGroup.find_one({'_id': ObjectId(id)}).get(
            'variables')
        result = []
        if variables:
            for var in variables:
                result.append({var.get('var'): [var.get('name'),
                                                var.get('usage'),
                                                var.get('type'),
                                                var.get('multi')]})
            return json.dumps({'variable': result}), 200
        else:
            return json.dumps({'variable': []})
    except:
        return json.dumps({'variable': []}), 500


@login_required
@code.route('/acquire_search/<pattern>', methods=['GET', 'POST'])
def ratio(pattern):
    """
    :param pattern: the pattern string to be searched
    :return:
    """
    result_list = sorted(fuzzier.search(pattern), key=lambda item: item[0],
                         reverse=True)
    returned_list = []
    try:
        for item in result_list:
            group_var = item[1]
            group_name = db.Group.find_one({'var': group_var}).get('name')
            subgroup = item[2]
            var_var = item[3]
            var_name = item[4]

            subgroup_id_list = db.Group.find_one({'var': group_var}).get(
                'sub_groups')
            subgroups_with_same_name = db.SubGroup.find({'name': subgroup})
            for subgroup_dict in subgroups_with_same_name:
                if str(subgroup_dict.get('_id')) in subgroup_id_list:
                    returned_list.append(
                        [group_var, group_name, str(subgroup_dict.get('_id')),
                         subgroup, var_var, var_name])
                    break
        return json.dumps({'search_result': returned_list}), 200
    except:
        return json.dumps({'search_result': []}), 500


@login_required
@code.route('/acquire_search_result', methods=['GET', 'POST'])
def acquire_search_result():
    received_json = request.json
    if received_json:
        subgroup_id = received_json.get('subgroup_id')
        var_var = received_json.get('var_var')
        var_list = db.SubGroup.find_one({'_id': ObjectId(subgroup_id)}).get(
            'variables')
        for item in var_list:
            if item.get('var') == var_var:
                result = [item.get('usage'), item.get('type'),
                          item.get('multi')]

                return json.dumps({'variable': result}), 200

    return json.dumps({'variable': ''}), 500
