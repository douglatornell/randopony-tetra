.. _DataModelManagement-section:

Data Model Management
=====================

The data model objects and underlying persistence in the database of model
instances can be managed from the command line via the Pyramid
:command:`pshell` command.
This is useful for tasks like:

* creating database tables for new model objects during development

* manipulation of model instances for which there is no admin
  interface;
  e.g. :class:`models.EmailAddress` and :class:`models.Link`

* bulk deletion of model instances

The code examples below assume that the configuration file that
:command:`pshell` is started with includes a section like:

.. code-block:: ini

   [pshell]
   m = randopony.models
   session = randopony.models.DBSession
   t = transaction


Database Table Creation
-----------------------

To create tables for new data model objects that don't already exist in the
database use:

.. code-block:: python

   >>> m.meta.Base.metadata.create_all()


Manipulation of Database Model Instances
----------------------------------------

Example: Create a database row for the club webmaster's email address.

.. code-block:: python

   >>> email = m.EmailAddress(key='webmaster', email='tom@example.com')
   >>> with t.manager:
   >>>     session.add(email)
