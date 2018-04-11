import queue
import json
import logging
import threading
from crawlers.core.flags import FLAGS


class BaseThread(threading.Thread):
    def __init__(self, name: str, worker, pool):
        threading.Thread.__init__(self, name=name)
        self._worker = worker     # can be a Fetcher/Parser/Saver instance
        self._thread_pool = pool  # ThreadPool

    def running(self):
        return

    def run(self):
        logging.warning(f'{self.__class__.__name__}[{self.getName()}] started...')

        while True:
            try:
                # keep running self.working() and checking result
                # break (terminate) thread when self.working() failed
                # break (terminate) thread when queue is empty, and all jobs
                # are done
                if not self.running():
                    break
            except queue.Empty:
                if self._thread_pool.all_done():
                    break
            except Exception as e:
                import sys, os
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                logging.warning(f'{self.__class__.__name__} end: error={str(e)}, file={str(fname)}, line={str(exc_tb.tb_lineno)}')

                break

        logging.warning(f'{self.__class__.__name__}[{self.getName()}] ended...')


class FetcherThread(BaseThread):
    def __init__(self, name: str, worker, pool, session=None):
        super().__init__(name, worker, pool)
        self.session = session

    def running(self):
        """
        invoke Fetcher's working()

        content: (status_code, url, html_text)
        """
        priority, url, data, deep, repeat = self._thread_pool.get_task(FLAGS.FETCH)
        try:
            data = json.loads(data)
        except:
            data = {}
        fetch_result, data, content = self._worker.working(url, data, repeat, self.session)

        # fetch success, update FETCH counter, add task to task_queue_p, for
        # parser's further process
        if isinstance(data, dict):
            data = json.dumps(data)
        if fetch_result == 1:
            self._thread_pool.update_flag(FLAGS.FETCH, 1)
            self._thread_pool.put_task(FLAGS.PARSE, (priority, url, data, deep, content))

        # fetch failed, put back to task_queue_f and repeat later
        elif fetch_result == 0:
            self._thread_pool.put_task(FLAGS.FETCH, (priority + 1, url, data, deep, repeat + 1))

        # current round of fetcher is done, notify task_queue_f with
        # task_done() to stop block
        self._thread_pool.finish_task(FLAGS.FETCH)
        return False if fetch_result == -1 else True


class ParserThread(BaseThread):
    def __init__(self, name: str, worker, pool):
        super().__init__(name, worker, pool)

    def running(self):
        """
        invoke Parser's working()

        get all required urls from target html text

        content: (status_code, url, html_text)
        """
        priority, url, data, deep, content = self._thread_pool.get_task(FLAGS.PARSE)
        try:
            data = json.loads(data)
        except:
            data = {}
        parse_result = 1
        urls = []
        stamp = ()

        # if data is negative or data has a negative 'save' value, parse the
        # html, otherwise skip
        if not data or not data.get('save'):
            parse_result, urls, stamp = self._worker.working(priority, url, data, deep, content)

        if parse_result > 0:
            self._thread_pool.update_flag(FLAGS.PARSE, 1)

            # add each url in urls list into task_queue_f, waiting for
            # fetcher's further process
            for _url, _data, _priority in urls:
                if isinstance(_data, dict):
                    _data = json.dumps(_data)
                self._thread_pool.put_task(FLAGS.FETCH, (_priority, _url, _data, deep + 1, 0))

            # add current url (already fetched/parsed) into task_queue_s,
            # waiting for saver's further process
            #
            # if data in task_queue_p has a positive 'save' value, or no data but with an url
            if (data and data.get('save')) or (not data and url):
                try:
                    # when saving to task_queue_s, delete 'save' key
                    del data['save']
                    del data['type']
                    data = json.dumps(data)
                except:
                    pass
                self._thread_pool.put_task(FLAGS.SAVE, (url, data, stamp))

        # current round of parser is done, notify task_queue_p with
        # task_done() to stop block
        self._thread_pool.finish_task(FLAGS.PARSE)
        return True


class SaverThread(BaseThread):
    def __init__(self, name: str, worker, pool):
        super().__init__(name, worker, pool)

    def running(self):
        """
        invoke Saver's working()
        """
        url, data, stamp = self._thread_pool.get_task(FLAGS.SAVE)
        save_result = self._worker.working(url, data, stamp)

        if save_result:
            self._thread_pool.update_flag(FLAGS.SAVE, 1)

        # current round of saver is done, notify task_queue_s with
        # task_done() to stop block
        self._thread_pool.finish_task(FLAGS.SAVE)
        return True
