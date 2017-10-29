.. _Development-section:

Development
===========

.. _PythonVersions-section:

Python Versions
---------------

RandoPony-tetra is developed and tested with Python 3.6.


.. _DevelopmentEnvironment-section:

Development Environment
-----------------------

Development in a `conda`_ environment is *strongly* recommended to isolate
:obj:`randopony-tetra` and the packages it depends on from other installed
Python packages.

.. _conda: http://conda.pydata.org/docs/

Clone the `code repository`_ from Bitbucket:

.. code-block:: sh

   $ hg clone https://bitbucket.org/douglatornell/randopony-tetra

.. _code repository: https://bitbucket.org/douglatornell/randopony-tetra/

Use :program:`conda` to create a development environment and activate it:

.. code-block:: sh

   $ cd randopony-tetra
   $ conda env create -f environment.yaml
   ...
   $ source activate randopony

To deactivate the development environment,
use:

.. code-block:: sh

   (randopony)$ source deactivate

Install RandoPony as a development package:

.. code-block:: sh

   (randopony-tetra)$ pip install --editable .

Run the development server:

.. code-block:: sh

   (randopony-tetra)$ pserve --reload development.ini


.. _TestingAndCoverage-section:

Testing and Coverage
--------------------

The test suite for the :kbd:`randopony-tetra` package is in :file:`randopony-tetra/tests/`.
The `pytest`_ tool is used for test fixtures and as the test runner for the suite.

.. _pytest: https://docs.pytest.org/en/latest/

With your :kbd:`randopony` development environment activated,
use:

.. code-block:: bash

    (randopony-tetra)$ cd randopony-tetra/
    (randopony-tetra)$ py.test

to run the test suite.

You can monitor what lines of code the test suite exercises using the `coverage.py`_ tool with the command:

.. _coverage.py: https://coverage.readthedocs.org/en/latest/

.. code-block:: bash

    (randopony-tetra)$ cd SalishSeaCmd/
    (randopony-tetra)$ coverage run -m py.test

and generate a test coverage report with:

.. code-block:: bash

    (randopony-tetra)$ coverage report

to produce a plain text report,
or

.. code-block:: bash

    (randopony-tetra)$ coverage html

to produce an HTML report that you can view in your browser by opening :file:`randopony-tetra/htmlcov/index.html`.

:file:`randopony-tetra/.coveragerc` contains settings which enable branch
coverage,
limit coverage analysis to the :mod:`randopony` package and its sub-packages,
and include the line number of code without test coverage in the report.


.. _Documentation-section:

Documentation
-------------

The documentation is written using reStructuredText markup,
and built with Sphinx.

Build the docs with:

.. code-block:: sh

   (randopony-tetra)$ (cd docs && make html)

The results are browsable in :file:`randopony-tetra/docs/_build/html/`.

Online,
the docs are hosted at https://randopony.readthedocs.org/ where they
are automatically updated whenever changes are pushed to the `Bitbucket
repository`_.

.. _Bitbucket repository: https://bitbucket.org/douglatornell/randopony-tetra/


.. _SourceCode-section:

Source Code
-----------

The source repository is hosted on Bitbucket:

* https://bitbucket.org/douglatornell/randopony-tetra/


.. _ReportingBugs-section:

Reporting Bugs
--------------

Please report bugs via the Bitbucket issue tracker:

* https://bitbucket.org/douglatornell/randopony-tetra/issues/
