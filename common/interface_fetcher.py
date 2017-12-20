"""
login into a specified XPLAN site, fetch all interface data to local database
"""
import re
import time
from common.meta import Meta
from selenium import webdriver
# from app import celery
from app.models import InterfaceNode, InterfaceLeafPage



# # RUN WORKER: celery -A common.interface_fetcher worker --pool=solo -l info
# @celery.task(bind=True)
# def initialize_interface(self) -> dict:
#     URL_INTERFACE = f'https://{Meta.company}.xplan.iress.com.au/factfind/edit_interface'
#     menu = {'data': []}
#
#     # a refresh happens, if cached url is the page interface then restore session
#     # and return main menu again
#     if Meta.current_url and Meta.current_url == URL_INTERFACE:
#         if test_login(menu=menu):
#             time.sleep(1)
#             for _id in range(1, 200):
#                 self.update_state(state='PROGRESS',
#                                   meta={'current': _id + 1, 'total': 100,
#                                         'status': 'working'})
#                 if not get_menu(_id, menu):
#                     break
#
#     # a new login session
#     else:
#         login('chromedriver')
#         time.sleep(1)
#         if test_login(menu=menu):
#             Meta.current_url = URL_INTERFACE
#             time.sleep(1)
#             for _id in range(1, 200):
#                 self.update_state(state='PROGRESS',
#                                   meta={'current': _id + 1, 'total': 100,
#                                         'status': 'working'})
#                 if not get_menu(_id, menu):
#                     break
#
#     return {'status': 'Initialization Finished', 'result': menu}
#
#
# def get_menu(_id: int, menu: dict or list) -> bool:
#     try:
#         # find menu item with `hidden` tags
#         Meta.browser.find_element_by_xpath(
#             f'//*[@id="edit_interface_page"]/div[2]/div[1]/div/div[2]/div/ul/li[{_id}]/a/span[1]/font')
#         return True
#     except:
#         # if there is no `hidden` tags, get id and text
#         try:
#             if isinstance(menu, list):
#                 menu.append({
#                     'id': Meta.browser.find_element_by_xpath(f'//*[@id="edit_interface_page"]/div[2]/div[1]/div/div[2]/div/ul/li[{_id}]').get_attribute('id'),
#                     'text': Meta.browser.find_element_by_xpath(f'//*[@id="edit_interface_page"]/div[2]/div[1]/div/div[2]/div/ul/li[{_id}]/a/span[1]').text,
#                     'type': 'root',
#                 })
#             else:
#                 menu.get('data').append({
#                     'id': Meta.browser.find_element_by_xpath(f'//*[@id="edit_interface_page"]/div[2]/div[1]/div/div[2]/div/ul/li[{_id}]').get_attribute('id'),
#                     'parent': '#',
#                     'text': Meta.browser.find_element_by_xpath(f'//*[@id="edit_interface_page"]/div[2]/div[1]/div/div[2]/div/ul/li[{_id}]/a/span[1]').text
#                 })
#             return True
#         except:
#             return False
#
#
# subgroup_name_ref = {
#     'telephone/email list': 'Contact',
#     'address list': 'Address',
#     'employment': 'Employment',
#     'dependent': 'Dependent',
#     'goals': 'Goals',
#     'income': 'Cashflow',
#     'expense': 'Cashflow',
#     'asset list': 'Balance Sheet-Asset',
#     'liability list': 'Balance Sheet-Liability',
#     'existing funds': 'Superannuation-Plans',
#     'retirement income': 'Retirement Income',
#     'bank details': 'Bank',
#     'insurance group': 'Insurance Group',
#     'insurance group by cover': 'Insurance Group',
#     'general insurance policies': 'Risk',
#     'medical insurance': 'Medical Insurance',
# }
#
#
# @celery.task(bind=True)
# def update_interface(self, _id: str, sleep: int = 1) -> dict or list:
#     """
#     case 1: a sub menu is expanded, return new list of menu
#     case 2: a leaf, return content of panel data
#     """
#     menu = {'data': []}
#
#     # normal node
#     if re.search('^client_[0-9]+', _id):
#         Meta.browser.find_element_by_xpath(f'//*[@id="{_id}"]/a/span[1]').click()
#         time.sleep(sleep)
#
#         for child in range(1, 200):
#             self.update_state(state='PROGRESS',
#                               meta={'current': child + 1, 'total': 100,
#                                     'status': 'working'})
#             try:
#                 # find hidden tag
#                 Meta.browser.find_element_by_xpath(
#                     f'//*[@id="{_id}"]/ul/li[{child}]/a/span[1]/font')
#             except:
#                 try:
#                     element = Meta.browser.find_element_by_xpath(
#                         f'//*[@id="{_id}"]/ul/li[{child}]')
#
#                     if not re.search('(_gap|_title)',
#                                      element.get_attribute('rel')):
#
#                         text = Meta.browser.find_element_by_xpath(
#                             f'//*[@id="{_id}"]/ul/li[{child}]/a/span[1]').text
#                         if text != 'Retirement Funds':
#                             menu.get('data').append({
#                                 'id': element.get_attribute('id'),
#                                 'parent': _id,
#                                 'text': text
#                             })
#                 except:
#                     break
#     # leaf node
#     else:
#         menu = handle_leaf(_id, sleep)
#     # endif
#     return {'status': 'Update Finished', 'result': menu}
#
#
# def handle_leaf(_id: str, sleep: int = 2) -> dict:
#     Meta.browser.find_element_by_xpath(
#         f'//*[@id="{_id}"]/a/span[1]').click()
#     time.sleep(sleep)
#     menu = {}
#
#     name = Meta.browser.find_element_by_xpath(
#         '//*[@id="edit_interface_page"]/div[2]/div[3]/div/div[2]/table/tbody/tr[1]/td[2]/div/a/span').text
#     if re.findall('\[(.+?)\] (.+)', name):
#         name = '--'.join(re.findall('\[(.+?)\] (.+)', name)[0])
#     content = {name: []}
#
#     if Meta.browser.find_element_by_xpath(
#             '//*[@id="entity_types_1"]').get_attribute('checked'):
#         content.get(name).append('individual')
#     if Meta.browser.find_element_by_xpath(
#             '//*[@id="entity_types_2"]').get_attribute('checked'):
#         content.get(name).append('superfund')
#     if Meta.browser.find_element_by_xpath(
#             '//*[@id="entity_types_3"]').get_attribute('checked'):
#         content.get(name).append('partnership')
#     if Meta.browser.find_element_by_xpath(
#             '//*[@id="entity_types_4"]').get_attribute('checked'):
#         content.get(name).append('trust')
#     if Meta.browser.find_element_by_xpath(
#             '//*[@id="entity_types_5"]').get_attribute('checked'):
#         content.get(name).append('company')
#     menu['leaf_basic'] = content
#
#     # if content is a Group
#     content = {'group': []}
#     try:
#         Meta.browser.find_element_by_xpath(
#             '//*[@id="tab-general"]/table/tbody/tr[2]/td[1]')
#     except:
#         pass
#     else:
#         for i in range(2, 50):
#             try:
#                 if Meta.browser.find_element_by_xpath(
#                         f'//*[@id="tab-general"]/table/tbody/tr[{i}]/td[2]/input').get_attribute(
#                     'checked'):
#                     content.get('group').append(
#                         Meta.browser.find_element_by_xpath(
#                             f'//*[@id="tab-general"]/table/tbody/tr[{i}]/td[1]').text)
#             except:
#                 break
#         menu['leaf_group'] = content
#
#     # if content is a XPLAN collection, type 1
#     content = {'table1': [], 'table2': []}
#     try:
#         Meta.browser.find_element_by_xpath(
#             '//*[@id="tr_element_xplan_definition"]/td/div/span[1]')
#     except:
#         pass
#     else:
#         if name.lower() in subgroup_name_ref:
#             menu['subgroup'] = subgroup_name_ref.get(name.lower())
#         # table 1
#         for i in range(1, 30):
#             try:
#                 if Meta.browser.find_element_by_xpath(
#                         f'//*[@id="xstore_listfields_{i}"]').get_attribute(
#                     'checked'):
#                     content.get('table1').append(
#                         Meta.browser.find_element_by_xpath(
#                             f'//*[@id="tr_element_xplan_definition"]/td/div/span[{i}]/label').text)
#
#                     if Meta.browser.find_element_by_xpath(
#                             f'//*[@id="xstore_capturefields_{i}"]').get_attribute(
#                         'checked'):
#                         content.get('table2').append(
#                             Meta.browser.find_element_by_xpath(
#                                 f'//*[@id="tr_element_xplan_edit_fields_definition"]/td/div/span[{i}]/label').text)
#             except:
#                 break
#
#         # table 2
#         for i in range(1, 30):
#             try:
#                 if Meta.browser.find_element_by_xpath(
#                         f'//*[@id="xstore_capturefields_{i}"]').get_attribute(
#                     'checked'):
#                     content.get('table2').append(
#                         Meta.browser.find_element_by_xpath(
#                             f'//*[@id="tr_element_xplan_edit_fields_definition"]/td/div/span[{i}]/label').text)
#             except:
#                 break
#
#         menu['leaf_xplan'] = content
#
#     # if content is a XPLAN collection, type 2
#     try:
#         Meta.browser.find_element_by_xpath(
#             '//*[@id="tr_element_xplan_list_tabs"]/td/div[1]/div[1]/table/tbody[1]/tr[1]')
#     except:
#         pass
#     else:
#         if name.lower() in subgroup_name_ref:
#             menu['subgroup'] = subgroup_name_ref.get(name.lower())
#         # table 1
#         for i in range(1, 50):
#             try:
#                 content.get('table1').append(
#                     Meta.browser.find_element_by_xpath(
#                         f'//*[@id="tr_element_xplan_list_tabs"]/td/div[1]/div[1]/table/tbody[1]/tr[{i}]/td[2]').text)
#             except:
#                 break
#
#         # table 2
#         for i in range(1, 50):
#             try:
#                 content.get('table2').append(
#                     Meta.browser.find_element_by_xpath(
#                         f'//*[@id="tr_element_xplan_edit_tabs"]/td/div[1]/div[1]/table/tbody[1]/tr[{i}]/td[2]').text)
#             except:
#                 break
#
#         menu['leaf_xplan'] = content
#
#     return menu


class InterfaceFetcher:
    def __init__(self, add_on: dict = None):
        self.subgroup_name_ref = {
            'telephone/email list': 'Contact',
            'address list': 'Address',
            'employment': 'Employment',
            'dependent': 'Dependent',
            'goals': 'Goals',
            'income': 'Cashflow',
            'expense': 'Cashflow',
            'asset list': 'Balance Sheet-Asset',
            'liability list': 'Balance Sheet-Liability',
            'existing funds': 'Superannuation-Plans',
            'retirement income': 'Retirement Income',
            'bank details': 'Bank',
            'insurance group': 'Insurance Group',
            'insurance group by cover': 'Insurance Group',
            'general insurance policies': 'Risk',
            'medical insurance': 'Medical Insurance',
        }
        if add_on:
            self.subgroup_name_ref.update(add_on)

    @staticmethod
    def create_driver(driver: str = 'phantomjs'):
        # new driver
        if not Meta.session_id and not Meta.executor_url:
            if driver == 'phantomjs':
                Meta.browser = webdriver.PhantomJS(
                    executable_path='common/phantomjs')
            else:
                Meta.browser = webdriver.Chrome(
                    executable_path='common/chromedriver')

            Meta.session_id = Meta.browser.session_id
            Meta.executor_url = Meta.browser.command_executor._url

        # resume session
        elif Meta.session_id and Meta.executor_url:
            Meta.browser = webdriver.Remote(command_executor=Meta.executor_url,
                                            desired_capabilities={})
            Meta.browser.session_id = Meta.session_id
        else:
            return None

    @staticmethod
    def login(driver: str = 'phantomjs'):
        if not Meta.browser:
            InterfaceFetcher.create_driver(driver)
        Meta.browser.get(f'https://{Meta.company}.xplan.iress.com.au/home')
        try:
            Meta.browser.find_element_by_id('userid').send_keys(
                Meta.company_username)
            Meta.browser.find_element_by_id('passwd').send_keys(
                Meta.company_password)
            Meta.browser.find_element_by_id('btn_login').click()
        except:
            Meta.browser.find_element_by_id('username').send_keys(
                Meta.company_username)
            Meta.browser.find_element_by_id('password').send_keys(
                Meta.company_password)
            Meta.browser.find_element_by_xpath('//*[@id="xiled-page-content"]/div/form/div[2]/input').click()
        finally:
            return

    def test_login(menu: dict = None, dump: bool = False) -> bool:
        Meta.browser.get(
            f'https://{Meta.company}.xplan.iress.com.au/factfind/edit_interface')

        inner_html = Meta.browser.execute_script(
            "return document.body.innerHTML")
        if re.search(r'permission_error', inner_html):
            # login failed
            if not dump:
                menu['error'] = 'Unable to load Interface View, please ensure the correctness of username/password, and no other is using this account.'

            return False
        return True

    @staticmethod
    def quit_driver():
        Meta.browser.get(
            f'https://{Meta.company}.xplan.iress.com.au/home/logoff?')
        Meta.browser.quit()
        Meta.current_url = None
        Meta.session_id = None
        Meta.executor_url = None

    def fetch(self, sleep: int = 1, text: str = None,
              driver: str = 'chromedriver'):
        URL_INTERFACE = f'https://{Meta.company}.xplan.iress.com.au/factfind/edit_interface'
        menu = []

        InterfaceFetcher.login(driver)
        time.sleep(1)

        if InterfaceFetcher.test_login(dump=True):
            Meta.current_url = URL_INTERFACE
            time.sleep(1)

            for _id in range(1, 200):
                if not self.get_menu(_id, menu):
                    break

        for node in menu:
            _id = node.get('id')
            if text and text.lower() in node.get('text').lower():
                node['children'] = self.r_dump_interface(_id, sleep)
                InterfaceNode(node).new(force=True)
            elif text:
                continue

            node['children'] = self.r_dump_interface(_id, sleep)
            InterfaceNode(node).new(force=True)

    def get_menu(self, _id: int, menu: dict or list) -> bool:
        try:
            # find menu item with `hidden` tags
            Meta.browser.find_element_by_xpath(
                f'//*[@id="edit_interface_page"]/div[2]/div[1]/div/div[2]/div/ul/li[{_id}]/a/span[1]/font')
            return True
        except:
            # if there is no `hidden` tags, get id and text
            try:
                if isinstance(menu, list):
                    menu.append({
                        'id': Meta.browser.find_element_by_xpath(f'//*[@id="edit_interface_page"]/div[2]/div[1]/div/div[2]/div/ul/li[{_id}]').get_attribute('id'),
                        'text': Meta.browser.find_element_by_xpath(f'//*[@id="edit_interface_page"]/div[2]/div[1]/div/div[2]/div/ul/li[{_id}]/a/span[1]').text,
                        'type': 'root',
                    })
                else:
                    menu.get('data').append({
                        'id': Meta.browser.find_element_by_xpath(f'//*[@id="edit_interface_page"]/div[2]/div[1]/div/div[2]/div/ul/li[{_id}]').get_attribute('id'),
                        'parent': '#',
                        'text': Meta.browser.find_element_by_xpath(f'//*[@id="edit_interface_page"]/div[2]/div[1]/div/div[2]/div/ul/li[{_id}]/a/span[1]').text
                    })
                return True
            except:
                return False

    def r_dump_interface(self, _id: str, sleep: int = 1) -> list:
        id_list = []
        # getting children when a node is not a leaf
        if re.search('^client_[0-9]+', _id):
            try:
                Meta.browser.find_element_by_xpath(
                    f'//*[@id="{_id}"]/a/span[1]').click()
                time.sleep(2)
            except:
                return id_list

            for child in range(1, 200):
                try:
                    # find hidden tag
                    Meta.browser.find_element_by_xpath(
                        f'//*[@id="{_id}"]/ul/li[{child}]/a/span[1]/font')
                except:
                    try:
                        element = Meta.browser.find_element_by_xpath(
                            f'//*[@id="{_id}"]/ul/li[{child}]')

                        if not re.search('(_gap|_title)',
                                         element.get_attribute('rel')):

                            text = Meta.browser.find_element_by_xpath(
                                f'//*[@id="{_id}"]/ul/li[{child}]/a/span[1]').text
                            child_id = element.get_attribute('id'),

                            # something is wrong with page `Retirement Funds`,
                            # skipped other wise page crashed

                            if text != 'Retirement Funds':
                                child_list = self.r_dump_interface(child_id[0], sleep=sleep)
                                # if child is empty, process leaf page
                                if not child_list:
                                    leaf_type = self.dump_page(child_id[0], text)
                                    if leaf_type:
                                        id_list.append({
                                            'id': child_id[0],
                                            'text': text,
                                            'type': leaf_type,
                                        })
                                else:
                                    id_list.append({
                                        'id': child_id[0],
                                        'text': text,
                                        'type': 'root',
                                        'children': child_list
                                    })
                    except:
                        break
        return id_list

    def dump_page(self, _id: str, text: str, sleep: int = 3) -> str:
        """
        called in `r_dump_interface()` when an empty list returned (current
        node is a leaf), dump page content to database
        """
        try:
            Meta.browser.find_element_by_xpath(
                f'//*[@id="{_id}"]/a/span[1]').click()
        except:
            return ''

        time.sleep(sleep)
        page = {}
        leaf_type = 'other'

        try:
            name = Meta.browser.find_element_by_xpath(
                '//*[@id="edit_interface_page"]/div[2]/div[3]/div/div[2]/table/tbody/tr[1]/td[2]/div/a/span').text
            if re.findall('\[(.+?)\] (.+)', name):
                name = '--'.join(re.findall('\[(.+?)\] (.+)', name)[0])
                leaf_type = 'variable'
        except:
            name = '(Empty)'
        content = {name: []}

        if Meta.browser.find_element_by_xpath(
                '//*[@id="entity_types_1"]').get_attribute('checked'):
            content.get(name).append('individual')
        if Meta.browser.find_element_by_xpath(
                '//*[@id="entity_types_2"]').get_attribute('checked'):
            content.get(name).append('superfund')
        if Meta.browser.find_element_by_xpath(
                '//*[@id="entity_types_3"]').get_attribute('checked'):
            content.get(name).append('partnership')
        if Meta.browser.find_element_by_xpath(
                '//*[@id="entity_types_4"]').get_attribute('checked'):
            content.get(name).append('trust')
        if Meta.browser.find_element_by_xpath(
                '//*[@id="entity_types_5"]').get_attribute('checked'):
            content.get(name).append('company')
        page['leaf_basic'] = content

        # if content is a Group
        content = {'group': []}
        try:
            Meta.browser.find_element_by_xpath(
                '//*[@id="tab-general"]/table/tbody/tr[2]/td[1]')
        except:
            pass
        else:
            for i in range(2, 50):
                try:
                    if Meta.browser.find_element_by_xpath(
                            f'//*[@id="tab-general"]/table/tbody/tr[{i}]/td[2]/input').get_attribute(
                        'checked'):
                        content.get('group').append(
                            Meta.browser.find_element_by_xpath(
                                f'//*[@id="tab-general"]/table/tbody/tr[{i}]/td[1]').text)
                except:
                    break
            page['leaf_group'] = content
            leaf_type = 'group'

        # if content is a XPLAN collection, type 1
        content = {'table1': [], 'table2': []}
        try:
            Meta.browser.find_element_by_xpath(
                '//*[@id="tr_element_xplan_definition"]/td/div/span[1]')
        except:
            pass
        else:
            if name.lower() in self.subgroup_name_ref:
                page['subgroup'] = self.subgroup_name_ref.get(name.lower())
            # table 1
            for i in range(1, 30):
                try:
                    if Meta.browser.find_element_by_xpath(
                            f'//*[@id="xstore_listfields_{i}"]').get_attribute(
                        'checked'):
                        content.get('table1').append(
                            Meta.browser.find_element_by_xpath(
                                f'//*[@id="tr_element_xplan_definition"]/td/div/span[{i}]/label').text)

                        if Meta.browser.find_element_by_xpath(
                                f'//*[@id="xstore_capturefields_{i}"]').get_attribute(
                            'checked'):
                            content.get('table2').append(
                                Meta.browser.find_element_by_xpath(
                                    f'//*[@id="tr_element_xplan_edit_fields_definition"]/td/div/span[{i}]/label').text)
                except:
                    break

            # table 2
            for i in range(1, 30):
                try:
                    if Meta.browser.find_element_by_xpath(
                            f'//*[@id="xstore_capturefields_{i}"]').get_attribute(
                        'checked'):
                        content.get('table2').append(
                            Meta.browser.find_element_by_xpath(
                                f'//*[@id="tr_element_xplan_edit_fields_definition"]/td/div/span[{i}]/label').text)
                except:
                    break

            page['leaf_xplan'] = content
            leaf_type = 'xplan'

        # if content is a XPLAN collection, type 2
        try:
            Meta.browser.find_element_by_xpath(
                '//*[@id="tr_element_xplan_list_tabs"]/td/div[1]/div[1]/table/tbody[1]/tr[1]')
        except:
            pass
        else:
            if name.lower() in self.subgroup_name_ref:
                page['subgroup'] = self.subgroup_name_ref.get(name.lower())
            # table 1
            for i in range(1, 50):
                try:
                    content.get('table1').append(
                        Meta.browser.find_element_by_xpath(
                            f'//*[@id="tr_element_xplan_list_tabs"]/td/div[1]/div[1]/table/tbody[1]/tr[{i}]/td[2]').text)
                except:
                    break

            # table 2
            for i in range(1, 50):
                try:
                    content.get('table2').append(
                        Meta.browser.find_element_by_xpath(
                            f'//*[@id="tr_element_xplan_edit_tabs"]/td/div[1]/div[1]/table/tbody[1]/tr[{i}]/td[2]').text)
                except:
                    break

            page['leaf_xplan'] = content
            leaf_type = 'xplan'

        InterfaceLeafPage(_id, text, page).new()
        return leaf_type

    def update_node(self, name: str, include_page: bool = False):
        node_dict = InterfaceNode.search({'text': name})
        if not node_dict:
            node_dict = InterfaceLeafPage.search({'text': name})

        if node_dict:
            _id = node_dict.get('id')

            # refresh child list
            if node_dict.get('type') == 'root':


                # refresh child list, and if nodes in child list are leaves,
                # refresh all leaves' page content
                if include_page:
                    pass


            # refresh a leaf's page
            elif node_dict.get('type') == 'child':
                pass

    def update_leaf_page(self, _id: str):
        pass

    def delete_node(self, name):
        pass
