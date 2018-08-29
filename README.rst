noqlite
==========

simple nosql over sqlite

install
=======

::

    pip install noqlite


usage
=====

.. code:: python

    from noqlite import NoQLite, Query

    db = NoQLite('bicycles-per-capita.db')
    db.insert({'rate': 0.6, 'country': 'Japan'})
    db.insert({'rate': 0.8, 'country': 'Denmark'})
    db.insert({'rate': 1.3, 'country': 'Netherlands'})
    db.search(Query().rate > 1)
    # [{'id': 3, 'country': 'Netherlands', 'rate': 1.3}]
