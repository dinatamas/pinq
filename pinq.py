"""LINQ syntax and functionality implemented in Python."""


import functools
import itertools


##############
# EXCEPTIONS #
##############


class NoElementsError(Exception):
    pass


class NoMatchError(Exception):
    pass


class OutOfRangeError(Exception):
    pass


class UnsupportedIteratedTypeError(Exception):
    pass


########
# PINQ #
########


class Pinq:
    """The core class for PINQ."""

    def __init__(self, iterable):
        if not hasattr(iterable, '__iter__'):
            raise TypeError('A Pinq object must be created from an iterable.')
        self._iterable = iterable
    
    ### ITERABILITY ###

    def __iter__(self):
        return iter(self._iterable)
    
    ### LINQ METHODS ###

    def aggregate(self, func, seed=None, resultSelector=None):
        """
        https://docs.microsoft.com/en-us/dotnet/api/system.linq.enumerable.aggregate
        https://github.com/dotnet/runtime/blob/master/src/libraries/System.Linq/src/System/Linq/Aggregate.cs

        functools.reduce implements the core functionality of this method
        perfectly and is implemented in C.
        """
        try:
            result = functools.reduce(func, self._iterable, seed)
        except TypeError:
            raise NoElementsError(
                'Called Pinq.aggregate() on empty iterable without seed.'
            )
        if resultSelector is None:
            return result
        else:
            return resultSelector(result)
    
    def all(self, predicate):
        """
        https://docs.microsoft.com/en-us/dotnet/api/system.linq.enumerable.all
        https://github.com/dotnet/runtime/blob/master/src/libraries/System.Linq/src/System/Linq/AnyAll.cs

        All and map are builtins (implemented in C). Using map instead of a
        list comprehension is preferable because map returns a generator.
        """
        return all(map(predicate, self._iterable))
    
    def any(self, predicate=None):
        """
        https://docs.microsoft.com/en-us/dotnet/api/system.linq.enumerable.any
        https://github.com/dotnet/runtime/blob/master/src/libraries/System.Linq/src/System/Linq/AnyAll.cs

        Any and map are builtins (implemented in C). Using map instead of a
        list comprehension is preferable because map returns a generator.
        """
        if predicate is None:
            return any(self._iterable)
        else:
            return any(map(predicate, self._iterable))
    
    def append(self, element):
        """
        https://docs.microsoft.com/en-us/dotnet/api/system.linq.enumerable.append
        https://github.com/dotnet/runtime/blob/master/src/libraries/System.Linq/src/System/Linq/AppendPrepend.cs
        https://github.com/dotnet/runtime/blob/master/src/libraries/System.Linq/src/System/Linq/AppendPrepend.SpeedOpt.cs

        Since an out-of-place solution is required it's not efficient to
        produce a new iterable (in any way) but rather to chain two iterables.
        itertools.chain serves that purpose perfectly, and is implemented in C.
        """
        return Pinq(itertools.chain(self._iterable, [element]))
    
    ### AsEnumerable is not required for Python! Yay!

    def average(self, func=None):
        """
        https://docs.microsoft.com/en-us/dotnet/api/system.linq.enumerable.average
        https://github.com/dotnet/runtime/blob/master/src/libraries/System.Linq/src/System/Linq/Average.cs

        There's no straightforward builtin solution for this. Summation could
        be executed efficiently with the sum builtin, but average also needs a
        count. Many collections have the __len__ method, but not all iterables,
        so average cant't rely on that. It is still attempted for the potential
        performance gain. For best performance summing and counting should be
        performed in the same loop.

        The len method shouldn't be used! Because if the len is implemented by
        the class by looping through and counting, the worst case scenario
        requires us to loop through twice. Since one loop is definitely
        required (because of the summation), the overhead of increasing a
        counter is relatively small compared to the overhead of double looping.
        """
        if not any(self._iterable):
            raise NoElementsError('Called Pinq.average() on empty iterable.')
        try:
            c = len(self._iterable)
        except TypeError:
            it = iter(self._iterable)
            c = 1
            if func is None:
                s = next(it)
                for e in it:
                    try: s = s + e
                    except TypeError: s = s + float(e)
                    except ValueError: raise UnsupportedIteratedTypeError(
                        'Pinq.average() requires number-like iterated types that'
                        ' support addition and division by int or can be'
                        ' converted to float.'
                    )
                    c += 1
            else:
                s = func(next(it))
                for e in it:
                    try: s = s + func(e)
                    except TypeError: s = s + float(func(e))
                    except ValueError: raise UnsupportedIteratedTypeError(
                        'Pinq.average() requires number-like iterated types'
                        ' that support addition and division by int or can be'
                        ' converted to float.'
                    )
                    c += 1
        else:
            if func is None:
                try: s = sum(self._iterable)
                except: TypeError: s = sum(map(float, self._iterable))
                except: ValueError: raise UnsupportedIteratedTypeError(
                    'Pinq.average() requires number-like iterated types that'
                    ' support addition and division by int or can be converted'
                    ' to float.'
                )
            else:
                try: s = sum(map(func, self))
                except: TypeError: s = sum(map(func, map(float, self)))
                except: ValueError: raise UnsupportedIteratedTypeError(
                    'Pinq.average() requires number-like iterated types that'
                    ' support addition and division by int or can be converted'
                    ' to float.'
                )
        try: result = s / c
        except TypeError: result = float(s) / c
        except ValueError: raise UnsupportedIteratedTypeError(
            'Pinq.average() requires number-like iterated types that'
            ' support addition and division by int or can be converted'
            ' to float.'
        )
        return result

    ### Cast is not required for Python! Yay!

    def concat(self, other):
        """
        https://docs.microsoft.com/en-us/dotnet/api/system.linq.enumerable.concat
        https://github.com/dotnet/runtime/blob/master/src/libraries/System.Linq/src/System/Linq/Concat.cs
        https://github.com/dotnet/runtime/blob/master/src/libraries/System.Linq/src/System/Linq/Concat.SpeedOpt.cs

        Since an out-of-place solution is required it's not efficient to
        produce a new iterable (in any way) but rather to chain two iterables.
        itertools.chain serves that purpose perfectly, and is implemented in C.
        """
        if not hasattr(other, '__iter__'):
            raise TypeError('Pinq.concat() must be called with an iterable.')
        return Pinq(itertools.chain(self._iterable, other))

    def contains(self, value, comparer=None):
        """
        https://docs.microsoft.com/en-us/dotnet/api/system.linq.enumerable.contains
        https://github.com/dotnet/runtime/blob/master/src/libraries/System.Linq/src/System/Linq/Contains.cs

        This functionality is already implemented by the `in` membership test
        operation available for iterables. 
        However, in some cases, like dictionaries, the __contains__ method
        behaves differently than just iterating over all elements and checking
        for equality. It is unfortunately one of the cases where the user has
        to be conscious about the underlying iterable.
        This is not the fault of PINQ, rather it's the implementation decision
        of the builtin dict.

        If a comparer is supplied, the optimal solution is to create a partial
        function where one of the arguments of comparer is value, and the other
        is the one that is received by map while iterating. Using map instead
        of a list comprehension is preferable because map returns a generator.

        TODO(rm9wia@inf.elte.hu): Wouldn't a for loop be better than map?
        """
        if comparer is None:
            return value in self._iterable
        else:
            return value in map(
                functools.partial(comparer, value), self._iterable
            )
    
    def count(self, predicate=None):
        """
        https://docs.microsoft.com/en-us/dotnet/api/system.linq.enumerable.count
        https://github.com/dotnet/runtime/blob/master/src/libraries/System.Linq/src/System/Linq/Count.cs

        Many collections have the __len__ method, but not all iterables, so
        count can't rely on that. It is still attempted for the potential
        performance gain.
        """
        if predicate is None:
            if hasattr(self._iterable, '__len__'):
                return len(self._iterable)
            count = 0
            for _ in self._iterable:
                count += 1
            return count
        else:
            count = 0
            for _ in map(predicate, self._iterable):
                count += 1
            return count
    
    def default_if_empty(self, default_value):
        """
        https://docs.microsoft.com/en-us/dotnet/api/system.linq.enumerable.defaultifempty
        https://github.com/dotnet/runtime/blob/master/src/libraries/System.Linq/src/System/Linq/DefaultIfEmpty.cs
        
        The simplest way to return a new Pinq object from the default value
        is to use a list. It is also more likely to be optimized than creating
        a new DefaultIfEmptyIterator class.
        """
        if any(self._iterable):
            return self
        return Pinq([default_value])
    
    def distinct(self):
        """
        https://docs.microsoft.com/en-us/dotnet/api/system.linq.enumerable.distinct
        https://github.com/dotnet/runtime/blob/master/src/libraries/System.Linq/src/System/Linq/Distinct.cs
        
        The original implementation uses sets too.
        This implementation is similar to:
        https://more-itertools.readthedocs.io/en/stable/api.html#more_itertools.unique_everseen
        https://more-itertools.readthedocs.io/en/stable/_modules/more_itertools/recipes.html#unique_everseen

        #TODO(rm9wia@inf.elte.hu): Are _seenset_add and _seenlist_add important?
        Special cases:
            set, dictionary, and the 'key' keyword to transform to tuples (hashable).
        """
        class DistinctIterator(Pinq):
            def __init__(self, iterable):
                self._iterable = iterable
            
            def __iter__(self):
                self._seenset = set()
                self._seenset_add = _seenset.add
                self._seenlist = []
                self._seenlist_add = _seenlist.append
                return self
            
            def __next__(self):
                item = next(self._iterable)
                if item not in self._seenset:
                    self._seenset_add(item)
                    return item
                except TypeError:
                    if item not in self._seenlist:
                        self._seenlist_add(item)
                    return item

        return DistinctIterator(self._iterable)
    
    def element_at(self, index):
        """
        https://docs.microsoft.com/en-us/dotnet/api/system.linq.enumerable.elementat
        https://github.com/dotnet/runtime/blob/master/src/libraries/System.Linq/src/System/Linq/ElementAt.cs
        https://more-itertools.readthedocs.io/en/stable/_modules/more_itertools/recipes.html#nth
        """
        try:
            return self._iterable.__getitem__(index)
        except (AttributeError, TypeError):
            try:
                return next(itertools.islice(self._iterable, index))
            except StopIteration:
                raise OutOfRangeError(
                    'Pinq.element_at() received an index that is larger than'
                    'the size of the iterable.'
                )
        except IndexError:
            raise OutOfRangeError(
                'Pinq.element_at() received an index that is larger than the'
                'size of the iterable.'
            )
    
    def element_at_or_default(self, index, default):
        """
        https://docs.microsoft.com/en-us/dotnet/api/system.linq.enumerable.elementatordefault
        https://github.com/dotnet/runtime/blob/master/src/libraries/System.Linq/src/System/Linq/ElementAt.cs
        https://more-itertools.readthedocs.io/en/stable/_modules/more_itertools/recipes.html#nth
        """
        try:
            return self._iterable.__getitem__(index)
        except (AttributeError, TypeError):
            try:
                return next(itertools.islice(self._iterable, index))
            except StopIteration:
                return default
        except IndexError:
            return default
    
    def empty(self):
        """
        https://docs.microsoft.com/en-us/dotnet/api/system.linq.enumerable.empty
        https://github.com/dotnet/runtime/blob/master/src/libraries/System.Linq/src/System/Linq/Enumerable.SizeOpt.cs
        https://github.com/dotnet/runtime/blob/master/src/libraries/System.Linq/src/System/Linq/Enumerable.SpeedOpt.cs
        
        Since Python doesn't bother with types, empty doesn't have to take a
        type argument. The simplest iterable is a list.
        """
        return Pinq([])
    
    def except(self, first, second, comparer):
        """
        https://docs.microsoft.com/en-us/dotnet/api/system.linq.enumerable.except
        https://github.com/dotnet/runtime/blob/master/src/libraries/System.Linq/src/System/Linq/Except.cs

        Special cases: set, dict
        """
        class ExceptIterator(Pinq):
            def __init__(self, first, second, comparer):
                self._first = first
                self._second = second
                self._comparer = comparer
            
            def __iter__(self):
                self._seenset = set()
                self._seenset_add = _seenset.add
                self._seenlist = []
                self._seenlist_add = _seenlist.append
                for item in self._second:
                    try:
                        self._seenset_add(item)
                    except TypeError:
                        if item not in self._seenlist:
                            self._seenlist_add(item)
                return self
            
            def __next__(self):
                item = next(self._iterable)
                if item not in self._seenset:
                    self._seenset_add(item)
                    return item
                except TypeError:
                    if item not in self._seenlist:
                        self._seenlist_add(item)
                    return item
        
        return ExceptIterator(self._iterable)

    def first(self, predicate):
        """
        https://docs.microsoft.com/en-us/dotnet/api/system.linq.enumerable.first
        https://github.com/dotnet/runtime/blob/master/src/libraries/System.Linq/src/System/Linq/First.cs
        https://more-itertools.readthedocs.io/en/stable/_modules/more_itertools/more.html#first
        """
        if predicate is None:
            try:
                return next(iter(self._iterable))
            except StopIteration:
                raise NoElementsError('Called Pinq.first() on empty iterable.')
        else:
            try:
                return next(filter(predicate, self._iterable))
            except StopIteration:
                raise NoMatchError('Pinq.first() found no matching elements.')
    
    def first_or_default(self, predicate, default):
        """
        https://docs.microsoft.com/en-us/dotnet/api/system.linq.enumerable.firstordefault
        https://github.com/dotnet/runtime/blob/master/src/libraries/System.Linq/src/System/Linq/First.cs
        https://more-itertools.readthedocs.io/en/stable/_modules/more_itertools/more.html#first
        """
        if predicate is None:
            try:
                return next(iter(self._iterable))
            except StopIteration:
                return default
        else:
            try:
                return next(filter(predicate, self._iterable))
            except StopIteration:
                return default
    
    def group_by(self, key_selector, element_selector, result_selector, comparer):
        """
        https://docs.microsoft.com/en-us/dotnet/api/system.linq.enumerable.groupby
        https://github.com/dotnet/runtime/blob/master/src/libraries/System.Linq/src/System/Linq/Grouping.cs
        https://github.com/dotnet/runtime/blob/master/src/libraries/System.Linq/src/System/Linq/Lookup.cs
        https://codereview.stackexchange.com/questions/732/implementation-of-groupbytkey-telement-in-net

        Simple solution: itertools.groupby(sorted(map(element_selector, self._iterable)), key_selector)
        Or something similar, with result_selector and comparer as well.
        """
        class GroupByIterator(Pinq):
            def __init__(self, iterable, key_selector, element_selector, result_selector, comparer):
                pass
            
            def __iter__(self):
                pass
            
            def __next__(self):
                pass
        
        class Grouping:
            def __init__(self, key):
        
        return GroupByIterator(
            self._iterable, key_selector, element_selector,
            result_selector, comparer
        )


########
# LINQ #
########


Linq = Pinq  # In case you prefer.