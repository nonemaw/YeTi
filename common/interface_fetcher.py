
"""
login into a specified XPLAN site, fetch all data to local database
"""
import re
import time
from common.meta import Meta
from selenium import webdriver
from app import celery


def quit_driver():
    Meta.browser.get(f'https://{Meta.company}.xplan.iress.com.au/home/logoff?')
    Meta.browser.quit()
    Meta.current_url = None
    Meta.session_id = None
    Meta.executor_url = None

def create_driver():
    Meta.browser = webdriver.Chrome()
    Meta.session_id = Meta.browser.session_id
    Meta.executor_url = Meta.browser.command_executor._url

# RUN WORKER: celery worker -A app.common.interface_fetcher --loglevel=info
@celery.task(bind=True)
def initialize_interface(self, number:int=99) -> dict:
    URL_LOGIN = f'https://{Meta.company}.xplan.iress.com.au/home'
    URL_INTERFACE = f'https://{Meta.company}.xplan.iress.com.au/factfind/edit_interface'
    menu = {'data': []}

    # a refresh happens, if cached url is the page interface, return menu directly
    if Meta.current_url is not None and Meta.current_url == URL_INTERFACE:
        Meta.current_url = f'https://{Meta.company}.xplan.iress.com.au/factfind/edit_interface'
        time.sleep(1)
        for id in range(number):
            self.update_state(state='PROGRESS',
                              meta={'current': id + 1, 'total': number, 'status': 'working'})
            get_menu(id, number, menu)
        return {'status': 'Initialization Finished', 'result': menu}

    else:
        try:
            Meta.browser.get(URL_LOGIN)
        except:
            create_driver()
            Meta.browser.get(URL_LOGIN)

        # try to login
        Meta.browser.find_element_by_id('userid').send_keys(Meta.company_username)
        Meta.browser.find_element_by_id('passwd').send_keys(Meta.company_password)
        Meta.browser.find_element_by_id('btn_login').click()
        time.sleep(1)

        Meta.browser.get(URL_INTERFACE)
        inner_html = Meta.browser.execute_script("return document.body.innerHTML")

        if re.search(r'permission_error', inner_html):
            # login failed
            menu['error'] = 'Unable to load Interface View, please ensure the correctness of username/password, and no other is using this account.'
            return {'status': 'Initialization Finished', 'result': menu}

        else:
            print('Going in, awaiting Interface page being loaded ...')
            Meta.current_url = f'https://{Meta.company}.xplan.iress.com.au/factfind/edit_interface'
            time.sleep(1)
            for id in range(number):
                self.update_state(state='PROGRESS',
                                  meta={'current': id + 1, 'total': number, 'status': 'working'})
                get_menu(id, number, menu)
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


@celery.task(bind=True)
def get_menu(id:int, number:int, menu:dict):
    try:
        # find menu item with `hidden` tags
        Meta.browser.find_element_by_xpath(f'//*[@id="client_{id}"]/a/span[1]/font')
    except:
        # if there is no `hidden` tags, click it
        try:
            menu.get('data').append({'id': f'client_{id}', 'parent': '#', 'text': Meta.browser.find_element_by_xpath(f'//*[@id="client_{id}"]/a/span[1]').text})
        except:
            pass


def refresh_menu(clicked_id:str) -> dict:
    """
    case 1: a sub menu is expanded, return new list of menu
    case 2: a leaf, return content of panel data
    """
    URL_LOGOUT = f'https://{Meta.company}.xplan.iress.com.au/home/logoff?'
    local_browser = webdriver.Remote(command_executor=Meta.executor_url, desired_capabilities={})
    local_browser.session_id = Meta.session_id

    try:
        local_browser.find_element_by_xpath(f'//*[@id="{clicked_id}"]/a/span[1]').click()
        menu = {'data': []}

        for child_id in range(99):
            try:
                local_browser.find_element_by_xpath(f'//*[@id="{clicked_id}-{child_id}"]/a/span[1]/font')
            except:
                try:
                    menu.get('data').append({'id': f'{clicked_id}-{child_id}', 'parent': f'{clicked_id}', 'text': local_browser.find_element_by_xpath(f'//*[@id="{clicked_id}-{child_id}"]/a/span[1]').text})
                except:
                    pass
        return menu

    except Exception as e:
        print(e)
        local_browser.get(URL_LOGOUT)


if __name__ == '__main__':
    from pprint import pprint
    pprint(initialize_interface())
