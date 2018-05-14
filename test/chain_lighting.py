import copy
import inspect
from functools import partial, reduce
from collections import Iterator, Iterable


class CL:
    def __init__(self, obj):
        try:
            assert obj and isinstance(obj, (Iterator, Iterable)), 'Invalid object for ChainLighting to work'
        except AssertionError:
            obj = list(obj)

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
        self_id = '0x{:02x}'.format(id(self))
        if self.type == 1:
            return f'<ChainLighting object at {self_id}>, value={self.__obj}, type=Iterator'
        elif self.type == 2:
            return f'<ChainLighting  object at {self_id}>, value={self.__obj}, type=Iterable'

        return f'<ChainLighting  object at {self_id}>, value={self.__obj}, type={type(self.__obj)}'

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
        after some operations an Iterator and Iterable might be converted
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
        parameters is larger or equal then the given one

        return: func's real number of parameters
        """
        assert callable(func), 'Parameter "func" got a non-callable object'
        num = len(inspect.getfullargspec(func).args)
        # the given number of arguments "arg_num" must be -le the real number
        if arg_num is not None:
            assert num >= arg_num

        return num

    def __build_lambda(self, func, arg_num: int = None):
        arg_num = self.__assert_func(func, arg_num)

        if arg_num == 0:
            return lambda a, b, c: func()
        elif arg_num == 1:
            return lambda a, b, c: func(a)
        elif arg_num == 2:
            return lambda a, b, c: func(a, b)
        elif arg_num == 3:
            return lambda a, b, c: func(a, b, c)
        else:
            raise TypeError('Function can only has 3 arguments at most')

    # tools:
    # reverse() -> self
    # length()
    # done() -> self.__obj
    # iter() -> iter(self.__obj)
    @property
    def reverse(self) -> 'Chain':
        return self.reversed()

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
            res = any(map(func, self.__obj))
        self.__restore_from_cache()

        return res

    def all(self, func=None) -> bool:
        if not func:
            res = all(self.__obj)
        else:
            res = all(map(func, self.__obj))
        self.__restore_from_cache()

        return res

    def map(self, func) -> 'Chain':
        self.__assert_func(func, arg_num=1)
        self.__obj = map(func, self.__obj)
        self.__update_type_n_cache()

        return self

    def filter(self, func) -> 'Chain':
        self.__assert_func(func, arg_num=1)
        self.__obj = filter(func, self.__obj)
        self.__update_type_n_cache()

        return self

    def sorted(self, key=None, reverse=None) -> 'Chain':
        """
        doing sorted() operation, but will modify self.__obj's value and return
        self for further possible operations, using "done" to retrieve result
        value
        """
        if key:
            self.__assert_func(key, arg_num=1)

        if reverse is not None:
            assert isinstance(reverse, (bool, int)), f'Argument "reverse" should be in type of bool/int, but got {type(reverse)}'
            self.__obj = sorted(self.__obj, key=key, reverse=reverse)
        else:
            self.__obj = sorted(self.__obj, key=key)
        self.__update_type_n_cache()

        return self

    def reversed(self) -> 'Chain':
        """
        doing reversed() operation, but will modify self.__obj's value and
        return self for further possible operations, using "done" to retrieve
        result value
        """
        if self.type == 2:
            self.__obj = reversed(self.__obj)
        elif self.type == 1:
            self.__obj = iter(reversed(list(self.__obj)))
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
        return self.reduce(func=lambda x, y: x + y)

    def average(self):
        return self.sum() / len(self)

    # advancing operations:
    # sort_by()
    # group_by()
    # count_by()
    # distinct_by()
    def sort_by(self):
        pass

    def group_by(self, func):
        pass
