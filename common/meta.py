
from selenium import webdriver
from common.crypto import AESCipher

class Meta:
    """
    `company_xxx` variable will be modified when user logged in, and reset
    when logged out, is accessible to all other modules across the application
    """
    company = 'ytml'
    company_username = 'ytmladmin'
    company_password = 'Passw0rdOCT'


    """
    `crypto` variable is an instance for AESCipher
    """
    crypto = AESCipher()


    """
    browser is used for fetch interface menu
    """
    browser = None
    session_id = None
    executor_url = None
    current_url = None
