rangetree: easy range lookups
=============================

.. image:: https://img.shields.io/pypi/v/rangetree.svg
    :target: https://pypi.python.org/pypi/rangetree
.. image:: https://travis-ci.org/nanobit/rangetree.svg?branch=master
    :target: https://travis-ci.org/nanobit/rangetree
.. image:: https://coveralls.io/repos/nanobit/rangetree/badge.svg
    :target: https://coveralls.io/r/nanobit/rangetree

``rangetree`` is an Apache2 licensed library, written in Python 3, for easy and fast
lookups of numeric ranges.

Given three integer ranges, 0 - 9, 10 - 99, and 100 - 999, ``rangetree`` makes
it trivial to look up exactly which range any integer falls in. (Note Python
slices and ranges include the first index, and exclude the second.)

.. code-block:: python

    >>> from rangetree import RangeTree
    >>>
    >>> r = RangeTree()
    >>> r[0:10] = 'single digits'
    >>> r[10:100] = 'double digits'
    >>> r[100:1000] = 'triple digits'
    >>>
    >>> r[4]
    'single digits'


``RangeTree``s are optimized for lookups, and make use of the excellent
bintrees library.

.. _bintrees: https://bitbucket.org/mozman/bintrees

Features
--------

- supports open and closed ranges
- supports integer keys
- optimized for lookups (not insertions)

Installation
------------

To install ``rangetree``, simply:

.. code-block:: bash

    $ pip install rangetree

Usage
-----

Insertion is done using Python's slice notation, or using range objects.

.. code-block:: python

    >>> r = RangeTree()
    >>> r[0:10] = 'single digits'
    >>> r[range(10, 100)] = 'double digits'

Negative integers are supported.

.. code-block:: python

    >>> r[-10:0] = 'negative singles'

Missing a range will result in a ``KeyError``. Use ``Rangtree.get()``.

.. code-block:: python

    >>> 1000 in r
    False
    >>> r[1000]
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "rangetree.py", line 93, in __getitem__
        raise KeyError(key)
    KeyError: 1000
    >>> r.get(1000, 'no value')
    'no value'

Open ranges (that go to infinity) are supported. Setting open ranges is only
possible using the slice notation.

.. code-block:: python

    >>> r[1000:] = 'quadruple digits or more'
    >>> r[999999999]

Overlapping ranges will result in a ``KeyError``.

    >>> r = RangeTree()
    >>> r[1000:] = 'quadruple digits or more'
    >>> r[10000:] = 'ten thousand'
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "rangetree.py", line 58, in __setitem__
        raise KeyError('Overlapping intervals.')
    KeyError: 'Overlapping intervals.'

Changelog
---------

1.0 (2016-10-20)
~~~~~~~~~~~~~~~~~~
Initial public release.


Contributing
------------
Contributions are very welcome. Tests can be run with ``tox``, please ensure
the coverage at least stays the same before you submit a pull request.

Credits
-------

The development of ``rangetree`` is sponsored by Nanobit_.

``rangetree`` is tested with Hypothesis_, by David R. MacIver.

``rangetree`` is benchmarked using perf_, by Victor Stinner.

.. _Nanobit: http://nanobit.co
.. _Hypothesis: http://hypothesis.readthedocs.io/en/latest/
.. _perf: https://github.com/haypo/perf
