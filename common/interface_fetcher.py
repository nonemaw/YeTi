
"""
login into a specified XPLAN site, fetch all data to local database
"""
import requests
import re
import time
from common import meta
from selenium import webdriver


def initialize_interface() -> list:
    URL_LOGIN = f'https://{meta.company}.xplan.iress.com.au/home'
    URL_LOGOUT = f'https://{meta.company}.xplan.iress.com.au/home/logoff?'
    URL_INTERFACE = f'https://{meta.company}.xplan.iress.com.au/factfind/edit_interface'
    browser = webdriver.PhantomJS(executable_path='./phantomjs')

    try:
        # login payload
        payload = {
            "userid": meta.company_username,
            "passwd": meta.company_password,
            "rolename": "User",
            "redirecturl": ''
        }

        browser.get(URL_LOGIN)
        browser.find_element_by_id('userid').send_keys(payload.get('userid'))
        browser.find_element_by_id('passwd').send_keys(payload.get('passwd'))
        browser.find_element_by_id('btn_login').click()
        print('Logged in, awaiting page being loaded ...')
        time.sleep(1.5)

        browser.get(URL_INTERFACE)
        inner_html = browser.execute_script("return document.body.innerHTML")
        if re.search(r'permission_error', inner_html):
            # login failed
            raise Exception('Currently there is another user using this XPLAN account.')
        else:
            menu = []
            print('Going in, awaiting Interface page being loaded ...')
            time.sleep(1)

            for id in range(99):
                try:
                    browser.find_element_by_xpath(f'//*[@id="client_{id}"]/a/span[1]/font')
                except:
                    try:
                        menu.append({'id': f'client_{str(id)}', 'parent': '#', 'text': browser.find_element_by_xpath(f'//*[@id="client_{id}"]/a/span[1]').text})
                    except Exception as e:
                        print(e)
                        pass

            print(menu)


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

    except Exception as e:
        print(e)
        browser.get(URL_LOGOUT)


if __name__ == '__main__':
    initialize_interface()
