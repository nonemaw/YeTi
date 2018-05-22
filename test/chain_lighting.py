import copy
import inspect
from functools import reduce
from collections import Iterator, Iterable, OrderedDict


class CL:
    def __init__(self, obj):
        try:
            assert obj and isinstance(obj, (Iterator, Iterable)), 'Invalid object for ChainLightning to work'
        except AssertionError:
            obj = list(obj)

        if isinstance(obj, dict) and not isinstance(obj, OrderedDict):
            tmp = OrderedDict()
            for key in obj:
                tmp[key] = obj.get(key)
            obj = tmp

        self.__obj = obj
        self.__cache = copy.deepcopy(obj)
        if isinstance(obj, Iterator):
            self.type = 1  # type 1 is Iterator
        else:
            self.type = 2  # type 2 is Iterable

    def __iter__(self):
        if self.type == 1:
            return self.__obj

        return iter(self.__obj)

    def __str__(self):
        self_obj = str(self.__obj)
        self_obj_type = str(type(self.__obj))
        self_id = '0x{:02x}'.format(id(self))
        if self.type == 1:
            return f'<ChainLightning object at {self_id}>, value={self_obj}, type=1<Iterator>'
        elif self.type == 2:
            return f'<ChainLightning object at {self_id}>, value={self_obj}, type=2<Iterable>'

        return f'<ChainLightning object at {self_id}>, value={self_obj}, type=0<{self_obj_type}>'

    def __repr__(self):
        return str(self)

    def __len__(self):
        length = self.reduce(func=lambda x, _: x + 1, initial=0)
        self.__restore_from_cache()
        return length

    def __enter__(self):
        return iter(self)

    def __update_type_n_cache(self):
        """
        after some operations an Iterator or Iterable might be converted
        between each other, try to update type/cache after those changes
        """
        self.__cache = copy.deepcopy(self.__obj)
        if isinstance(self.__obj, Iterator):
            self.type = 1
        elif isinstance(self.__obj, Iterable):
            self.type = 2
        else:
            self.type = 0

    def __restore_from_cache(self):
        """
        restore from cache for Iterators
        """
        if self.type == 1:
            self.__obj = copy.deepcopy(self.__cache)

    def __assert_func(self, func, arg_num: int = None):
        """
        assert whether the "func" is a valid function

        if "arg_num" is given (not None), then assert if func's valid number of
        parameters is legal

        return: func's legal number of arguments
        """
        assert callable(func), 'Parameter "func" got a non-callable object'
        # _args is the total number of func's arguments
        _args = len(inspect.getfullargspec(func).args)
        # _kwargs is the total number of func's kw-arguments
        try:
            _kwargs = len(inspect.getfullargspec(func).defaults)
        except:
            _kwargs = 0

        # the given number of arg_num should pass one of the assert()
        if arg_num is not None:
            try:
                assert _args - _kwargs == arg_num
                return _args - _kwargs
            except AssertionError:
                assert _args == arg_num
                return _args

    # def __build_lambda(self, func, arg_num: int = None):
    #     arg_num = self.__assert_func(func, arg_num)
    #
    #     if arg_num == 0:
    #         return lambda a, b, c: func()
    #     elif arg_num == 1:
    #         return lambda a, b, c: func(a)
    #     elif arg_num == 2:
    #         return lambda a, b, c: func(a, b)
    #     elif arg_num == 3:
    #         return lambda a, b, c: func(a, b, c)
    #     else:
    #         raise TypeError('Function can only has 3 arguments at most')

    # property tools:
    # reverse()
    # sort()
    # rsort()
    # length()
    # done() -> self.__obj
    # iter() -> iter(self.__obj)
    @property
    def reverse(self):
        return self.reversed().done

    @property
    def sort(self):
        return self.sorted().done

    @property
    def rsort(self):
        return self.sorted(reverse=True).done

    @property
    def length(self) -> int:
        return len(self)

    @property
    def done(self):
        """
        retrieve self.__obj's value when user's operation is done, e.g.:
        CL(xxx).sorted(x).map(x).foldl(x).filter(x).group_by(x).done
        """
        return self.__obj

    @property
    def iter(self) -> Iterator:
        """
        obtain an iterator from self
        """
        return iter(self)

    # basic operations:
    # any() -> res
    # all() -> res
    #
    # map() -> self
    # filter() -> self
    # sorted() -> self
    # reversed() -> self
    #
    # reduce() -> res
    # foldl() -> res
    # foldr() -> res
    def any(self, func=None) -> bool:
        if not func:
            res = any(self.__obj)
        else:
            self.__assert_func(func, arg_num=1)
            res = any(map(func, self.__obj))
        self.__restore_from_cache()

        return res

    def all(self, func=None) -> bool:
        if not func:
            res = all(self.__obj)
        else:
            self.__assert_func(func, arg_num=1)
            res = all(map(func, self.__obj))
        self.__restore_from_cache()

        return res

    def map(self, func) -> 'CL':
        self.__assert_func(func, arg_num=1)
        self.__obj = map(func, self.__obj)
        self.__update_type_n_cache()

        return self

    def filter(self, func) -> 'CL':
        self.__assert_func(func, arg_num=1)
        self.__obj = filter(func, self.__obj)
        self.__update_type_n_cache()

        return self

    def sorted(self, key=None, reverse=None) -> 'CL':
        """
        doing sorted() operation, but will modify self.__obj's value and return
        self for further possible operations, using "done" to retrieve result
        value
        """
        if key:
            self.__assert_func(key, arg_num=1)

        if reverse is not None and not isinstance(self.__obj, dict):
            assert isinstance(reverse, (bool, int)), f'Argument "reverse" should be in type of bool/int, but got {type(reverse)}'
            self.__obj = sorted(self.__obj, key=key, reverse=reverse)
        elif reverse and not isinstance(self.__obj, dict):
            self.__obj = sorted(self.__obj, key=key)
        elif isinstance(self.__obj, dict):
            if reverse is not None:
                res = sorted(self.__obj, key=key, reverse=reverse)
            else:
                res = sorted(self.__obj, key=key)
            tmp = OrderedDict()
            for key in res:
                tmp[key] = self.__obj.get(key)
            self.__obj = tmp
        self.__update_type_n_cache()

        return self

    def reversed(self) -> 'CL':
        """
        doing reversed() operation, but will modify self.__obj's value and
        return self for further possible operations, using "done" to retrieve
        result value
        """
        if self.type == 2 and not isinstance(self.__obj, dict):
            self.__obj = reversed(self.__obj)
        elif self.type == 1 and not isinstance(self.__obj, dict):
            # iterator is not reversible, convert to list for reversed()
            self.__obj = reversed(list(self.__obj))
        elif isinstance(self.__obj, dict):
            res = reversed(self.__obj)
            tmp = OrderedDict()
            for key in res:
                tmp[key] = self.__obj.get(key)
            self.__obj = tmp
        self.__update_type_n_cache()

        return self

    def reduce(self, func, initial=None):
        """
        reduce / foldl method
        """
        self.__assert_func(func, arg_num=2)

        if initial is None:
            res = reduce(func, self.__obj)
        else:
            res = reduce(func, self.__obj, initial)
        self.__restore_from_cache()

        return res

    def fold_left(self, func, initial=None):
        return self.reduce(func, initial)

    def foldl(self, func, initial=None):
        return self.reduce(func, initial)

    def fold_right(self, func, initial=None):
        """
        r_reduce / foldr method
        """
        self.__assert_func(func, arg_num=2)

        if initial is None:
            res = reduce(func, self.reversed())
        else:
            res = reduce(func, self.reversed(), initial)
        self.__restore_from_cache()

        return res

    def foldr(self, func, initial=None):
        return self.fold_right(func, initial)

    # math operations:
    # sum() -> res
    # average() -> res
    # max() -> res
    # min() -> res
    def sum(self):
        try:
            return self.reduce(func=lambda x, y: x + y)
        except:
            return None

    def average(self):
        sum = self.sum()
        if isinstance(sum, (int, float, complex)):
            return sum / len(self)
        else:
            return None

    def max(self, func=None, min: bool = False):
        """
        can accept a function as argument for comparing a "max" value

        e.g.: max(func=lambda x: len(x)) for find the longest string in an
        Iterator/Iterable
        """
        res = None
        tmp = None

        if func is not None:
            self.__assert_func(func, arg_num=1)
        else:
            func = lambda x: x

        for item in self.__obj:
            try:
                if res is None and tmp is None:
                    res = item
                    tmp = func(item)
                else:
                    if min:
                        res = item if func(item) < tmp else res
                    else:
                        res = item if func(item) > tmp else res
            except:
                res = None
                break
        self.__restore_from_cache()

        return res

    def min(self, func=None):
        """
        can accept a function as argument for comparing a "min" value

        e.g.: min(func=lambda x: len(x)) for find the shortest string in an
        Iterator/Iterable
        """
        return self.max(func=func, min=True)

    # advancing operations:
    # sort_by()
    # group_by()
    # count_by()
    # distinct_by()
    def sort_by(self):
        pass

    def group_by(self, func):
        pass

    def count_by(self):
        pass

    def distinct_by(self):
        pass
