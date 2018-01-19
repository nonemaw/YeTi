import json
import re

from flask import request
from flask_login import login_required
from bson import ObjectId

from . import code
from app.models import Group, SubGroup, InterfaceLeafPage
from common.meta import Meta
from common.code_tools import cleanup_mess, format
import fuzzier.fuzzier as fuzzier


@login_required
@code.route('/code_formatting', methods=['POST'])
def code_formatting():
    received_json = request.json
    if received_json:
        if received_json.get('message') != 'judge':
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

        elif received_json.get('message') == 'judge':
            judge_message = Meta.parser.parse(source_code=received_json.get('code'), message_only=True)
            return json.dumps({'judge_result': judge_message}), 200

        else:
            return json.dumps({'code': code}), 200

    return json.dumps({'code': ''}), 500


@login_required
@code.route('/acquire_group', methods=['GET'])
def group():
    result = []
    try:
        groups = Meta.db_company.Group.find({}).sort([('name', 1)])
        for group_dict in groups:
            result.append({group_dict.get('var'): group_dict.get('name')})
        return json.dumps({'group': result}), 200
    except:
        return json.dumps({'group': []}), 500


@login_required
@code.route('/acquire_subgroup/<var>', methods=['GET'])
def subgroup(var):
    """
    :param var: the 'var' name of parent group
    :return:
    """
    try:
        subgroup_ids = Group.search({'var': var}).get(
            'sub_groups')
        result = []
        if subgroup_ids:
            for id in subgroup_ids:
                result.append({id: SubGroup.search({'_id': ObjectId(id)}).get(
                    'name')})
        return json.dumps({'subgroup': result}), 200
    except:
        return json.dumps({'subgroup': []}), 500


@login_required
@code.route('/acquire_variable/<id>', methods=['GET'])
def variable(id):
    try:
        variables = SubGroup.search({'_id': ObjectId(id)}).get('variables')
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
@code.route('/acquire_search', methods=['POST'])
def do_search():
    """
    return a list of research result for displaying in the table
    """
    received_json = request.json
    if received_json:
        result_list = sorted(fuzzier.search(received_json.get('pattern'),
                                            int(received_json.get('count'))),
                             key=lambda item: item[0],
                             reverse=True)
        returned_list = []

        try:
            for item in result_list:
                group_var = item[1]
                group_name = Group.search({'var': group_var}).get('name')
                subgroup = item[2]
                var_var = item[3]
                var_name = item[4]

                subgroup_id_list = Group.search({'var': group_var}).get(
                    'sub_groups')
                subgroups_with_same_name = Meta.db_company.SubGroup.find(
                    {'name': subgroup})
                for subgroup_dict in subgroups_with_same_name:
                    if str(subgroup_dict.get('_id')) in subgroup_id_list:
                        returned_list.append(
                            [group_var, group_name,
                             str(subgroup_dict.get('_id')),
                             subgroup, var_var, var_name])
                        break

            return json.dumps({'search_result': returned_list}), 200

        except:
            return json.dumps({'search_result': []}), 500

    return json.dumps({'search_result': []}), 500


@login_required
@code.route('/acquire_search_result', methods=['POST'])
def acquire_search_result():
    """
    return detailed variable information when client click on of the search result
    """
    received_json = request.json

    if received_json:
        var_list = SubGroup.search(
            {'_id': ObjectId(received_json.get('subgroup_id'))}).get(
            'variables')
        for item in var_list:
            if item.get('var') == received_json.get('var_var'):
                result = [item.get('usage'), item.get('type'),
                          item.get('multi')]

                return json.dumps({'variable': result}), 200

    return json.dumps({'variable': ''}), 500


@login_required
@code.route('/acquire_interface', methods=['GET'])
def acquire_interface():
    result = []
    try:
        root_nodes = Meta.db_company.InterfaceNode.find({}).sort([('id', 1)])
        for node_dict in root_nodes:
            # remove database _id serial number
            del node_dict['_id']
            result.append(node_dict)
        return json.dumps({'root_nodes': result}), 200
    except:
        return json.dumps({'root_nodes': []}), 500


@login_required
@code.route('/acquire_leaf', methods=['POST'])
def acquire_leaf():
    received_json = request.json

    if received_json:
        _id = received_json.get('id')
        leaf_content = InterfaceLeafPage.search({'id': _id})
        # remove database _id serial number, this `_id` is not `id`
        if leaf_content:
            del leaf_content['_id']
            return json.dumps({'leaf': leaf_content}), 200

    return json.dumps({'leaf': {}}), 500
