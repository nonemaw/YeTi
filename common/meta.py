from app.db import mongo_connect, client


class Meta:
    """
    `company_xxx` variable will be modified when user logged in, and reset
    when logged out, is accessible to all other modules across the application
    """
    company = 'ytml'
    company_username = 'ytml1'
    company_password = ''

    db_default = mongo_connect(client, 'ytml')
    db_company = None

    # `crypto` variable is an instance for AESCipher
    crypto = None

    # `jison` is an instance of Jison parser
    jison = None

    # `fetchers` are instances of Fetcher/Interface Fetcher
    menu_fetcher = None
    interface_fetcher = None

    # browser is used for fetch interface menu
    browser = None
    session_id = None
    executor_url = None
    current_url = None

    @staticmethod
    def empty(attribute=None):
        """
        empty Meta's all attributes or one/some specific attributes
        """
        if not attribute:
            for attr in filter(
                    lambda x: not x.startswith('__') and
                              not callable(getattr(Meta, x)), dir(Meta)):
                setattr(Meta, attr, None)

        elif isinstance(attribute, str):
            try:
                setattr(Meta, attribute, None)
            except:
                pass

        elif isinstance(attribute, list):
            for attr in attribute:
                try:
                    setattr(Meta, attr, None)
                except:
                    pass
