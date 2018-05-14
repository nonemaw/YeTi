from functools import partial, reduce
from itertools import chain
from typing import Callable, Any, Sequence, Optional, Mapping


class FnChain:
    """
    FnChain(obj).map(...).filter(...).reduce(...)...
    API LIST:
    - foldl/foldr: fold from left/right
    - reduce: foldl alias
    - map
    - filter
    - zip
    - all
    - any
    - first
    - first_not
    - count
    - max
    - min
    - flatten
    """

    def __init__(self, obj):
        try:
            assert obj and isinstance(obj, (list, tuple, str))
        except AssertionError:
            obj = list(obj)  # try cast to list, else raise Error
        self.__ori = obj
        self.__obj = obj.copy() if hasattr(obj, 'copy') else obj

    # collect method
    def foldl(self, f, init=None):
        assert callable(f)
        tmp = partial(reduce, f, self.__obj)
        if init is not None:
            tmp = partial(tmp, init)
        self.__obj = tmp()
        return self.__obj

    def reduce(self, f, init=None):
        return self.foldl(f, init)

    def foldr(self, f, init=None):
        assert callable(f)
        # reversed foldl
        return self.foldl(reversed(self.__obj), init)

    def all(self, f=None) -> bool:
        if not f:
            return all(self.__obj)
        else:
            assert callable(f)
            return all(map(lambda x: f(x), self.__obj))

    def any(self, f=None) -> bool:
        if not f:
            return any(self.__obj)
        else:
            assert callable(f)
            return any(map(lambda x: f(x), self.__obj))

    def first(self, f: Callable[[Any], bool]):
        assert callable(f)
        self.filter(lambda x: f(x))
        for ret in self.__obj:
            return ret
        return None

    def first_index(self, f: Callable[[Any], bool]):
        assert callable(f)
        i = 0
        for item in self.__obj:
            if f(item):
                return i
            i += 1
        return None

    def first_not(self, f: Callable[[Any], bool]):
        assert callable(f)
        self.filter(lambda x: not f(x))
        for ret in self.__obj:
            return ret
        return None

    def first_not_index(self, f: Callable[[Any], bool]):
        assert callable(f)
        i = 0
        for item in self.__obj:
            if not f(item):
                return i
            i += 1
        return None

    def indexes(self, f: Callable[[Any], bool]):
        assert callable(f)
        i = 0
        ret = []
        for item in self.__obj:
            if f(item):
                ret.append(i)
            i += 1
        return ret

    def distinct(self) -> bool:
        if len(set(self.__obj)) != 1:
            return False
        return True

    def count(self) -> int:
        return self.reduce(lambda x, _: x + 1, 0)

    def max(self):
        ret = None
        for o in self.__obj:
            if not ret or ret < o:
                ret = o
        return ret

    def min(self):
        ret = None
        for o in self.__obj:
            if not ret or ret > o:
                ret = o
        return ret

    def sum(self):
        return self.reduce(lambda x, y: x + y)

    def average(self):
        return self.sum() / self.count()

    def execute(self):
        # do nothing, just iterate obj once
        for _ in self.__obj:
            pass
        return None

    def collect(self) -> Sequence:
        return [o for o in self.__obj]

    def split(self, f: Callable[[Any], bool]) -> Sequence:
        assert callable(f)
        ret = []
        tmp = []
        for _ in self.__obj:
            if f(_):
                ret.append(tmp)
                tmp = []
            else:
                tmp.append(_)
        ret.append(tmp)
        return ret

    def flatten(self, layer=1) -> Sequence:
        ret = self.__obj
        for _ in range(layer):
            ret = chain.from_iterable(ret)
        return ret

    def group_by(self,
                 key: Optional[str] = None,
                 attr: Optional[str] = None,
                 f: Optional[Callable[[Any], Any]] = None) -> Mapping:
        if key is None and f is None and attr is None:
            raise ValueError('Either f, attr or key should be set')
        ret = {}  # value => obj
        if key:
            for o in self.__obj:
                target = o[key]
                if target not in ret:
                    ret[target] = []
                ret[target].append(o)
        elif attr:
            for o in self.__obj:
                target = getattr(o, attr)
                if target not in ret:
                    ret[target] = []
                ret[target].append(o)
        else:
            for o in self.__obj:
                target = f(o)
                if target not in ret:
                    ret[target] = []
                ret[target].append(o)
        return ret

    # pipe method
    def map(self, f: object) -> 'FnChain':
        assert callable(f)
        self.__obj = map(f, self.__obj)
        return self

    def filter(self, f) -> 'FnChain':
        assert callable(f)
        self.__obj = filter(f, self.__obj)
        return self

    def non_empty(self) -> 'FnChain':
        return self.filter(lambda x: x)

    def empty(self) -> 'FnChain':
        return self.filter(lambda x: not x)

    def apply(self, f) -> 'FnChain':
        def body(item):
            i_cp = item if not hasattr(item, 'copy') else item.copy()
            f(i_cp)
            return item

        return self.map(body)

    # special function
    def it(self, wrap=False):
        if not wrap:
            return self.__obj.copy()
        return FnChain(self.__obj.copy())

    def ori(self):
        return self.__ori

    def restore(self):
        self.__obj = self.__ori.copy() if hasattr(self.__ori, 'copy') else self.__ori
        return self

    def to_list(self) -> list:
        return list(self.__obj)

    def to_tuple(self) -> tuple:
        return tuple(self.__obj)

    def to_dict(self):
        return dict(self.__obj)