"""LINQ syntax and functionality implemented in Python."""


import functools
import itertools


##############
# EXCEPTIONS #
##############


class NoElementsError(Exception):
    pass


class UnsupportedIteratedType(Exception):
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
        sperformed in the same loop.

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
                    except ValueError: raise UnsupportedIteratedType(
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
                    except ValueError: raise UnsupportedIteratedType(
                        'Pinq.average() requires number-like iterated types'
                        ' that support addition and division by int or can be'
                        ' converted to float.'
                    )
                    c += 1
        else:
            if func is None:
                try: s = sum(self._iterable)
                except: TypeError: s = sum(map(float, self._iterable))
                except: ValueError: raise UnsupportedIteratedType(
                    'Pinq.average() requires number-like iterated types that'
                    ' support addition and division by int or can be converted'
                    ' to float.'
                )
            else:
                try: s = sum(map(func, self))
                except: TypeError: s = sum(map(func, map(float, self)))
                except: ValueError: raise UnsupportedIteratedType(
                    'Pinq.average() requires number-like iterated types that'
                    ' support addition and division by int or can be converted'
                    ' to float.'
                )
        try: result = s / c
        except TypeError: result = float(s) / c
        except ValueError: raise UnsupportedIteratedType(
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


########
# LINQ #
########


Linq = Pinq  # In case you prefer.