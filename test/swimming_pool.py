from queue import Queue
import inspect
import types
import threading
from contextlib import contextmanager


def singleton(cls, *args, **kwargs):
    instances = {}
    def __singleton():
        ins = instances.get(cls)
        if ins is None:
            ins = cls(*args, **kwargs)
            instances[cls] = ins
        return ins
    return __singleton


class SwimmingPool:
    """
    store objects in a queue to work as a pool for improving performance

    when a classed passed into the constructor, parameters are required too
    """
    pool = dict()

    def __new__(cls, size: int):
        pass

    # def __init__(self, size: int, obj: type, *args, **kwargs):
    #     self.busy_queue = Queue()
    #     self.idle_queue = Queue()
    #     self.size = size
    #     self.__obj = self.__build_instance(obj, *args, **kwargs)
    #     self.args = args

    def __build_instance(self, obj, *args, **kwargs):
        # a class object, build instance
        if isinstance(obj, type):
            return obj(*args, **kwargs)

        # not a class, it can be an instance or something else, forget about
        # the type
        return obj


class ObjectPool:
    def __init__(self, fn_cls, *args, **kwargs):
        super(ObjectPool, self).__init__()
        self.fn_cls = fn_cls
        self._myinit(*args, **kwargs)

    def _myinit(self, *args, **kwargs):
        self.args = args
        self.maxSize = int(kwargs.get("maxSize", 1))
        self.queue = Queue()

    def _get_obj(self):
        # 因为传进来的可能是函数，还可能是类
        if type(self.fn_cls) == types.FunctionType:
            return self.fn_cls(self.args)
        # 判断是经典或者新类
        elif type(self.fn_cls) == types.ClassType or type(
                self.fn_cls) == types.TypeType:
            return apply(self.fn_cls, self.args)
        else:
            raise "Wrong type"

    def borrow_obj(self):
        # 要是对象池大小还没有超过设置的最大数，可以继续放进去新对象
        if self.queue.qsize() < self.maxSize and self.queue.empty():
            self.queue.put(self._get_obj())
        # 都会返回一个对象给相关去用
        return self.queue.get()

    def recover_obj(self, obj):
        self.queue.put(obj)


# 测试用函数和类
def echo_func(num):
    return num


class echo_cls(object):
    pass


# 不用构造含有__enter__, __exit__的类就可以使用with，当然你可以直接把代码放到函数去用
@contextmanager
def poolobj(pool):
    obj = pool.borrow_obj()
    try:
        yield obj
    except Exception as e:
        yield None
    finally:
        pool.recover_obj(obj)


obj = ObjectPool(echo_func, 23, maxSize=4)
obj2 = ObjectPool(echo_cls, maxSize=4)


class MyThread(threading.Thread):
    def run(self):
        # 为了实现效果，我搞了个简单的多线程，2个with放在一个地方了，只为测试用
        with poolobj(obj) as t:
            pass
        with poolobj(obj2) as t:
            pass


if __name__ == '__main__':
    threads = []
    for i in range(200):
        t = MyThread()
        t.start()
        threads.append(t)
    for t in threads:
        t.join(True)