# Python INtegrated Query

PINQ (Python INtegrated Query) is a library that strives to implement similar
functionality to that of LINQ in the .NET environment.

LINQ can be - originally - used in two main scenarios:
* On containers that implement the IEnumerable interface.
* On query providers implementing IQueryable (such as DbSet in Entity Framework)

This repository currently implements the first scenario.

Usage
=====

To use this library, simply include the `pinq.py` file into your project.
To be able to perform the queries, first convert the iterable to a Pinq object.
After this, you can use the same methods that are available in the .NET LINQ
(except for some that only make sense in a strong typed language).
The performance of this library is comparable to that of the .NET implementation,
as it not only directly resembles the API but also the implementation details.

NOTE: Creating a Pinq object doesn't copy the iterable's contents,
it only keeps a reference to the original iterable. Any changes to the original
iterable will also affect Pinq. (Copying iterable contents wouldn't be possible
in the case of infinite generators, and wouldn't be preferable in the case of
files and network-backed iterables).

NOTE: Some operations may enumerate the whole iterable, and therefore may be
non-repeatable, if the iterable itself is not re-iterable. (Such as generators
or files)

Implementation details
======================

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

* self._iterable should be iterated instead of self, as it avoids a tiny bit of overhead. 
* pinq-methods shouldn't rely on each other, it is more efficient and makes it easier to modify individual methods later

Algorithm details:
------------------

Prefer to use algorithms similar to that of the original C# implementation.
Except when there are any builtins (e.g. sum, all, etc.) or highly-optimized solutions (e.g. map)
that are very much optimized in Python (f.e. written in native C).
In that case, use them even if it seems to be overhead.
List comprehensions are FINE. They are not written in C, but there's
plenty of time to decide to use map/filter/etc. when needed LATER.
Actually, they are not. List comprehensions are evaluated beforehand,
generators such as the one returned by map are not.

Todos
=====

* Support IQueryable usage and query providers.
* Support extension methods:
    * https://docs.microsoft.com/en-us/dotnet/csharp/programming-guide/classes-and-structs/extension-methods
    * https://stackoverflow.com/questions/514068/extension-methods-in-python
    * These can't be used for builtins, but can be used to enable other users to 
    add specific functionality (optimisations) for their specific types for LINQ.
    * Use special methods for builtins. (Check iterable's type in `__init__`)
* Handle infinite iterables (many method)s will hit an infinite loop!)
* Support iterables of unhashables to be converted to iterables of hashables for performance gain.
* Consider using a _marker=object() to detect when a default is not provided

References
==========

Similar projects
----------------

* https://github.com/viralogic/py-enumerable

LINQ
----

* https://github.com/dotnet/runtime/tree/master/src/libraries/System.Linq/src/System/Linq
* https://en.wikipedia.org/wiki/Language_Integrated_Query
* https://docs.microsoft.com/en-us/dotnet/csharp/programming-guide/concepts/linq/
* https://github.com/Microsoft/referencesource/blob/master/System.Core/System/Linq/Enumerable.cs
* https://codeblog.jonskeet.uk/2011/02/23/reimplementing-linq-to-objects-part-45-conclusion-and-list-of-posts/

### List of all operations:
* https://docs.microsoft.com/en-us/dotnet/api/system.linq.enumerable?view=netcore-3.1#methods
* https://referencesource.microsoft.com/

### LINQ to Python

* https://stackoverflow.com/questions/3925093/pythons-list-comprehension-vs-net-linq
* https://www.markheath.net/post/python-equivalents-of-linq-methods

Other implementations
---------------------

* https://github.com/viralogic/py-enumerable
* https://pypi.org/project/Linq/
* In Javascript: https://github.com/mihaifm/linq

Python reading (for implementation details)
-------------------------------------------

* https://docs.python.org/3/library/collections.abc.html#module-collections.abc
* https://docs.python.org/3/glossary.html#term-asynchronous-iterable
* https://docs.python.org/3/glossary.html#term-iterable
* https://docs.python.org/3.8/reference/datamodel.html#emulating-container-types
* https://docs.python.org/3/tutorial/classes.html#iterators
* https://docs.python.org/dev/library/stdtypes.html#iterator-types
* https://rszalski.github.io/magicmethods/#sequence

* https://docs.python.org/3/library/functions.html
* https://github.com/python/cpython/blob/master/Python/bltinmodule.c
* https://docs.python.org/3.8/library/functools.html
* https://github.com/python/cpython/blob/master/Lib/functools.py
* https://github.com/python/cpython/blob/master/Modules/_functoolsmodule.c
* https://docs.python.org/3.8/library/itertools.html
* https://github.com/python/cpython/blob/master/Modules/itertoolsmodule.c
* https://pypi.org/project/more-itertools/