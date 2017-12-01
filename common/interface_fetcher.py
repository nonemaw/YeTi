
"""
login into a specified XPLAN site, fetch all data to local database
"""
import re
import time
from common.meta import Meta
from selenium import webdriver
from app import celery

def login():
    if not Meta.browser:
        create_driver()
    Meta.browser.get(f'https://{Meta.company}.xplan.iress.com.au/home')
    Meta.browser.find_element_by_id('userid').send_keys(Meta.company_username)
    Meta.browser.find_element_by_id('passwd').send_keys(Meta.company_password)
    Meta.browser.find_element_by_id('btn_login').click()

def test_login(menu:dict) -> bool:
    Meta.browser.get(f'https://{Meta.company}.xplan.iress.com.au/factfind/edit_interface')
    inner_html = Meta.browser.execute_script("return document.body.innerHTML")
    if re.search(r'permission_error', inner_html):
        # login failed
        menu['error'] = 'Unable to load Interface View, please ensure the correctness of username/password, and no other is using this account.'
        return False
    return True

def quit_driver(browser):
    browser.get(f'https://{Meta.company}.xplan.iress.com.au/home/logoff?')
    browser.quit()
    Meta.current_url = None
    Meta.session_id = None
    Meta.executor_url = None

def create_driver():
    if not Meta.session_id and not Meta.executor_url:
        Meta.browser = webdriver.Chrome()
        Meta.browser = Meta.browser
        Meta.session_id = Meta.browser.session_id
        Meta.executor_url = Meta.browser.command_executor._url
    elif Meta.session_id and Meta.executor_url:
        Meta.browser = webdriver.Remote(command_executor=Meta.executor_url, desired_capabilities={})
        Meta.browser.session_id = Meta.session_id
    else:
        return None

# RUN WORKER: celery -A common.interface_fetcher worker --pool=solo -l info
@celery.task(bind=True)
def initialize_interface(self, number:int=99) -> dict:
    URL_INTERFACE = f'https://{Meta.company}.xplan.iress.com.au/factfind/edit_interface'
    menu = {'data': []}

    # a refresh happens, if cached url is the page interface then restore session
    # and return main menu again
    if Meta.current_url and Meta.current_url == URL_INTERFACE:
        if test_login(menu):
            time.sleep(1.5)
            for _id in range(number):
                self.update_state(state='PROGRESS',
                                  meta={'current': _id + 1, 'total': number, 'status': 'working'})
                get_menu(_id, number, menu)

    else:
        login()
        time.sleep(1)
        if test_login(menu):
            print('Going in, awaiting Interface page being loaded ...')
            Meta.current_url = URL_INTERFACE
            time.sleep(1.5)
            for _id in range(number):
                self.update_state(state='PROGRESS',
                                  meta={'current': _id + 1, 'total': number, 'status': 'working'})
                get_menu(_id, number, menu)

    return {'status': 'Initialization Finished', 'result': menu}
        # for id in range(100):
        #     try:
        #         # find hidden tag
        #         browser.find_element_by_xpath(f'//*[@id="client_{id}"]/a/span[1]/font')
        #     except:
        #         # if no hidden tag, perform click operation
        #         try:
        #             browser.find_element_by_xpath(f'//*[@id="client_{id}"]/a/span[1]').click()
        #         except:
        #             pass
        #         else:
        #             time.sleep(0.1)
        #             # on click success, keep clicking children
        #             for child in range(100):
        #                 try:
        #                     # find hidden tag
        #                     browser.find_element_by_xpath(f'//*[@id="client_{id}-{child}"]/a/span[1]/font')
        #                 except:
        #                     # if no hidden tag, perform click operation on child
        #                     try:
        #                         browser.find_element_by_xpath(f'//*[@id="client_{id}-{child}"]/a/span[1]').click()
        #                     except:
        #                         pass
        #                     else:
        #                         time.sleep(0.1)
        #                         # on click success, keep clicking sub children
        #                         for sub in range(50):
        #                             try:
        #                                 # find hidden tag
        #                                 browser.find_element_by_xpath(f'//*[@id="client_{id}-{child}-{sub}"]/a/span[1]/font')
        #                             except:
        #                                 # if no hidden tag, perform click operation on sub child
        #                                 try:
        #                                     browser.find_element_by_xpath(f'//*[@id="client_{id}-{child}-{sub}"]/a/span[1]').click()
        #                                 except:
        #                                     pass
        #                                 else:
        #                                     time.sleep(0.1)
        #                             else:
        #                                 pass
        #                 else:
        #                     pass
        #     else:
        #         pass
        #
        # inner_html = browser.execute_script("return document.body.innerHTML")
        # print(inner_html)

def get_menu(_id:int, number:int, menu:dict):
    try:
        # find menu item with `hidden` tags
        Meta.browser.find_element_by_xpath(f'//*[@id="client_{_id}"]/a/span[1]/font')
    except:
        # if there is no `hidden` tags, click it
        try:
            menu.get('data').append({'id': f'client_{_id}',
                                     'parent': '#',
                                     'text': Meta.browser.find_element_by_xpath(f'//*[@id="client_{_id}"]/a/span[1]').text})
        except:
            pass


@celery.task(bind=True)
def update_interface(self, _id:str, number:int=99) -> dict:
    """
    case 1: a sub menu is expanded, return new list of menu
    case 2: a leaf, return content of panel data
    """
    menu = {'data': []}
    Meta.browser.find_element_by_xpath(f'//*[@id="{_id}"]/a/span[1]').click()
    time.sleep(1)

    for child in range(number):
        self.update_state(state='PROGRESS',
                          meta={'current': child + 1, 'total': number, 'status': 'working'})
        try:
            # find hidden tag
            Meta.browser.find_element_by_xpath(f'//*[@id="{_id}-{child}"]/a/span[1]/font')
        except:
            # if no hidden tag, perform click operation on child
            try:
                menu.get('data').append({'id': f'{_id}-{child}',
                                         'parent': f'{_id}',
                                         'text': Meta.browser.find_element_by_xpath(f'//*[@id="{_id}-{child}"]/a/span[1]').text})
            except:
                pass

    return {'status': 'Update Finished', 'result': menu}


if __name__ == '__main__':
    from pprint import pprint
    pprint(initialize_interface())
