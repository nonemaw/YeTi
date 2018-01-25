from app.db import mongo_connect, client
from common.crypto import AESCipher
from uni_parser.loader import ParserLoader


class Meta:
    db = mongo_connect(client, 'ytml')

    # `crypto` variable is an instance for AESCipher
    crypto = None

    # `parser` is an instance of ParserLoader
    parser = None

    # `fetchers` are instances of Fetcher/Interface Fetcher
    menu_fetcher = None
    interface_fetcher = None

    @staticmethod
    def demolish(attribute=None):
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

    @staticmethod
    def initialize():
        Meta.crypto = AESCipher()
        Meta.parser = ParserLoader(grammar='xplan')
