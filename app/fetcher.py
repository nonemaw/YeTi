"""
login into a specified XPLAN site, fetch all data to local database
"""
import requests
import re
from bson import ObjectId
from .db import mongo_connect
from .models import Group, SubGroup


USERNAME = "ytmlai2"
PASSWORD = "Passw0rd1"
COMPANY = 'ytml'
BASE = "https://{}.xplan.iress.com.au".format(COMPANY)
URL_LOGIN = "https://{}.xplan.iress.com.au/home".format(COMPANY)
URL_LIST = "https://{}.xplan.iress.com.au/ufield/list".format(COMPANY)
URL_WALKER = "https://{}.xplan.iress.com.au/ufield/list_iframe?group=".format(COMPANY) + '{}'
URL_LOGOUT = "https://{}.xplan.iress.com.au/home/logoff?".format(COMPANY)


db = mongo_connect(COMPANY)


def fetcher():
    with requests.session() as session:

        # login payload
        payload = {
            "userid": USERNAME,
            "passwd": PASSWORD,
            "rolename": "User",
            "redirecturl": ''
        }

        # send POST to login page
        session.post(URL_LOGIN, data=payload, headers=dict(referer=URL_LOGIN))

        # try to get main list page content
        fields = session.get(URL_LIST, headers = dict(referer = URL_LIST))
        if re.search(r'permission_error', fields.text):
            # login failed
            print('Currently there is another user using this XPLAN account.')
        else:
            sub_group_list = []
            former_group = ''
            former_group_id = ''
            former_sub_group = ''
            former_sub_group_id = ''
            former_sub_group_variables = []

            # logged in, loop in drop-down options
            dropdown_options = re.search(r'<select\b[^>]*>(?P<option_tags>.*)<\/select>', fields.text).group('option_tags').split('</option>')
            dropdown_options[-1] = '_loop_end'  # original dropdown_options[-1] is an empty string ''
            for option in dropdown_options:
                """ main loop in options (groups)
                """
                if option == '_loop_end':
                    # update both former group and former sub_group
                    db.Group.update({'_id': ObjectId(former_group_id)}, {'$set': {'sub_groups': sub_group_list}})
                    db.SubGroup.update({'_id': ObjectId(former_sub_group_id)}, {'$set': { 'variables': former_sub_group_variables}})
                    break
                try:
                    # for each group (option)
                    match = re.search(r'value="(?P<group>[^>]*)">(?P<obj_name>.*$)', option)
                    group_var = match.group('group').strip()
                    group_name = match.group('obj_name').strip()
                    if group_var != former_group:
                        if former_group and former_group_id and len(sub_group_list):
                            db.Group.update({'_id': ObjectId(former_group_id)}, {'$set': {'sub_groups': sub_group_list}})
                            sub_group_list = []
                        former_group_id = Group(group_var, group_name).new()
                        former_group = group_var

                    print('### Processing {} - {} ###'.format(group_var, group_name))

                    # loop in each option's variables (subgroup - variable)
                    sub = re.sub(r'<td align.+<\/td>\n', '', session.get(URL_WALKER.format(group_var), headers=dict(referer=URL_WALKER.format(group_var))).text)
                    for href_name_type in re.findall(r'<a href=\"([^=]+)\" .+\">(.+)<\/a><\/td>\n\s+<td>(.+)<\/td>', sub):
                        """ sub loop in sub groups - variables
                        """
                        # for each variable
                        if len(href_name_type):
                            href, name, type = href_name_type
                            var = href.split('/')[-1]
                            sub_group = 'empty'
                            if '&#x5B;' in name:
                                sub_group, name = re.search(r'&#x5B;(.+)&#x5D; (.+)', name).groups()

                            if sub_group != former_sub_group:
                                # updating former SubGroup's variables, then insert new SubGroup to DB
                                if former_sub_group and former_sub_group_id:
                                    db.SubGroup.update({'_id': ObjectId(former_sub_group_id)}, {'$set': {'variables': former_sub_group_variables}})
                                    former_sub_group_variables = []
                                former_sub_group_id = SubGroup(sub_group).new()
                                former_sub_group = sub_group
                                sub_group_list.append(former_sub_group_id)

                            print('Fetching ' + BASE + href)
                            if '/ufield/edit/entity_' in href:
                                usage = '$entity.' + href.split('/ufield/edit/entity_')[1].replace('/', '.')
                            elif '/ufield/edit/entity' in href:
                                usage = '$entity.' + href.split('/ufield/edit/entity/')[1]
                            else:
                                usage = '$entity.' + href.split('/ufield/edit/')[1].replace('/', '.')

                            # information collection to a variable finished: var / name / sub_group / type / usage
                            if type == 'Multi' or type == 'Choice':
                                multi = {}
                                session.get(BASE + href, headers=dict(referer=BASE + href))
                                multi_content = session.get(BASE + '/ufield/list_options', headers=dict(referer=BASE + href))
                                multi_content = re.sub(r'(?:&#xA0;|<img)', '\n', multi_content.text)
                                multi_choice = iter(re.findall(r'<td>(.*)<\/td>(?:\n\s+|\s+)<td(.+)>', multi_content))

                                for m in multi_choice:
                                    """multi_choice is like:
                                     [('1', ' align="center"'),
                                      ('car', '>Increase Assessable Assets</td'),
                                      ('2', ' align="center"'),
                                      ('trunk', '>Decrease Assessable Assets</td')
                                     ]
                                     multi: {1: [choice_value, choice_text], 2:[choice_value, choice_text], ...}
                                    """
                                    index = int(m[0])
                                    next_item = next(multi_choice)
                                    try:
                                        choice_text = re.search(r'>(.+)<.+', next_item[1]).group(0)
                                    except:
                                        choice_text = ''
                                    multi[index] = [next_item[0], choice_text]
                            else:
                                multi = None
                                former_sub_group_variables.append(dict(var=var, name=name, type=type, multi=multi, usage=usage))
                except Exception as e:
                    print('Error message: ' + str(e))
                    continue

        # logout
        session.get(URL_LOGOUT)
