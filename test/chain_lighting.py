import copy
import inspect
from functools import reduce
from itertools import islice
from reprlib import recursive_repr
from collections import Iterator, Iterable, OrderedDict, Mapping


class OrderedTable(OrderedDict):
    """
    enabling dot operation for dict/OrderedDict
    Example:
    >>> t = OrderedTable({'key1': 1, 'key2': {'key3': 3, 'key4': 4}})
    >>> t.key2.key5 = 5
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.items():
                    self[k] = OrderedTable(v) if isinstance(v, dict) else v

            if kwargs:
                for k, v in kwargs.items():
                    self[k] = OrderedTable(v) if isinstance(v, dict) else v

    @recursive_repr()
    def __repr__(self):
        if not self:
            return 'OrderedTable()'
        return f'OrderedTable({list(self.items())})'

    def __getattr__(self, item):
        """
        enable
        >>> t.key
        """
        return self.get(item)

    def __setattr__(self, key, value):
        """
        enable
        >>> t.key2 = 2
        """
        # convert value to Table type before passing to __setitem__
        if isinstance(value, dict):
            value = OrderedTable(value)
        self.__setitem__(key, value)

    def __delattr__(self, item):
        """
        enable
        >>> del t.key3
        """
        self.__delitem__(item)

    def __setitem__(self, key, value):
        """
        signature not matched, but it works good
        """
        super().__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delitem__(self, key):
        """
        signature not matched, but it works good
        """
        super().__delitem__(key)
        del self.__dict__[key]

    def update(self, m: Mapping = None, **kwargs):
        """
        override dict's update method for Table: when updating mappings,
        convert them into Table first rather than pass dict directly
        """
        if m is not None:
            for k, v in m.items() if isinstance(m, Mapping) else m:
                if isinstance(v, dict):
                    v = OrderedTable(v)
                self[k] = v

        for k, v in kwargs.items():
            if isinstance(v, dict):
                v = OrderedTable(v)
            self[k] = v

    def append_keys(self, keys: Iterable, default=None):
        for k in keys:
            self.update({k: default})

    def append(self, item=None, **kwargs):
        """
        append one or multiple key-value pairs to the end of dict

        the operation will be converted to update() if same key appears
        """
        if item is not None:
            if isinstance(item, list):
                for i in item:
                    self.update(i)
            elif isinstance(item, Mapping):
                self.update(item)

        for k, v in kwargs.items():
            if isinstance(v, dict):
                v = OrderedTable(v)
            self[k] = v

    def extend(self, items:Iterable):
        """
        extend multiple key-value pairs to the end of dict

        the operation will be converted to update() if same key appears
        """
        for i in items:
            self.update(i)


class CL:
    """
    ChainLightning provides convenient function chain mechanisms, which also
    allows you to modify Iterable/Iterator directly at same time
    """

    def __init__(self, obj):
        self.__obj = self.__assert_obj(obj)
        self.__cache = copy.deepcopy(obj)
        if isinstance(obj, Iterator):
            self.type = 1  # type 1 is Iterator
        else:
            self.type = 2  # type 2 is Iterable

    def __iter__(self):
        if self.type == 1:
            return copy.deepcopy(self.__obj)

        return iter(self.__obj)

    def __str__(self):
        if self.type == 1:
            self_obj = str(list(self))
        else:
            self_obj = str(self.__obj)
        self_id = '0x{:02x}'.format(id(self))
        if self.type == 1:
            return f'<ChainLightning at {self_id}> value={self_obj} type=Iterator'
        elif self.type == 2:
            return f'<ChainLightning at {self_id}> value={self_obj} type=Iterable'

        self_type = str(type(self.__obj))
        return f'<ChainLightning at {self_id}> value={self_obj} type={self_type}'

    def __repr__(self):
        return str(self)

    def __len__(self):
        return self.reduce(func=lambda x, _: x + 1, initial=0)

    def __enter__(self):
        return iter(self)

    def __call__(self, func_name: str, *args, **kwargs):
        if hasattr(self, func_name):
            return getattr(self, func_name)(*args, **kwargs)

    def __getitem__(self, item):
        """
        enable
        >>> CL(iter([1, 2, 3, 4, 5]))[::2]
        """
        if not isinstance(item, (int, slice)):
            raise TypeError(
                f'Indices must be an integer or slice, not {type(item)}'
            )

        # Iterable case, pass item directly
        if self.type == 2:
            return self.__obj.__getitem__(item)
        # Iterator case
        elif self.type == 1:
            # slice case, "item" is a built-in slice object
            if isinstance(item, slice):
                res = islice(self, item.start, item.stop, item.step)
                return res
            # int case
            else:
                counter = 0
                for i in self:
                    if counter == item:
                        return i
                    else:
                        counter += 1
                else:
                    raise IndexError('Index out of range')

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

    def __assert_obj(self, obj):
        try:
            assert obj and isinstance(obj, (Iterator, Iterable))
        except AssertionError:
            obj = list(obj)

        if isinstance(obj, dict) and not isinstance(obj, OrderedTable):
            tmp = OrderedTable()
            for key in obj:
                tmp[key] = obj.get(key)
            obj = tmp

        return obj

    def __assert_func(self, func, arg_num: int = None):
        """
        assert whether the "func" is a valid function

        if "arg_num" is given (not None), then assert if func's valid number of
        parameters is legal

        return: func's legal number of arguments
        """
        if not callable(func):
            raise TypeError('Argument "func" got a non-callable object')

        # the given number of arg_num should pass one of the assert()
        if arg_num is not None:
            # _args is the total number of func's arguments
            _args = len(inspect.getfullargspec(func).args)
            # _kwargs is the total number of func's kw-arguments
            try:
                _kwargs = len(inspect.getfullargspec(func).defaults)
            except:
                _kwargs = 0

            try:
                assert _args - _kwargs == arg_num
                return _args - _kwargs
            except AssertionError:
                try:
                    assert _args == arg_num
                    return _args
                except AssertionError:
                    raise TypeError(
                        f'{func.__name__}() takes {_args} args and {_kwargs} kwargs, but expecting {arg_num} args'
                    )

    ###################### tools: ######################
    # length()        -> len(self)
    # done()          -> self.__obj
    # get_iter()      -> Iterator
    # get_reverse()   -> self.__obj
    # get_sort()      -> self.__obj
    # has_duplicate() -> bool
    # check()         -> self.__obj
    def length(self) -> int:
        return len(self)

    def done(self):
        """
        retrieve self.__obj's value when user's operation is done, e.g.:
        CL(xxx).sorted(x).map(x).filter(x).group_by(x).done()
        """
        return self.__obj

    def get_iter(self) -> Iterator:
        """
        obtain an iterator from self
        """
        return iter(self)

    def get_reverse(self):
        """
        obtain a reversed version of current object's value, and it won't
        modify the object's value
        """
        # an Iterable
        if self.type == 2 and not isinstance(self.__obj, dict):
            return reversed(self)
        # an Iterator, not reversible, convert to list for reversed()
        elif self.type == 1 and not isinstance(self.__obj, dict):
            return reversed(list(self))
        # a dict
        elif isinstance(self.__obj, dict):
            # FIXME: why I cannot use reversed(self) in here?
            res = reversed(self.__obj)
            tmp = OrderedTable()
            for key in res:
                tmp[key] = self.__obj.get(key)
            return tmp

    def get_sort(self, key=None, reverse=None):
        """
        obtain a sorted version of current object's value, and it won't
        modify the object's value
        """
        if key:
            self.__assert_func(key, arg_num=1)

        # sorted() with reverse flag
        if reverse is not None and not isinstance(self.__obj, dict):
            if not isinstance(reverse, (bool, int)):
                raise TypeError(
                    f'Argument "reverse" should be in type of bool/int, but got {type(reverse)}'
                )
            return sorted(self, key=key, reverse=reverse)
        # sorted without reverse flag
        elif not reverse and not isinstance(self.__obj, dict):
            return sorted(self, key=key)
        # a dict
        elif isinstance(self.__obj, dict):
            if reverse is not None:
                res = sorted(self, key=key, reverse=reverse)
            else:
                res = sorted(self, key=key)
            tmp = OrderedTable()
            for key in res:
                tmp[key] = self.__obj.get(key)
            return tmp

    def get_rsort(self, key=None):
        """
        obtain a reversely sorted version of current object's value, and it
        won't modify the object's value
        """
        return self.get_sort(key, reverse=True)

    def has_duplicate(self):
        """
        if there exists duplicate items
        """
        return not (len(self) == len(set(self)))

    def check(self, _type=None):
        """
        enable a quick check to __obj's human-readable value
        """
        if self.type == 1:
            if _type is not None and callable(_type):
                return _type(self)
            return list(self)
        else:
            return self.__obj

    ###################### pipelines: ######################
    # map()        -> self
    # zip()        -> self
    # filter()     -> self
    # sorted()     -> self
    # reversed()   -> self
    # flatten()    -> self
    #
    # key_only()   -> self
    # value_only() -> self
    #
    # append()     -> self
    # extend()     -> self
    # insert()     -> self
    # remove()     -> self
    # pop()        -> self
    # update()     -> self
    #
    # reset()      -> self
    def map(self, func) -> 'CL':
        self.__assert_func(func, arg_num=1)
        self.__obj = map(func, self)
        self.__update_type_n_cache()

        return self

    def zip(self, obj=None) -> 'CL':
        """
        zip current object with another Iterator/Iterable or None
        """
        assert isinstance(obj, (Iterator, Iterable))
        self.__obj = zip(self, obj)
        self.__update_type_n_cache()

        return self

    def filter(self, func) -> 'CL':
        self.__assert_func(func, arg_num=1)
        self.__obj = filter(func, self)
        self.__update_type_n_cache()

        return self

    def sorted(self, key=None, reverse=None) -> 'CL':
        """
        doing sorted() operation, and it will modify object's value and
        return self as a pipeline
        """
        if key:
            self.__assert_func(key, arg_num=1)

        # sorted() with reverse flag
        if reverse is not None and not isinstance(self.__obj, dict):
            if not isinstance(reverse, (bool, int)):
                raise TypeError(
                    f'Argument "reverse" should be in type of bool/int, but got {type(reverse)}'
                )
            self.__obj = sorted(self, key=key, reverse=reverse)
        # sorted without reverse flag
        elif not reverse and not isinstance(self.__obj, dict):
            self.__obj = sorted(self, key=key)
        # a dict
        elif isinstance(self.__obj, dict):
            if reverse is not None:
                res = sorted(self, key=key, reverse=reverse)
            else:
                res = sorted(self, key=key)
            tmp = OrderedTable()
            for key in res:
                tmp[key] = self.__obj.get(key)
            self.__obj = tmp
        self.__update_type_n_cache()

        return self

    def rsorted(self, key=None) -> 'CL':
        return self.sorted(key, reverse=True)

    def reversed(self) -> 'CL':
        """
        doing reversed() operation, and it will modify object's value and
        return itself as a pipeline
        """
        # an Iterable
        if self.type == 2 and not isinstance(self.__obj, dict):
            # FIXME: why I cannot use reversed(self) in here?
            self.__obj = reversed(self.__obj)
        # an Iterator, not reversible, convert to list for reversed()
        elif self.type == 1 and not isinstance(self.__obj, dict):
            self.__obj = reversed(list(self))
        # a dict
        elif isinstance(self.__obj, dict):
            # FIXME: why I cannot use reversed(self) in here?
            res = reversed(self.__obj)
            tmp = OrderedTable()
            for key in res:
                tmp[key] = self.__obj.get(key)
            self.__obj = tmp
        self.__update_type_n_cache()

        return self

    def __flatten(self, obj):
        for i in obj:
            if isinstance(i, Iterable) and not isinstance(i, (str, bytes)):
                yield from self.__flatten(i)
            else:
                yield i

    def flatten(self) -> 'CL':
        """
        make object "flat" and return itself as a pipeline

        CL([1,2,[3,4,[5,6],7,[8,9]]]).flatten() => CL([1,2,3,4,5,6,7,8,9])
        """
        self.__obj = iter([_ for _ in self.__flatten(self)])
        self.__update_type_n_cache()
        return self

    def key_only(self) -> 'CL':
        """
        only work when object's value is a dict and return itself as a pipeline
        """
        if isinstance(self.__obj, dict):
            self.__obj = [_ for _ in self]
            self.__update_type_n_cache()

        return self

    def value_only(self) -> 'CL':
        """
        only work when object's value is a dict and return itself as a pipeline
        """
        if isinstance(self.__obj, dict):
            self.__obj = [self.__obj.get(_) for _ in self]
            self.__update_type_n_cache()

        return self

    def append(self, item) -> 'CL':
        """
        append an item to the end of Iterable/Iterator/Dict
        """
        # an Iterable or a dict
        if self.type == 2:
            self.__obj.append(item)
        # an Iterator
        elif self.type == 1:
            tmp = list(self.__obj)
            tmp.append(item)
            self.__obj = iter(tmp)

        return self

    def extend(self, items) -> 'CL':
        """
        extend a list of items to the end of Iterable/Iterator/Dict
        """
        if not isinstance(items, (list, tuple, dict)):
            try:
                items = list(items)
            except:
                return self

        # an Iterable or a dict
        if self.type == 2:
            self.__obj.extend(items)
        # an Iterator
        elif self.type == 1:
            tmp = list(self.__obj)
            tmp.extend(items)
            self.__obj = iter(tmp)

        return self

    def insert(self) -> 'CL':
        """
        insert an item to designated position of Iterable/Iterator/Dict
        """
        return self

    def remove(self) -> 'CL':
        """
        remove an item from designated position of Iterable/Iterator/Dict
        """
        return self

    def pop(self) -> 'CL':
        """
        pop an item from designated position of Iterable/Iterator/Dict
        """
        return self

    def update(self) -> 'CL':
        """
        update an item to designated position of Iterable/Iterator/Dict
        """
        return self

    def reset(self, obj=None) -> 'CL':
        """
        reset object's value if error occurs

        e.g.:
        >>> t = CL([1,2,3])
        >>> t.map(lambda x: x[0])
        >>> print(t)
        it will continuously raise TypeError whenever you call the object, as
        closure of map() only invokes when object is being called, the wrong
        lambda function will be stored in memory until the map iterator has
        been consumed

        in this case use reset() to reset object's value
        """
        self.__obj = self.__assert_obj(obj)
        self.__update_type_n_cache()
        return self

    ###################### basic operations: ######################
    # any()    -> res
    # all()    -> res
    # reduce() -> res
    # foldl()  -> res
    # foldr()  -> res
    def any(self, func=None) -> bool:
        if not func:
            res = any(self)
        else:
            self.__assert_func(func, arg_num=1)
            res = any(map(func, self))

        return res

    def all(self, func=None) -> bool:
        if not func:
            res = all(self)
        else:
            self.__assert_func(func, arg_num=1)
            res = all(map(func, self))

        return res

    def reduce(self, func, initial=None):
        """
        reduce / foldl method
        """
        self.__assert_func(func, arg_num=2)

        return reduce(func, self, initial)

    def fold_left(self, func, initial=None):
        return self.reduce(func, initial)

    def foldl(self, func, initial=None):
        return self.reduce(func, initial)

    def fold_right(self, func, initial=None):
        """
        r_reduce / foldr method
        """
        self.__assert_func(func, arg_num=2)

        return reduce(func, self.reversed(), initial)

    def foldr(self, func, initial=None):
        return self.fold_right(func, initial)

    ###################### math operations: ######################
    # sum()     -> res
    # average() -> res
    # max()     -> res
    # min()     -> res
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

        if "min" is set to True, then it will return a minimum value
        """
        res = None
        cmp = None

        if func is not None:
            self.__assert_func(func, arg_num=1)
        else:
            func = lambda x: x

        for item in self:
            try:
                if res is None and cmp is None:
                    res = item
                    cmp = func(item)
                else:
                    new_cmp = func(item)
                    if min:
                        if new_cmp < cmp:
                            res = item
                            cmp = new_cmp
                    else:
                        if new_cmp > cmp:
                            res = item
                            cmp = new_cmp
            except:
                return None

        return res

    def min(self, func=None):
        """
        can accept a function as argument for comparing a "min" value

        e.g.: min(func=lambda x: len(x)) for find the shortest string in an
        Iterator/Iterable
        """
        return self.max(func=func, min=True)

    ###################### advance operations: ######################
    # sort_by()
    # group_by()
    # count_by()
    # distinct_by()
    # flatten()
    # first()
    # first_not()
    def sort_by(self):
        pass

    def group_by(self, key, attr, func):
        if key is None and func is None and attr is None:
            raise ValueError(
                'CL.group_by() should accept at least one argument')

        res = {}
        if key:
            pass
        elif attr:
            pass
        else:
            pass

        return res

    def count_by(self):
        pass

    def distinct_by(self):
        pass


if __name__ == '__main__':
    t = CL([1,2,3,4,5])
    t.append('fdsafsdfdsf')
    print(t)
