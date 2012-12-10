.. _Development-section:

Development
===========

RandoPony-tetra is developed and tested with Python 3.3.


.. _DevelopmentEnvironment-section:

Development Environment
-----------------------

Development in a virtualenv is *strongly* recommended to isolate
:obj:`randopony-tetra` and the packages it depends on from other installed Python packages.
Using the virtualenv tool built into Python 3.3,
create a virtualenv,
activate it,
and install the :obj:`distribute` library in it:

.. code-block:: sh

   tom:$ cd ~/.virtualenvs
   tom:.virtualenvs$ pyvenv-3.3 randopony-test
   tom:.virtualenvs$ source randopony-test/bin/activate
   (randopony-test) tom:.virtualenvs$ cd /tmp/
   (randopony-test) tom:tmp$ curl -O http://python-distribute.org/distribute_setup.py
   (randopony-test) tom:tmp$ python distribute_setup.py

Clone the code repository from Bitbucket:

.. code-block:: sh

   (randopony-test) tom:$ cd python
   (randopony-test) tom:python$ hg clone https://bitbucket.org/douglatornell/randopony-tetra


.. TestingAndCoverage-section:

Testing and Coverage
--------------------

The test suite uses only the tools provided by the Python 3.3 :mod:`unittest`
module.
The simplest way to run the complete test suite is with
:program:`unittest discover`:

.. code-block:: sh

   (randopony-tetra) tom:randopony-tetra$ python -m unittest discover
   ..........................................................
   ----------------------------------------------------------------------
   Ran 58 tests in 1.513s

   OK

A more sophisticated test runner like :program:`nose` or :program:`py.test`
can be used to run parts of the test suite, etc.

To generate a test coverage report,
run the test suite via :program:`coverage`,
and then run :program:`coverage report`:

.. code-block:: sh

   (randopony-tetra) tom:randopony-tetra$ coverage run -m unittest discover
   ..........................................................
   ----------------------------------------------------------------------
   Ran 58 tests in 1.577s

   OK

   (randopony-tetra) tom:randopony-tetra$ coverage report
   Name                                   Stmts   Miss Branch BrMiss  Cover  Missing
   ----------------------------------------------------------------------------------
   randopony/__init__                        19      0      0      0   100%
   randopony/__version__                      1      1      0      0     0%   2
   randopony/models/__init__                  5      0      0      0   100%
   randopony/models/admin                    19      0      0      0   100%
   randopony/models/brevet                   48      0      6      0   100%
   randopony/models/core                     37      0      0      0   100%
   randopony/models/meta                      6      0      0      0   100%
   randopony/models/populaire                41      0      0      0   100%
   randopony/scripts/__init__                 0      0      0      0   100%
   randopony/scripts/initializedb            24     24      2      2     0%   2-39
   randopony/tests/__init__                   0      0      0      0   100%
   randopony/tests/test_admin               103      0      2      0   100%
   randopony/tests/test_auth                 35      0      0      0   100%
   randopony/tests/test_brevet_admin        130      0      0      0   100%
   randopony/tests/test_models              117      0      0      0   100%
   randopony/tests/test_populaire_admin     132      0      0      0   100%
   randopony/tests/test_site                105      0      0      0   100%
   randopony/tests/test_wrangler_admin      106      0      0      0   100%
   randopony/views/__init__                   0      0      0      0   100%
   randopony/views/admin/__init__             0      0      0      0   100%
   randopony/views/admin/brevet              71      0      6      0   100%
   randopony/views/admin/core                42      2     10      1    94%   25-26
   randopony/views/admin/populaire           68      0      6      0   100%
   randopony/views/admin/wrangler            50      0      4      0   100%
   randopony/views/site                      35      0      2      0   100%
   ----------------------------------------------------------------------------------
   TOTAL                                   1194     27     38      3    98%

:file:`randopony-tetra/.coveragerc` contains settings which enable branch
coverage,
limit coverage analysis to the :mod:`randopony` package and its sub-packages,
and include the line number of code without test coverage in the report.


.. Documentation-section:

Documentation
-------------

The documentation is written using reStructuredText markup,
and built with Sphinx.

.. note::

   As of early December 2012 parts of the Sphinx tool chain does not work
   under Python 3.3.
   Setting up a Python 2.7 or 3.2 virtualenv with Sphinx installed in it is
   thus required to build the documentation.

Build the docs with:

.. code-block:: sh

   (sphinx-3.2)tom:randopony-tetra$ (cd docs && make html)

The results are browsable in :file:`randopony-tetra/docs/_build/html/`.