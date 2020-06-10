This is a very slightly modified version of the py-enumerable project.

All the credit goes to the original creators/contributors to that project.

I occasionally check out the original project for updates, but still, I highly
recommend you visit the GitHub repository https://github.com/viralogic/py-enumerable.

Support extension methods:
https://docs.microsoft.com/en-us/dotnet/csharp/programming-guide/classes-and-structs/extension-methods
https://stackoverflow.com/questions/514068/extension-methods-in-python
* These can't be used for builtins, but can be used to enable other users to
  add specific functionality (optimisations) for their specific types for LINQ.

PROBLEM! What if an iterable is not actually finite? What if an infinite generator.

Names
=====

* PyLinq, PyLINQ
* PINQ (Python Integrated Query)

References
==========

LINQ
----

https://github.com/dotnet/runtime/tree/master/src/libraries/System.Linq/src/System/Linq

* https://en.wikipedia.org/wiki/Language_Integrated_Query
* https://docs.microsoft.com/en-us/dotnet/csharp/programming-guide/concepts/linq/
* https://github.com/Microsoft/referencesource/blob/master/System.Core/System/Linq/Enumerable.cs

List of all operations:
* https://docs.microsoft.com/en-us/dotnet/api/system.linq.enumerable?view=netcore-3.1#methods
* https://referencesource.microsoft.com/

LINQ to Python
--------------

* https://stackoverflow.com/questions/3925093/pythons-list-comprehension-vs-net-linq
* https://www.markheath.net/post/python-equivalents-of-linq-methods


Other implementations
---------------------

* https://github.com/viralogic/py-enumerable
* https://pypi.org/project/Linq/
* In Javascript: https://github.com/mihaifm/linq

Implementation details
======================

* Emulating container types: https://docs.python.org/3.8/reference/datamodel.html#emulating-container-types
* Iterators: https://docs.python.org/3/tutorial/classes.html#iterators
* Iterators: https://docs.python.org/dev/library/stdtypes.html#iterator-types
* https://rszalski.github.io/magicmethods/#sequence

* Linq is an iterable, not at iterator. It shouldn't have a `__next__` method.
* Linq is also not a general container. We can't (and shouldn't) always guarantee random access.
* Linq should have a similar API to that of IEnumerable.

* Even if a type were to have some default implementations (such as list's append or string's concat)
  it's better to avoid using them, because most of the time these LINQ methods do not happen in-place,
  so a very resource-consuming deepcopy could be required.
* An exception would be to create specific "extension methods" for specific types...

* Linq is merely storing a reference to the original iterable, so modifying that may also have side-effects
  (wanted or unwanted) on Linq. It may be worth to copy that (like RepeatableIterable?). Having said that,
  it's normal to have different references to the same data in memory, so it shouldn't be a problem.

Algorithm details:
    Prefer to use algorithms similar to that of the original C# implementation.
    EXCEPT:
        When there are any builtins (e.g. sum, all, etc.) or highly-optimized solutions (e.g. map)
        that are very much optimized in Python (f.e. written in native C).
        In that case, use them even if it seems to be overhead.
        https://docs.python.org/3/library/functions.html
        https://github.com/python/cpython/blob/master/Python/bltinmodule.c

        https://docs.python.org/3.8/library/functools.html
        https://github.com/python/cpython/blob/master/Lib/functools.py
        https://github.com/python/cpython/blob/master/Modules/_functoolsmodule.c

        https://docs.python.org/3.8/library/itertools.html
        https://github.com/python/cpython/blob/master/Modules/itertoolsmodule.c

        List comprehensions are FINE. They are not written in C, but there's
        plenty of time to decide to use map/filter/etc. when needed LATER.
        Actually, they are not. List comprehensions are evaluated beforehand,
        generators such as the one returned by map are not.

Further reading:
    * https://docs.python.org/3/library/collections.abc.html#module-collections.abc
    * https://docs.python.org/3/glossary.html#term-asynchronous-iterable
    * https://docs.python.org/3/glossary.html#term-iterable

TODO: Do IQueryable implementation as well! (With SQLite support?)