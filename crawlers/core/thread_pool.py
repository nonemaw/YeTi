import copy
from crawlers.core.thread_types import *


class ThreadPool:
    def __init__(self, fetcher, parser, saver, filter = None, fetcher_num: int = 1):
        self.fetcher = fetcher   # instance of Fetcher (worker)
        self.parser = parser     # instance of Parser (worker)
        self.saver = saver       # instance of Saver (worker)
        self.filter = filter     # instance of Filter (worker)

        self.flag_dict = {
            FLAGS.RUNNING: 0,    # the count of tasks which are running
            FLAGS.FETCH: 0,      # the count of urls which have been fetched successfully
            FLAGS.PARSE: 0,      # the count of urls which have been parsed successfully
            FLAGS.SAVE: 0,       # the count of urls which have been saved successfully
            FLAGS.NOT_FETCH: 0,  # the count of urls which haven't been fetched
            FLAGS.NOT_PARSE: 0,  # the count of urls which haven't been parsed
            FLAGS.NOT_SAVE: 0,   # the count of urls which haven't been saved
        }

        self.task_queue_f = queue.PriorityQueue()
        self.task_queue_p = queue.PriorityQueue()
        self.task_queue_s = queue.Queue()
        self.lock = threading.Lock()
        self.done_counter = 0
        self.fetcher_num = fetcher_num

    def update_flag(self, key, value):
        self.lock.acquire()
        self.flag_dict[key] += value
        self.lock.release()

    def add_task(self, task_name: FLAGS, task_content: tuple):
        '''
        add a task to queue based on name
        task_content is a tuple: (priority, url, data, deep, repeat)

        Queue.put_nowait(item) equals to Queue.put(item, block=False, timeout=None)
        '''
        # add task to fetch queue

        if task_name == FLAGS.FETCH and (not self.filter or self.filter.check_repetition(task_content[1])):
            self.task_queue_f.put(task_content, block=False)
            self.update_flag(FLAGS.NOT_FETCH, 1)

        # add task to parse queue
        elif task_name == FLAGS.PARSE:
            self.task_queue_p.put(task_content, block=False)
            self.update_flag(FLAGS.NOT_PARSE, 1)

        # add task to save queue
        elif task_name == FLAGS.SAVE:
            self.task_queue_s.put(task_content, block=False)
            self.update_flag(FLAGS.NOT_SAVE, 1)

    def get_task(self, task_name: FLAGS) -> tuple:
        '''
        get a task from queue based on name and return content
        task_content is a tuple: (priority, url, data, deep, repeat)

        queue.get(block, timeout):
        Remove and return an item from the queue. If optional args block is
        true and timeout is None (the default), block if necessary until an
        item is available. If timeout is a positive number, it blocks at most
        timeout seconds and raises the Empty exception if no item was available
        within that time. Otherwise (block is false), return an item if one is
        immediately available, else raise the Empty exception (timeout is
        ignored in that case).
        '''

        task_content = None
        # get task from fetch queue
        if task_name == FLAGS.FETCH:
            task_content = self.task_queue_f.get(block=True, timeout=5)
            self.update_flag(FLAGS.NOT_FETCH, -1)
        # get task from parse queue
        elif task_name == FLAGS.PARSE:
            task_content = self.task_queue_p.get(block=True, timeout=5)
            self.update_flag(FLAGS.NOT_PARSE, -1)
        # get task from save queue
        elif task_name == FLAGS.SAVE:
            task_content = self.task_queue_s.get(block=True, timeout=5)
            self.update_flag(FLAGS.NOT_SAVE, -1)

        self.update_flag(FLAGS.RUNNING, 1)
        return task_content

    def finish_task(self, task_name: FLAGS):
        '''
        finish an enqueued task based on name (just tell the queue task is
        done)

        queue.task_done()
        Indicate that a formerly enqueued task is complete. Used by queue
        consumer threads. For each get() used to fetch a task, a subsequent
        call to task_done() tells the queue that the processing on the task is
        complete.
        '''

        if task_name == FLAGS.FETCH:
            self.task_queue_f.task_done()
        elif task_name == FLAGS.PARSE:
            self.task_queue_p.task_done()
        elif task_name == FLAGS.SAVE:
            self.task_queue_s.task_done()
        self.update_flag(FLAGS.RUNNING, -1)

    def all_done(self):
        '''
        check if all tasks are done, when:

        tasks_running == 0
        NOT_FETCH == 0
        NOT_PARSE == 0
        NOT_SAVE == 0
        '''
        done = False if self.flag_dict[FLAGS.RUNNING] \
                     or self.flag_dict[FLAGS.NOT_FETCH] \
                     or self.flag_dict[FLAGS.NOT_PARSE] \
                     or self.flag_dict[FLAGS.NOT_SAVE]\
                     else True

        if done:
            self.done_counter += 1
            # if all fetchers done
            if self.done_counter == self.fetcher_num:
                if isinstance(self.saver.pipe, str):
                    with open(self.saver.pipe, 'a', encoding='utf-8') as F:
                        F.write('  ]\n}\n')

        return done

    def run(self, url: str, initial_data: dict = None, priority: int = 0,
            deep: int = 0, repeat: int = 0, session=None):
        if isinstance(self.saver.pipe, str):
            with open(self.saver.pipe, 'w') as F:
                F.write('{\n  "DATA":\n  [')

        logging.warning(f'{self.__class__.__name__} ThreadPool started: fetcher_num={self.fetcher_num}')

        # push tasks to queue, (priority, url, data, deep, repeat) is a task's content
        self.add_task(FLAGS.FETCH, (priority, url, initial_data, deep, repeat))

        # assume fetcher_num == 10, then:
        # fetcher_thread_list is a list with 10 threads, and each thread has
        # its own instance of Fetcher (self.fetcher)
        fetcher_thread_list = [FetcherThread(f'fetcher_thread-{i + 1}', copy.deepcopy(self.fetcher), self, session) for i in range(self.fetcher_num)]
        parser_saver_thread_list = [ParserThread("parser_thread", self.parser, self), SaverThread("saver_thread", self.saver, self)]

        # run all fetcher threads
        for fetcher_thread in fetcher_thread_list:
            fetcher_thread.daemon = True
            fetcher_thread.start()

        # run parser thread and saver thread
        for p_s_thread in parser_saver_thread_list:
            p_s_thread.daemon = True
            p_s_thread.start()

        # block until all running fetcher threads to finished
        for fetcher_thread in fetcher_thread_list:
            if fetcher_thread.is_alive():
                fetcher_thread.join()

        # if all fetcher threads finished but the NOT_FETCH counter > 0, then
        # clean up the fetch queue
        while self.flag_dict[FLAGS.NOT_FETCH] > 0:
            self.get_task(FLAGS.FETCH)
            self.finish_task(FLAGS.FETCH)

        # block until all running parser/saver threads to finish if they are
        # still not finished
        for p_s_thread in parser_saver_thread_list:
            if p_s_thread.is_alive():
                p_s_thread.join()
