import requests
import re
import copy
import json
import os
from datetime import datetime
from bs4 import BeautifulSoup
from bson import ObjectId
from app.models import Group, SubGroup
from fuzzier.jison import Jison


from crawlers.core.workers import Fetcher, Parser, Saver, Filter
from crawlers.core.thread_pool import ThreadPool
from crawlers.core.config import get_url_legal


"""
initial task:

(priority=0, url=f'https://{company}.xplan.iress.com.au/ufield/list', data={'type': 'main_list'}, deep=0, repeat=0)
"""


class FieldFetcher(Fetcher):
    def __init__(self, company: str, jison: Jison = None, db=None,
                 max_repeat: int = 3, sleep_time: int = 0):
        super().__init__(max_repeat, sleep_time)
        self.jison = jison
        self.company = company.lower()
        self.db = db

    def change_db(self, db):
        self.db = db

    def fetch(self, url: str, data: dict, session):
        """
        entry point task: (0, field_page_url, data={'type': 'field_page', 'save': False}, 0, 0)
        """
        # if save is 'True', skip operation and return data directly
        if data.get('save'):
            return 1, data, (200, '', '')

        # get the page of whole list of groups, or
        # get the page of target group, send to task_queue_p
        if data.get('type') == 'field_page' or data.get('type') == 'group_page':
            response = session.get(url, timeout=(3.05, 10))
            return 1, data, (response.status_code, response.url, response.text)

        # if the type is Multi or Choice, then get the page of choices
        elif data.get('type') == 'var_page':
            var_type = data.get('var_type')
            if var_type == 'Multi' or var_type == 'Choice':
                session.get(url)
                response = session.get(f'https://{self.company}.xplan.iress.com.au/ufield/list_options', timeout=(3.05, 10))
                return 1, data, (response.status_code, response.url, response.text)
            else:
                return 1, data, (200, '', '')

        else:
            raise Exception(f'Invalid data type: type={data.get("type")}')


class FieldParser(Parser):
    def __init__(self, company: str, max_deep: int = 2):
        super().__init__(max_deep)
        self.company = company

    def parse(self, priority: int, url: str, data: dict, deep: int, content: tuple):
        *_, html_text = content
        urls = []

        # get all groups' urls, send to task_queue_f
        if data.get('type') == 'field_page':
            field_page = html_text
            soup = BeautifulSoup(field_page, 'lxml')
            dropdown_options = soup.find(id='fld_group').find_all('option')

            for group in dropdown_options:
                group_var = group['value']
                group_name = group.text

                new_data = json.dumps({
                    'type': 'group_page',
                    'group_var': group_var,
                    'group_name': group_name,
                    'save': False
                })
                urls.append((f'https://{self.company}.xplan.iress.com.au/ufield/list_iframe?group={group_var}',
                             new_data,
                             priority + 1))

            stamp = ('Main Field List', datetime.now())
            return 1, urls, stamp

        # get all variables' urls under this group, send to task_queue_f
        if data.get('type') == 'group_page':
            group_page = html_text
            group_name = data.get('group_name')
            soup = BeautifulSoup(group_page, 'lxml')
            all_vars_under_current_group = soup.find('tbody', {'class': 'list2'}).find_all('tr')

            for var_entry in all_vars_under_current_group:
                # for each option's entry ([sub_group] - variable pair),
                # analysis sub_group and variable
                try:
                    var_detail = var_entry.find_all('td')[1:3]
                    var_type = var_detail[-1].text

                    # try if var_type is invalid (type int)
                    try:
                        int(var_type)
                    # exception happens, var_type is not an int, valid
                    except:
                        pass
                    # no exception happens, var_type is an int, invalid, raise exception
                    else:
                        raise Exception

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

                if '/ufield/edit/entity_' in href:
                    usage = f'{href.split("/ufield/edit/entity_")[1].replace("/", ".")}'
                elif '/ufield/edit/entity' in href:
                    usage = f'{href.split("/ufield/edit/entity/")[1]}'
                else:
                    usage = f'{href.split("/ufield/edit/")[1].replace("/", ".")}'

                new_data = copy.deepcopy(data)
                new_data.update({
                    'type': 'var_page',
                    'sub_group': sub_group,
                    'var_type': var_type,
                    'var': var,
                    'var_name': var_name,
                    'usage': usage,
                })

                if var_type == 'Multi' or var_type == 'Choice':
                    new_data.update({'save': False})
                    new_data = json.dumps(new_data)
                    urls.append((
                        f'https://{self.company}.xplan.iress.com.au{href}',
                        new_data,
                        priority + 1))
                else:
                    new_data.update({'save': True, 'multi': None})
                    new_data = json.dumps(new_data)
                    urls.append(('', new_data, priority + 1))

            stamp = (f'Group Page {group_name}', datetime.now())
            return 1, urls, stamp

        # get variable detailed information if type is Multi/Choice
        if data.get('type') == 'var_page':
            var_type = data.get('var_type')
            var_name = data.get('var_name')
            new_data = copy.deepcopy(data)

            # process the html text
            if var_type == 'Multi' or var_type == 'Choice':
                multi_choice_page = html_text
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

                new_data.update({'multi': multi, 'save': True})
                new_data = json.dumps(new_data)

            urls = [('', new_data, priority + 1)]
            stamp = (f'Multi Choice Var {var_name}', datetime.now())
            return 1, urls, stamp

        return 0, [], ()


class FieldSaver(Saver):
    def __init__(self, pipe):
        super().__init__(pipe)
        if isinstance(self.pipe, str):
            self.pipe = f'{self.pipe}.json'

    def save(self, url: str, data, stamp: tuple):
        if isinstance(self.pipe, str):
            with open(self.pipe, 'a') as F:
                F.write(f'{data},\n')

        else:
            try:
                # assume this is a db access instance, e.g. pymongo clientconnect
                pass

            except:
                pass

        return True


def login(username: str, password: str, company: str):
    session = requests.session()
    payload = {
        "userid": username,
        "passwd": password,
        "rolename": "User",
        "redirecturl": ''
    }
    session.post(f'https://{company}.xplan.iress.com.au/home',
                 data=payload,
                 headers={'referer': f'https://{company}.xplan.iress.com.au/home'})
    field_page = session.get(f'https://{company}.xplan.iress.com.au/ufield/list').text
    if re.search(r'permission_error|Login for User', field_page):
        raise Exception(
            'Currently there is another user using this XPLAN account.')

    return session

def logout(session, company: str):
    session.get(f'https://{company}.xplan.iress.com.au/home/logoff?')


if __name__ == "__main__":
    company = 'ytml'
    username = 'ytml2'
    password = 'Passw0rdOCT'
    session = login(username, password, company)

    url = f'https://{company}.xplan.iress.com.au/ufield/list'
    fetcher = FieldFetcher(company)
    parser = FieldParser(company)
    saver = FieldSaver(pipe='tttttttttttt')
    filter = None

    spider = ThreadPool(fetcher, parser, saver, filter, fetcher_num=1)
    spider.run(url, initial_data=json.dumps({'type': 'field_page'}), priority=0, deep=0, session=session)

    logout(session, company)


