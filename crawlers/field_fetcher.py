import requests
import re
import os
import gc
from bs4 import BeautifulSoup

from bson import ObjectId
from app.models import Group, SubGroup
from fuzzier.jison import Jison


class FieldFetcher:
    def __init__(self, company: str, jison: Jison, db=None):
        self.jison = jison
        self.company = company.lower()
        self.db = db
        self.BASE = f'https://{company}.xplan.iress.com.au'
        self.URL_LOGIN = f'https://{company}.xplan.iress.com.au/home'
        self.URL_LIST = f'https://{company}.xplan.iress.com.au/ufield/list'
        self.URL_WALKER = ''.join([f'https://{company}.xplan.iress.com.au/ufield/list_iframe?group=', '{}'])
        self.URL_LOGOUT = f'https://{company}.xplan.iress.com.au/home/logoff?'

    def change_company(self, company: str):
        self.company = company.lower()
        self.BASE = f'https://{company}.xplan.iress.com.au'
        self.URL_LOGIN = f'https://{company}.xplan.iress.com.au/home'
        self.URL_LIST = f'https://{company}.xplan.iress.com.au/ufield/list'
        self.URL_WALKER = ''.join([f'https://{company}.xplan.iress.com.au/ufield/list_iframe?group=', '{}'])
        self.URL_LOGOUT = f'https://{company}.xplan.iress.com.au/home/logoff?'

    def change_db(self, db=None):
        self.db = db

    def fetch(self, username: str, password: str, group_only: str = None,
              debug: bool = False) -> bool:
        # TODO: code is ugly, will refactored in the future

        this_path = os.path.dirname(os.path.realpath(__file__))
        parent_path = os.path.abspath(os.path.join(this_path, os.pardir))
        json_directory = os.path.join(parent_path, 'fuzzier', 'json')
        log_directory = os.path.join(this_path, 'log')

        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        if not os.path.exists(json_directory):
            os.makedirs(json_directory)

        to_json = {}
        with requests.session() as session:
            # login payload
            payload = {
                "userid": username,
                "passwd": password,
                "rolename": "User",
                "redirecturl": ''
            }
            session.post(self.URL_LOGIN, data=payload, headers={'referer': self.URL_LOGIN})
            field_page = session.get(self.URL_LIST, headers={'referer': self.URL_LIST}).text
            if re.search(r'permission_error|Login for User', field_page):
                raise Exception(
                    'Currently there is another user using this XPLAN account.')

            else:
                soup = BeautifulSoup(field_page, 'lxml')
                dropdown_options = soup.find(id='fld_group').find_all('option') + ['_loop_end']

                sub_group_list = []
                former_group = None
                former_group_id = None
                for group in dropdown_options:
                    gc.disable()
                    # if all options (groups) are traversed, update DB for former last group
                    if group == '_loop_end' and not group_only:
                        Group.update_doc(
                            {'_id': ObjectId(former_group_id)},
                            {'sub_groups': sub_group_list},
                            specific_db=self.db
                        )
                        break

                    elif group == '_loop_end' and group_only:
                        break

                    group_var = group['value']
                    group_name = group.text
                    if group_only:
                        # if current group not matched, continue
                        if group_var != group_only and group_name != group_only:
                            continue
                        # if current group matched, change `group_only` to
                        # currently group's `group_var` (because `group_only`
                        # can be also a `group_name`)
                        else:
                            group_only = group_var
                            Group.delete_doc({'var': group_only}, specific_db=self.db)

                    if group_var != former_group:
                        # if moved to a new group, update the former group's
                        # subgroup list to DB, then change former_group to
                        # current group
                        if former_group and former_group_id and len(sub_group_list):
                            Group.update_doc(
                                {'_id': ObjectId(former_group_id)},
                                {'sub_groups': sub_group_list},
                                specific_db=self.db
                            )
                            sub_group_list = []
                        former_group_id = Group(str(group_var), str(group_name)).new(specific_db=self.db)
                        former_group = group_var

                    if debug:
                        print(f'Processing <{group_var} - {group_name}>')

                    group_page = session.get(self.URL_WALKER.format(group_var), headers={'referer': self.URL_WALKER.format(group_var)}).text
                    soup = BeautifulSoup(group_page, 'lxml')

                    former_sub_group = None
                    former_sub_group_id = None
                    former_sub_group_variables = []
                    variables_to_json = []

                    all_vars_under_current_group = soup.find('tbody', {'class': 'list2'}).find_all('tr')
                    for var_entry in all_vars_under_current_group:

                        print(var_entry)
                        print('-----------------------------------------------')

                        # for each option's entry ([sub_group] - variable pair),
                        # analysis sub_group and variable
                        try:
                            var_detail = var_entry.find_all('td')[1:3]
                            var_type = var_detail[-1].text
                            var_detail = var_detail[0].find('a')
                            href = var_detail['href']
                            var = href.split('/')[-1]
                            var_name = var_detail.text
                        except:
                            var_detail = var_entry.find_all('td')[3:7]
                            var_type = var_detail[-1].text
                            var_detail = var_detail[0].find('a')
                            href = var_detail['href']
                            var = href.split('/')[-1]
                            var_name = var_detail.text

                        sub_group = None
                        if '[' in var_name:
                            sub_group, var_name = re.search(r'\[(.+)\] (.+)', var_name).groups()

                        if sub_group != former_sub_group:
                            # if moved to a new subgroup, updating former
                            # SubGroup's variables, then insert new current
                            # SubGroup to DB
                            if former_sub_group and former_sub_group_id:
                                SubGroup.update_doc(
                                    {'_id': ObjectId(former_sub_group_id)},
                                    {'variables': former_sub_group_variables},
                                    specific_db=self.db
                                )
                                if group_var in to_json:
                                    to_json[group_var].append({former_sub_group: variables_to_json})
                                else:
                                    to_json[group_var] = [{former_sub_group: variables_to_json}]
                                former_sub_group_variables = []
                                variables_to_json = []

                            former_sub_group_id = SubGroup(sub_group).new(specific_db=self.db)
                            former_sub_group = sub_group
                            sub_group_list.append(former_sub_group_id)

                        if debug:
                            print(f'Fetching {self.BASE}{href}')

                        if '/ufield/edit/entity_' in href:
                            usage = f'$client.{href.split("/ufield/edit/entity_")[1].replace("/", ".")}'
                        elif '/ufield/edit/entity' in href:
                            usage = f'$client.{href.split("/ufield/edit/entity/")[1]}'
                        else:
                            usage = f'$client.{href.split("/ufield/edit/")[1].replace("/", ".")}'

                        # information collection to a variable done:
                        # var / var_name / sub_group / var_type / usage

                        if var_type in ['Multi', 'Choice']:
                            # if a variable is a multi/single choice type,
                            # visit variable page and acquire choices
                            session.get(self.BASE + href, headers={'referer': f'{self.BASE}{href}'})
                            multi_choice_page = session.get(f'{self.BASE}/ufield/list_options', headers={'referer': f'{self.BASE}{href}'}).text
                            soup = BeautifulSoup(multi_choice_page, 'lxml')

                            multi = {}
                            index = 1
                            choices = soup.find_all('td', {'class': 'option-key'})
                            for choice in choices:
                                choice_var = choice.text
                                try:
                                    choice_text = choice.find_next_sibling('td').text
                                except:
                                    choice_text = ''
                                multi[str(index)] = [choice_var, choice_text]
                                index += 1

                            if var_type == 'Multi':
                                var_type = 'Multiple Choice / Checkboxes (List)'
                            elif var_type == 'Choice':
                                var_type = 'Single Choice (String)'
                        else:
                            multi = None

                        former_sub_group_variables.append(
                            {'var': var, 'name': var_name, 'type': var_type,
                             'multi': multi, 'usage': usage}
                        )
                        variables_to_json.append({var: var_name})

                    # end for
                    # end loop in current group's [sub_group] - variable pairs,
                    # update last subgroup's variables
                    SubGroup.update_doc(
                        {'_id': ObjectId(former_sub_group_id)},
                        {'variables': former_sub_group_variables},
                        specific_db=self.db)
                    if group_var in to_json:
                        to_json[group_var].append({former_sub_group: variables_to_json})
                    else:
                        to_json[group_var] = [{former_sub_group: variables_to_json}]

                    gc.enable()
                # end for
                # end loop in groups
            # endif, logout
            session.get(self.URL_LOGOUT)

        import json
        if not group_only:
            self.jison.write(json.dumps(to_json), file_name=self.company)
        else:
            self.jison.load(file_name=self.company).replace_object(group_only, json.dumps(to_json))
        return True

    def update_group(self, name: list or str):
        pass

    def delete_group(self, name: str):
        pass

    def delete_subgroup(self, name: str):
        pass
