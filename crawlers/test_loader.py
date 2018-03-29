from crawlers.core.workers import Fetcher, Parser, Saver, Filter
from crawlers.core.thread_pool import ThreadPool


if __name__ == "__main__":
    url = "https://www.jetbrains.com/help/pycharm/commenting-and-uncommenting-blocks-of-code.html"
    fetcher = Fetcher()
    parser = Parser(max_deep=2)
    saver = Saver(pipe='test_result')
    filter = Filter(bloom_capacity=1000)

    spider = ThreadPool(fetcher, parser, saver, filter, fetcher_num=10)
    spider.run(url, None, priority=0, deep=0)
