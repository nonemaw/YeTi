"""
login into a specified XPLAN site, fetch all data to local database
"""
import re
import time
from common.meta import Meta
from selenium import webdriver
from app import celery

subgroup_name_ref = {
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


def login(driver: str = 'phantomjs'):
    if not Meta.browser:
        create_driver(driver)
    Meta.browser.get(f'https://{Meta.company}.xplan.iress.com.au/home')
    Meta.browser.find_element_by_id('userid').send_keys(Meta.company_username)
    Meta.browser.find_element_by_id('passwd').send_keys(Meta.company_password)
    Meta.browser.find_element_by_id('btn_login').click()


def test_login(menu: dict) -> bool:
    Meta.browser.get(
        f'https://{Meta.company}.xplan.iress.com.au/factfind/edit_interface')

    inner_html = Meta.browser.execute_script("return document.body.innerHTML")
    if re.search(r'permission_error', inner_html):
        # login failed
        menu['error'] = \
            'Unable to load Interface View, please ensure the correctness of username/password, and no other is using this account.'
        return False
    return True


def quit_driver(browser):
    browser.get(f'https://{Meta.company}.xplan.iress.com.au/home/logoff?')
    browser.quit()
    Meta.current_url = None
    Meta.session_id = None
    Meta.executor_url = None


# RUN WORKER: celery -A common.interface_fetcher worker --pool=solo -l info
@celery.task(bind=True)
def initialize_interface(self, number: int = 200) -> dict:
    URL_INTERFACE = f'https://{Meta.company}.xplan.iress.com.au/factfind/edit_interface'
    menu = {'data': []}

    # a refresh happens, if cached url is the page interface then restore session
    # and return main menu again
    if Meta.current_url and Meta.current_url == URL_INTERFACE:
        if test_login(menu):
            time.sleep(1)
            for _id in range(1, number):
                self.update_state(state='PROGRESS',
                                  meta={'current': _id + 1, 'total': 100,
                                        'status': 'working'})
                if not get_menu(_id, menu):
                    break

    # a new login session
    else:
        login('chromedriver')
        time.sleep(1)
        if test_login(menu):
            Meta.current_url = URL_INTERFACE
            time.sleep(1)
            for _id in range(1, number):
                self.update_state(state='PROGRESS',
                                  meta={'current': _id + 1, 'total': 100,
                                        'status': 'working'})
                if not get_menu(_id, menu):
                    break

    return {'status': 'Initialization Finished', 'result': menu}


def get_menu(_id: int, menu: dict) -> bool:
    try:
        # find menu item with `hidden` tags
        Meta.browser.find_element_by_xpath(
            f'//*[@id="edit_interface_page"]/div[2]/div[1]/div/div[2]/div/ul/li[{_id}]/a/span[1]/font')
        return True
    except:
        # if there is no `hidden` tags, get id and text
        try:
            menu.get('data').append({'id': Meta.browser.find_element_by_xpath(
                f'//*[@id="edit_interface_page"]/div[2]/div[1]/div/div[2]/div/ul/li[{_id}]').get_attribute(
                'id'),
                'parent': '#',
                'text': Meta.browser.find_element_by_xpath(
                    f'//*[@id="edit_interface_page"]/div[2]/div[1]/div/div[2]/div/ul/li[{_id}]/a/span[1]').text
            })
            return True
        except:
            return False


@celery.task(bind=True)
def update_interface(self, _id: str) -> dict:
    """
    case 1: a sub menu is expanded, return new list of menu
    case 2: a leaf, return content of panel data
    """
    menu = {'data': []}

    # normal node
    if re.search('^client_[0-9]+', _id):
        Meta.browser.find_element_by_xpath(
            f'//*[@id="{_id}"]/a/span[1]').click()
        time.sleep(0.5)

        for child in range(1, 200):
            self.update_state(state='PROGRESS',
                              meta={'current': child + 1, 'total': 100,
                                    'status': 'working'})
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
                        if text != 'Retirement Funds':
                            menu.get('data').append(
                                {'id': element.get_attribute('id'),
                                 'parent': _id,
                                 'text': text
                                 })
                except:
                    break

    # leaf node
    else:
        Meta.browser.find_element_by_xpath(
            f'//*[@id="{_id}"]/a/span[1]').click()
        time.sleep(1)

        name = Meta.browser.find_element_by_xpath(
            '//*[@id="edit_interface_page"]/div[2]/div[3]/div/div[2]/table/tbody/tr[1]/td[2]/div/a/span').text
        if re.findall('\[(.+?)\] (.+)', name):
            name = '--'.join(re.findall('\[(.+?)\] (.+)', name)[0])
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
        menu['leaf_basic'] = content
        content = {name: {'table1': [], 'table2': []}}

        # if content is a XPLAN collection or XPLAN group
        try:
            Meta.browser.find_element_by_xpath(
                '//*[@id="tr_element_xplan_definition"]/td/div/span[1]')
        except:
            pass
        else:
            if name.lower() in subgroup_name_ref:
                menu['subgroup'] = subgroup_name_ref.get(name.lower())
            # table 1
            for i in range(1, 30):
                try:
                    if Meta.browser.find_element_by_xpath(
                            f'//*[@id="xstore_listfields_{i}"]').get_attribute(
                        'checked'):
                        content.get(name).get('table1').append(
                            Meta.browser.find_element_by_xpath(
                                f'//*[@id="tr_element_xplan_definition"]/td/div/span[{i}]/label').text)

                        if Meta.browser.find_element_by_xpath(
                                f'//*[@id="xstore_capturefields_{i}"]').get_attribute(
                            'checked'):
                            content.get(name).get('table2').append(
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
                        content.get(name).get('table2').append(
                            Meta.browser.find_element_by_xpath(
                                f'//*[@id="tr_element_xplan_edit_fields_definition"]/td/div/span[{i}]/label').text)
                except:
                    break

            menu['leaf_collection'] = content

        # if content is a XPLAN collection or XPLAN group
        try:
            Meta.browser.find_element_by_xpath(
                '//*[@id="tr_element_xplan_list_tabs"]/td/div[1]/div[1]/table/tbody[1]/tr[1]')
        except:
            pass
        else:
            if name.lower() in subgroup_name_ref:
                menu['subgroup'] = subgroup_name_ref.get(name.lower())
            # table 1
            for i in range(1, 30):
                try:
                    content.get(name).get('table1').append(
                        Meta.browser.find_element_by_xpath(
                            f'//*[@id="tr_element_xplan_list_tabs"]/td/div[1]/div[1]/table/tbody[1]/tr[{i}]/td[2]').text)
                except:
                    break

            # table 2
            for i in range(1, 30):
                try:
                    content.get(name).get('table2').append(
                        Meta.browser.find_element_by_xpath(
                            f'//*[@id="tr_element_xplan_edit_tabs"]/td/div[1]/div[1]/table/tbody[1]/tr[{i}]/td[2]').text)
                except:
                    break

            menu['leaf_collection'] = content

    # endif
    print(menu)
    return {'status': 'Update Finished', 'result': menu}


def dump_interface():
    pass
