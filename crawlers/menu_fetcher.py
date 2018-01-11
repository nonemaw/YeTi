"""
login into a specified XPLAN site, fetch all data to local database
"""
import requests
import re
import os
import logging

from bson import ObjectId
from common.meta import Meta
from app.models import Group, SubGroup
from fuzzier.jison import Jison


class MenuFetcher:
    def __init__(self):
        pass

    # TODO: along with Jison, support a list of group update, generate a list of 'to_json' result based on the list of groups
    def fetch(self, group_only: str = None):
        # TODO: code is ugly, will refactored in the future

        BASE = f'https://{Meta.company}.xplan.iress.com.au'
        URL_LOGIN = f'https://{Meta.company}.xplan.iress.com.au/home'
        URL_LIST = f'https://{Meta.company}.xplan.iress.com.au/ufield/list'
        URL_WALKER = ''.join([f'https://{Meta.company}.xplan.iress.com.au/ufield/list_iframe?group=', '{}'])
        URL_LOGOUT = f'https://{Meta.company}.xplan.iress.com.au/home/logoff?'

        this_path = os.path.dirname(os.path.realpath(__file__))
        parent_path = os.path.abspath(os.path.join(this_path, os.pardir))
        json_directory = os.path.join(parent_path, 'fuzzier', 'json')
        log_directory = os.path.join(this_path, 'log')

        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        if not os.path.exists(json_directory):
            os.makedirs(json_directory
                        )
        logger = logging.getLogger('my_logger')
        logfile_hdlr = logging.FileHandler(
            os.path.join(log_directory, 'fetcher.log'), 'w')
        logfile_hdlr.setFormatter(
            logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
        logger.addHandler(logfile_hdlr)
        logger.setLevel(logging.INFO)

        to_json = {}
        with requests.session() as session:
            try:
                # login payload
                payload = {
                    "userid": Meta.company_username,
                    "passwd": Meta.company_password,
                    "rolename": "User",
                    "redirecturl": ''
                }
                # send POST to login page
                session.post(URL_LOGIN, data=payload,
                             headers=dict(referer=URL_LOGIN))
                # try to get main list page content
                fields = session.get(URL_LIST,
                                     headers=dict(referer=URL_LIST))

                if re.search(r'permission_error', fields.text):
                    # login failed
                    raise Exception(
                        'Currently there is another user using this XPLAN account.')

                else:
                    # start working
                    dropdown_options = re.search(
                        r'<select\b[^>]*>(?P<option_tags>.*)<\/select>',
                        fields.text).group('option_tags').split('</option>')
                    dropdown_options[
                        -1] = '_loop_end'  # original dropdown_options[-1] is an empty string ''
                    sub_group_list = []
                    former_group = ''
                    former_group_id = ''

                    # for each group (option), the main loop
                    for option in dropdown_options:
                        if option == '_loop_end' and not group_only:
                            # update former group
                            Group.update_doc(
                                {'_id': ObjectId(former_group_id)},
                                {'sub_groups': sub_group_list})
                            break

                        try:
                            match = re.search(
                                r'value="(?P<group>[^>]*)">(?P<obj_name>.*$)',
                                option)
                            group_var = match.group('group').strip()
                            group_name = match.group('obj_name').strip()

                            if group_only:
                                # if current group not matched, continue
                                if group_var != group_only and group_name != group_only:
                                    continue
                                # if current group matched, change `group_only` to
                                # currently group's `group_var` (because `group_only`
                                # can be also a `group_name`)
                                else:
                                    group_only = group_var
                                    Group.delete_doc({'var': group_only})

                            if group_var != former_group:
                                # if moved to a new group, update the former group's
                                # subgroup list to DB, then change former_group to
                                # current group
                                if former_group and former_group_id and len(
                                        sub_group_list):
                                    Group.update_doc(
                                        {'_id': ObjectId(former_group_id)},
                                        {'sub_groups': sub_group_list})
                                    sub_group_list = []
                                former_group_id = Group(str(group_var),
                                                        str(group_name)).new()
                                former_group = group_var

                            logger.info(
                                f'Processing {group_var} - {group_name}')
                            all_subgroup_variable = re.sub(
                                r'<td align.+<\/td>\n', '',
                                session.get(URL_WALKER.format(group_var),
                                            headers=dict(
                                                referer=URL_WALKER.format(
                                                    group_var))).text)

                            former_sub_group = ''
                            former_sub_group_id = ''
                            former_sub_group_variables = []
                            variables_to_json = []

                            # for each option's entry ([sub_group] - variable pair),
                            # analysis sub_group and variable
                            for href_name_type in re.findall(
                                    r'<a href=\"([^=]+)\" .+\">(.+)<\/a><\/td>\n\s+<td>(.+)<\/td>',
                                    all_subgroup_variable):
                                if len(href_name_type):
                                    href, var_name, var_type = href_name_type
                                    var = href.split('/')[-1]
                                    sub_group = 'empty'
                                    if '&#x5B;' in var_name:
                                        sub_group, var_name = re.search(
                                            r'&#x5B;(.+)&#x5D; (.+)',
                                            var_name).groups()

                                    if sub_group != former_sub_group:
                                        # if moved to a new subgroup, updating former
                                        # SubGroup's variables, then insert new current
                                        # SubGroup to DB
                                        if former_sub_group and former_sub_group_id:
                                            SubGroup.update_doc(
                                                {'_id': ObjectId(former_sub_group_id)},
                                                {'variables': former_sub_group_variables})
                                            if group_var in to_json:
                                                to_json[group_var].append({
                                                    former_sub_group: variables_to_json})
                                            else:
                                                to_json[group_var] = [{
                                                    former_sub_group: variables_to_json}]
                                            former_sub_group_variables = []
                                            variables_to_json = []

                                        former_sub_group_id = SubGroup(
                                            sub_group).new()
                                        former_sub_group = sub_group
                                        sub_group_list.append(
                                            former_sub_group_id)

                                    logger.info(f'Fetching {BASE}{href}')
                                    if '/ufield/edit/entity_' in href:
                                        usage = f'$client.{href.split("/ufield/edit/entity_")[1].replace("/", ".")}'
                                    elif '/ufield/edit/entity' in href:
                                        usage = f'$client.{href.split("/ufield/edit/entity/")[1]}'
                                    else:
                                        usage = f'$client.{href.split("/ufield/edit/")[1].replace("/", ".")}'

                                    # information collection to a variable finished:
                                    # var / var_name / sub_group / var_type / usage
                                    if var_type == 'Multi' or var_type == 'Choice':
                                        multi = {}
                                        session.get(BASE + href,
                                                    headers=dict(
                                                        referer=BASE + href))
                                        multi_content = session.get(
                                            f'{BASE}/ufield/list_options',
                                            headers=dict(
                                                referer=BASE + href))
                                        multi_content = re.sub(
                                            r'(?:&#xA0;|<img)', '\n',
                                            multi_content.text)
                                        multi_choice = iter(re.findall(
                                            r'<td>(.*)<\/td>(?:\n\s+|\s+)<td(.+)>',
                                            multi_content))

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
                                                choice_text = re.search(
                                                    r'>(.+)<.+',
                                                    next_item[1]).group(1)
                                            except:
                                                choice_text = ''
                                            multi[index] = [next_item[0],
                                                            choice_text]

                                        if var_type == 'Multi':
                                            var_type = 'Multiple Choice / Checkboxes (List)'
                                        elif var_type == 'Choice':
                                            var_type = 'Single Choice (String)'
                                    else:
                                        multi = None

                                    former_sub_group_variables.append(
                                        dict(var=var, name=var_name,
                                             type=var_type, multi=multi,
                                             usage=usage))
                                    variables_to_json.append({var: var_name})

                            # end of loop in current group's [sub_group] - variable pairs,
                            # update last subgroup's variables
                            SubGroup.update_doc(
                                {'_id': ObjectId(former_sub_group_id)},
                                {'variables': former_sub_group_variables})
                            if group_var in to_json:
                                to_json[group_var].append(
                                    {former_sub_group: variables_to_json})
                            else:
                                to_json[group_var] = [
                                    {former_sub_group: variables_to_json}]

                        # endtry
                        except Exception as e:
                            logger.warning(f'Error message: {str(e)}')
                            continue
                    # endfor

                # endif, logout
                session.get(URL_LOGOUT)
            except KeyboardInterrupt:
                logger.info('Received keyboard interruption, logging out ...')
                session.get(URL_LOGOUT)

        import json
        if not group_only:
            Meta.jison.write(json.dumps(to_json), file_name=Meta.company)
        else:
            Meta.jison.replace_object(group_only, json.dumps(to_json))
        to_json.clear()

    def update_group(self, name: list or str):
        if isinstance(name, str):
            self.fetch(name)

    def delete_group(self, name: str):
        pass

    def delete_subgroup(self, name: str):
        pass


if __name__ == '__main__':
    from app.db import mongo_connect, client

    specific = input('specific nodes (optional): ')
    if not specific:
        specific = []
    else:
        specific = [x.strip() for x in specific.split(',') if x]

    Meta.company = 'fmd'
    Meta.company_username = 'DXu'
    Meta.company_password = ''
    Meta.jison = Jison()
    Meta.db_company = Meta.db_default if Meta.company == 'ytml' else mongo_connect(
        client, Meta.company)
    Meta.menu_fetcher = MenuFetcher()
    Meta.menu_fetcher.fetch()