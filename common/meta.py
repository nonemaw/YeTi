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

    # `fetcher` is an instance of Fetcher/Interface Fetcher
    fetcher = None
    interface_fetcher = None

    # browser is used for fetch interface menu
    browser = None
    session_id = None
    executor_url = None
    current_url = None

    statistic = {}
