
import json
import re

from flask import render_template, redirect, url_for, request, abort, flash
from flask_login import current_user, login_required
from bson import ObjectId

from . import code
from ..db import mongo_connect
from ..models import UserUtl
from ..decorators import admin_required


db = mongo_connect('ytml')


@login_required
@code.route('/code_formatting', methods=['GET', 'POST'])
def code_formatting():
    received_json = request.json
    if received_json:
        def indent(line:str, level:int):
            for i in range(level):
                line = '    ' + line
            return line

        def cleanup_mess(code:list):
            clean_code = []
            for line in code:
                    if not re.search(r'(^\s*<:for|^\s*<:if|^\s*<:else|^\s*<:end)', line):
                        # if a line is not started with 'for/if/else/end' but contains 'for/if/else/end'
                        if '<:for' in line or '<:if' in line or '<:else' in line or '<:end' in line:
                            for segment in line.split('<:'):
                                if ':>' in segment:
                                    clean_code.append('<:' + segment)
                                elif segment:
                                    clean_code.append(segment)
                        else:
                            clean_code.append(line)
                    else:
                        clean_code.append(line)
            return clean_code

        code = cleanup_mess(received_json.get('code').replace('\r\n', '\n').split('\n'))
        if received_json.get('message') == 'indent':
            level = 0
            for index, line in enumerate(code):
                if line.startswith('<:'):
                    if line.startswith('<:for') or line.startswith('<:if'):
                        if '<:end:>' in line:
                            if len(re.findall(r'<:if', line) + re.findall(r'<:for', line)) == len(re.findall(r'<:end:>', line)):
                                code[index] = indent(line, level)
                            else:
                                code[index] = indent(line, level)
                                level += 1
                        else:
                            code[index] = indent(line, level)
                            level += 1
                    elif line.startswith('<:else'):
                        code[index] = indent(line, level - 1)
                    elif line.startswith('<:end'):
                        level -= 1
                        code[index] = indent(line, level)
                    else:
                        code[index] = indent(line, level)
                else:
                    pass
            code = '\n'.join(code)
            return json.dumps({'code': code}), 200

        elif received_json.get('message') == 'dedent':
            for index, line in enumerate(code):
                code[index] = re.sub(r'^\s+', '', line)
            code = '\n'.join(code)
            return json.dumps({'code': code}), 200
        else:
            return json.dumps({'code': code}), 200
    else:
        return json.dumps({'code': ''}), 500


@login_required
@code.route('/group', methods=['GET', 'POST'])
def group():
    result = []
    groups = db.Group.find({}).sort([('name', 1)])
    for group_dict in groups:
        result.append({group_dict.get('var'): group_dict.get('name')})
    return json.dumps({'group': result}), 200


@login_required
@code.route('/subgroup/<var>', methods=['GET', 'POST'])
def subgroup(var):
    """
    :param var: the 'var' name of parent group
    :return:
    """
    subgroup_ids = db.Group.find_one({'var': var}).get('sub_groups')
    result = []
    if subgroup_ids:
        for id in subgroup_ids:
            result.append({id: db.SubGroup.find_one({'_id': ObjectId(id)}).get('name')})
        return json.dumps({'subgroup': result}), 200
    else:
        return json.dumps({'subgroup': []})


@login_required
@code.route('/variable/<id>', methods=['GET', 'POST'])
def variable(id):
    """
    :param var: the 'var' name of parent group
    :return:
    """
    variables = db.SubGroup.find_one({'_id': ObjectId(id)}).get('variables')
    result = []
    if variables:
        for var in variables:
            result.append({var.get('var'): [var.get('name'), var.get('usage'), var.get('type'), var.get('multi')]})
        return json.dumps({'variable': result}), 200
    else:
        return json.dumps({'variable': []})
