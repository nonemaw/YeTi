"""
login into a specified XPLAN site, fetch all data to local database
"""
import requests
import re
import os
import logging
import json

from . import global_vars
from bson import ObjectId
from app.db import mongo_connect
from app.models import Group, SubGroup


class Fetcher:
    def __init__(self, username, password, company='ytml', debug=False, mode='w'):
        self.debug = debug
        self.mode = mode
        self.db = mongo_connect(company)
        self.USERNAME = username
        self.PASSWORD = password
        self.BASE = "https://{}.xplan.iress.com.au".format(company)
        self.URL_LOGIN = "https://{}.xplan.iress.com.au/home".format(company)
        self.URL_LIST = "https://{}.xplan.iress.com.au/ufield/list".format(company)
        self.URL_WALKER = "https://{}.xplan.iress.com.au/ufield/list_iframe?group=".format(company) + '{}'
        self.URL_LOGOUT = "https://{}.xplan.iress.com.au/home/logoff?".format(company)

    def run(self):
        this_path = os.path.dirname(os.path.realpath(__file__))
        logger = logging.getLogger('my_logger')
        hdlr = logging.FileHandler(os.path.join(this_path, 'fetcher.log'), 'w')
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        logger.addHandler(hdlr)
        logger.setLevel(logging.INFO)

        with requests.session() as session:
            try:
                # login payload
                payload = {
                    "userid": self.USERNAME,
                    "passwd": self.PASSWORD,
                    "rolename": "User",
                    "redirecturl": ''
                }
                # send POST to login page
                session.post(self.URL_LOGIN, data=payload, headers=dict(referer=self.URL_LOGIN))
                # try to get main list page content
                fields = session.get(self.URL_LIST, headers = dict(referer = self.URL_LIST))
                if re.search(r'permission_error', fields.text):
                    # login failed
                    print('Currently there is another user using this XPLAN account.')
                else:
                    # start working
                    print('Start working ... ')

                    dropdown_options = re.search(r'<select\b[^>]*>(?P<option_tags>.*)<\/select>', fields.text).group('option_tags').split('</option>')
                    dropdown_options[-1] = '_loop_end'  # original dropdown_options[-1] is an empty string ''
                    sub_group_list = []
                    former_group = ''
                    former_group_id = ''
                    to_json = {}

                    # for each group (option), the main loop
                    for option in dropdown_options:
                        if option == '_loop_end':
                            # update former group
                            self.db.Group.update({'_id': ObjectId(former_group_id)}, {'$set': {'sub_groups': sub_group_list}})
                            # sub_group_to_json[self.db.SubGroup.find_one({'_id': ObjectId(former_sub_group_id)}).get('name')] = variables_to_json
                            break

                        try:
                            match = re.search(r'value="(?P<group>[^>]*)">(?P<obj_name>.*$)', option)
                            group_var = match.group('group').strip()
                            group_name = match.group('obj_name').strip()

                            if group_var != former_group:
                                # if moved to a new group, update the former group's subgroup list to DB, then change former_group to current group
                                if former_group and former_group_id and len(sub_group_list):
                                    self.db.Group.update({'_id': ObjectId(former_group_id)}, {'$set': {'sub_groups': sub_group_list}})
                                    sub_group_list = []
                                former_group_id = Group(group_var, group_name).new()
                                former_group = group_var

                            logger.info('Processing {} - {}'.format(group_var, group_name))
                            all_subgroup_variable = re.sub(r'<td align.+<\/td>\n', '', session.get(self.URL_WALKER.format(group_var), headers=dict(referer=self.URL_WALKER.format(group_var))).text)

                            former_sub_group = ''
                            former_sub_group_id = ''
                            former_sub_group_variables = []
                            variables_to_json = []

                            # for each option's entry ([sub_group] - variable pair), analysis sub_group and variable
                            for href_name_type in re.findall(r'<a href=\"([^=]+)\" .+\">(.+)<\/a><\/td>\n\s+<td>(.+)<\/td>', all_subgroup_variable):
                                if len(href_name_type):
                                    href, var_name, var_type = href_name_type
                                    var = href.split('/')[-1]
                                    sub_group = 'empty'
                                    if '&#x5B;' in var_name:
                                        sub_group, var_name = re.search(r'&#x5B;(.+)&#x5D; (.+)', var_name).groups()

                                    if sub_group != former_sub_group:
                                        # if moved to a new subgroup, updating former SubGroup's variables, then insert new current SubGroup to DB
                                        if former_sub_group and former_sub_group_id:
                                            self.db.SubGroup.update({'_id': ObjectId(former_sub_group_id)}, {'$set': {'variables': former_sub_group_variables}})
                                            if group_var in to_json:
                                                to_json[group_var].append({former_sub_group: variables_to_json})
                                            else:
                                                to_json[group_var] = [{former_sub_group: variables_to_json}]
                                            former_sub_group_variables = []
                                            variables_to_json = []
                                        former_sub_group_id = SubGroup(sub_group).new()
                                        former_sub_group = sub_group
                                        sub_group_list.append(former_sub_group_id)

                                    logger.info('Fetching ' + self.BASE + href)
                                    if '/ufield/edit/entity_' in href:
                                        usage = '$entity.' + href.split('/ufield/edit/entity_')[1].replace('/', '.')
                                    elif '/ufield/edit/entity' in href:
                                        usage = '$entity.' + href.split('/ufield/edit/entity/')[1]
                                    else:
                                        usage = '$entity.' + href.split('/ufield/edit/')[1].replace('/', '.')

                                    # information collection to a variable finished: var / var_name / sub_group / var_type / usage
                                    if var_type == 'Multi' or var_type == 'Choice':
                                        multi = {}
                                        session.get(self.BASE + href, headers=dict(referer=self.BASE + href))
                                        multi_content = session.get(self.BASE + '/ufield/list_options', headers=dict(referer=self.BASE + href))
                                        multi_content = re.sub(r'(?:&#xA0;|<img)', '\n', multi_content.text)
                                        multi_choice = iter(re.findall(r'<td>(.*)<\/td>(?:\n\s+|\s+)<td(.+)>', multi_content))

                                        for m in multi_choice:
                                            """multi_choice is like:
                                             [('1', ' align="center"'),
                                              ('car', '>Increase Assessable Assets</td'),
                                              ('2', ' align="center"'),
                                              ('trunk', '>Decrease Assessable Assets</td')]
                                             multi: {1: [choice_value, choice_text], 2:[choice_value, choice_text], ...}
                                            """
                                            index = str(m[0])
                                            next_item = next(multi_choice)
                                            try:
                                                choice_text = re.search(r'>(.+)<.+', next_item[1]).group(1)
                                            except:
                                                choice_text = ''
                                            multi[index] = [next_item[0], choice_text]
                                    else:
                                        multi = None

                                    former_sub_group_variables.append(dict(var=var, name=var_name, type=var_type, multi=multi, usage=usage))
                                    variables_to_json.append({var: var_name})

                            # end of loop in current group's [sub_group] - variable pairs, update last subgroup's variabls
                            self.db.SubGroup.update({'_id': ObjectId(former_sub_group_id)}, {'$set': {'variables': former_sub_group_variables}})
                            if group_var in to_json:
                                to_json[group_var].append({former_sub_group: variables_to_json})
                            else:
                                to_json[group_var] = [{former_sub_group: variables_to_json}]

                        except Exception as e:
                            logger.warning('Error message: ' + str(e))
                            continue

                # logout
                session.get(self.URL_LOGOUT)
            except KeyboardInterrupt:
                logger.info('Received KeyboardInterrupt, logging out ...')
                session.get(self.URL_LOGOUT)

        with open(os.path.join(this_path, global_vars.company + '.json'), self.mode) as J:
            json.dump(to_json, J)
