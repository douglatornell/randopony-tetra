.. DeploymentAndManagement-section:

Deployment and Management
=========================

This section describes deployment and management of RandoPony-tetra on the
:kbd:`randonneurs.bc.ca` domain hosted on Webfaction.

.. note::

   As of mid-January 2013 Webfaction does not provide a Pyramid/Python3
   environment that is installable from the control panel.
   While it should be possible to build such an environment,
   this document describes deployment in a Python 2.7, Pyramid 1.4 environment
   created from the control panel.

Most of the deployment and management activities described in this section
have been implemented as Fabric_ tasks,
so,
Fabric_ needs to be installed in the local virtualenv from which ou are working,
and you ned to have ssh key authentication working on Webfaction.

.. _Fabric: http://docs.fabfile.org/


.. _Environment-section:

Environment
-----------

Use the Webfaction control panel to:

#. Create staging and deployment sub-domains:
   :kbd:`randopony.bcrandonneur.webfactional.com`
   and :kbd:`randopony.randonneurs.bc.ca`

#. Create applications to mount on those domains,
   initially just a Pyramid 1.4/Python 2.7 application called
   :kbd:`randopony2013`.
   Make note of the port numbers that are assigned to the applications.

#. Create a website called :kbd:`randopony2013` hosted at
   :kbd:`randopony.bcrandonneur.webfactional.com` with the :kbd:`randopony2013`
   application mounted at :kbd:`/`


Initial Deployment
------------------

If the app is being installed for the first time in a newly created Webfaction
application directory:

#. Edit :file:`production.ini` to set the port number in the :kbd:`server:main`
   section to the port that Webfaction provided for the application;
   e.g.

   .. code-block:: ini

      [server:main]
      use = egg:waitress#main
      host = 127.0.0.1
      port = 19306

#. Edit :file:`fabfile.py` to set the module level values appropriately.
   In particular,
   the sum of :data:`app_name` and :data:`app_release` should equal the name
   of the Webfaction application you created in the :ref:`Environment-section`.

   .. code-block:: python

      env.user = 'bcrandonneur'
      env.hosts = ['bcrandonneur.webfactional.com']
      app_name = 'randopony'
      app_release = '2013'
      app_dir = '/home/{0}/webapps/{1}{2}'.format(env.user, app_name, app_release)

#. Upload the code and install the dependencies with:

   .. code-block:: python

      (randopony-tetra)randopony-tetra$ fab init
