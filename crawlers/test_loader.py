from crawlers.core.workers import Fetcher, Parser, Saver, Filter
from crawlers.core.thread_pool import ThreadPool

"""
看一下这个 500L 的异步（非线程）爬虫架构

https://github.com/HT524/500LineorLess_CN/blob/master/%E9%AB%98%E6%95%88%E7%88%AC%E8%99%AB%E4%B8%8E%E5%8D%8F%E7%A8%8B%20A%20Web%20Crawler%20With%20asyncio%20Coroutines/%E9%AB%98%E6%95%88%E7%88%AC%E8%99%AB%E4%B8%8E%E5%8D%8F%E7%A8%8B.md
"""


if __name__ == "__main__":
    url = "https://www.jetbrains.com/help/pycharm/commenting-and-uncommenting-blocks-of-code.html"
    fetcher = Fetcher()
    parser = Parser(max_deep=2)
    saver = Saver(pipe='test_result')
    filter = Filter(bloom_capacity=1000)

    spider = ThreadPool(fetcher, parser, saver, filter, fetcher_num=10)
    spider.run(url, None, priority=0, deep=0)
