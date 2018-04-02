import re
import time
import logging
import requests
from datetime import datetime
import random
import pybloom_live
from crawlers.core.config import get_url_legal, make_random_useragent,\
    CONFIG_URLPATTERN_ALL


# workers will be put into corresponding thread for executing, they are:
# fetcher, parser, saver and filter


class Fetcher:
    def __init__(self, max_repeat: int = 3, sleep_time: int = 0):
        self.max_repeat = max_repeat
        self.sleep_time = sleep_time

    def fetch(self, url:str, data: dict, session):
        """
        a base case of fetching page text

        <rewritable>
        """
        if session is not None:
            response = session.get(url, headers={'User-Agent': make_random_useragent(), 'Accept-Encoding': 'gzip'}, timeout=(3.05, 10))
        else:
            response = requests.get(url, headers={'User-Agent': make_random_useragent(), 'Accept-Encoding': 'gzip'}, timeout=(3.05, 10))

        return 1, data, (response.status_code, response.url, response.text)

    def working(self, url: str, data: dict, repeat: int, session=None):
        '''
        -1 (fetch failed and reach max_repeat),
         0 (need repeat),
         1 (fetch success)
        '''
        logging.warning(f'{self.__class__.__name__} work: data={data}, repeat={repeat}, url={url}')

        # sleep for a random time if data or data's 'save' are negative
        if not data or not data.get('save'):
            time.sleep(random.randint(0, self.sleep_time))

        try:
            fetch_result, data, content = self.fetch(url, data, session)
        except Exception as e:
            import sys, os
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(f'{self.__class__.__name__} end: error={str(e)}, file={str(fname)}, line={str(exc_tb.tb_lineno)}')

            if repeat >= self.max_repeat:
                fetch_result, content = -1, None
            else:
                fetch_result, content = 0, None

        logging.warning(f'{self.__class__.__name__} end: fetch_result={fetch_result}, url={url}')

        return fetch_result, data, content


class Parser:
    def __init__(self, max_deep: int = -1):
        self.max_deep = max_deep

    def parse(self, priority: int, url: str, data: dict, deep: int, content: tuple):
        '''
        a base case of getting all urls from current page text

        A <a href> attribute specifies the link's destination, e.g:
            <a href='https://www.sample.com'>Visitor</a>

        content: (status_code, url, html_text)
        stamp: (title, timestamp)

        <rewritable>
        '''
        *_, html_text = content
        urls = []

        if(self.max_deep < 0) or (deep < self.max_deep):
            hrefs = re.findall(r'<a[\w\W]+?href="(?P<url>[\w\W]{5,}?)"[\w\W]*?>[\w\W]+?</a>', html_text, flags=re.IGNORECASE)
            urls = [(_url, data, priority + 1) for _url in [get_url_legal(href, url) for href in hrefs]]

        title = re.search(r'<title>(?P<title>[\w\W]+?)</title>', html_text, flags=re.IGNORECASE)
        stamp = (title.group('title').strip(), datetime.now()) if title else ()

        return 1, urls, stamp

    def working(self, priority: int, url: str, data: dict, deep: int, content: tuple):

        logging.warning(f'{self.__class__.__name__} work: priority={priority}, data={data}, deep={deep}, url={url}')

        try:
            parse_result, urls, stamp = self.parse(priority, url, data, deep, content)
        except:
            parse_result, urls, stamp = -1, [], ()

        logging.warning(f'{self.__class__.__name__} end: parse_result={parse_result}, len(urls)={len(urls)}, len(stamp)={len(stamp)}, url={url}')

        return parse_result, urls, stamp


class Saver:
    def __init__(self, pipe):
        self.pipe = pipe

    def save(self, url: str, data, stamp: tuple):
        """
        a base case of saving data into file or somewhere else

        stamp: (title_of_page, parsed_timestamp)

        <rewritable>
        """
        if isinstance(self.pipe, str):
            stamp_temp = [i for i in stamp]
            stamp_temp[0] = re.sub(r' +', ' ', re.sub(r'&nbsp;|\n', '', stamp_temp[0]))
            with open(self.pipe + '.json', 'a', encoding='utf-8') as F:
                F.write(f'    {{\n      "URL":"{url}",\n      "TITLE":"{stamp_temp[0]}",\n      "TIME":"{stamp_temp[1]}"\n    }},\n')

        else:
            try:
                # assume this is a db access instance, e.g. pymongo clientconnect
                pass

            except:
                pass

        return True

    def working(self, url: str, data, stamp: tuple):
        logging.warning(f'{self.__class__.__name__} work: data={data}, url={url}')

        try:
            save_result = self.save(url, data, stamp)
        except:
            save_result = False

        return save_result


class Filter:
    def __init__(self, black=(CONFIG_URLPATTERN_ALL,), white=('^http',), bloom_capacity: int = 0):
        self.black_list = [re.compile(pattern, flags=re.IGNORECASE) for pattern in black] if black else []
        self.white_list = [re.compile(pattern, flags=re.IGNORECASE) for pattern in white] if white else []

        # if bloom_capacity > 0, use bloom filter, else use set
        self.url_set = set() if not bloom_capacity else None
        self.bloom_filter = pybloom_live.ScalableBloomFilter(bloom_capacity, error_rate=0.001) if bloom_capacity else None

    def check(self, url: str):
        for b in self.black_list:
            if b.search(url):
                return False

        for w in self.white_list:
            if w.search(url):
                return True

    def update(self, urls: list):
        # set case
        if self.url_set is not None:
            self.url_set.update(urls)

        # bloom filter case
        else:
            for url in urls:
                self.bloom_filter.add(url)

    def check_repetition(self, url: str):
        check_result = False
        if self.check(url):
            if self.url_set is not None:
                check_result = (url not in self.url_set)
                self.url_set.add(url)

            else:
                check_result = (not self.bloom_filter.add(url))

        return check_result
