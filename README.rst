
.. _Liquid: https://github.com/jg-rp/liquid
.. _Pipenv: https://pipenv.pypa.io/en/latest/

Flask-Liquid
============

A `Flask <https://palletsprojects.com/p/flask/>`_ extension for `Liquid`_. Render Liquid
templates in your Flask applications.

.. image:: https://img.shields.io/pypi/v/flask-liquid.svg?style=flat-square
    :target: https://pypi.org/project/flask-liquid/
    :alt: Version

.. image:: https://img.shields.io/github/workflow/status/jg-rp/flask-liquid/Tests/main?label=tests&style=flat-square
    :target: https://github.com/jg-rp/flask-liquid/tree/main/tests
    :alt: Tests

.. image:: https://img.shields.io/pypi/l/flask-liquid.svg?style=flat-square
    :target: https://pypi.org/project/flask-liquid/
    :alt: Licence

.. image:: https://img.shields.io/pypi/pyversions/flask-liquid.svg?style=flat-square
    :target: https://pypi.org/project/flask-liquid/
    :alt: Python versions

.. image:: https://img.shields.io/badge/pypy-3.7%20%7C%203.8-blue?style=flat-square
    :target: https://pypi.org/project/flask-liquid/
    :alt: PyPy versions

Installing
----------

Install Flask Liquid using `Pipenv`_:

.. code-block:: text

    $ pipenv install flask-liquid

Or `pip <https://pip.pypa.io/en/stable/getting-started/>`_:

.. code-block:: text

    $ python -m pip install -U flask-liquid

Links
-----

- Documentation: https://jg-rp.github.io/liquid/guides/flask-liquid
- Change Log: https://github.com/jg-rp/Flask-Liquid/blob/main/CHANGES.rst
- PyPi: https://pypi.org/project/Flask-Liquid/
- Source Code: https://github.com/jg-rp/Flask-Liquid
- Issue Tracker: https://github.com/jg-rp/flask-Liquid/issues

Contributing
------------

- Install development dependencies with `Pipenv`_

- Flask Liquid uses type hints and static type checking. Run ``mypy`` or  
  ``tox -e typing`` to check for typing issues.

- Format code using `black <https://github.com/psf/black>`_.

- Write tests using ``unittest.TestCase``.

- Run tests with ``make test`` or ``python -m unittest`` or ``pytest``.

- Check test coverage with ``make coverage`` and open ``htmlcov/index.html`` in your
  browser.
