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

The deployment strategy described here is:

* Deployment of nearly release-ready code from a local development environment
  to a staging environment Webfaction app that is mounted in a website hosted
  at a test domain;
  e.g. :kbd:`randopony.bcrandonneur.webfactional.com`.

* Testing of the staging deployment to the extent necessary to confirm that it
  is ready for production release.

* Promotion of the staging environment to production by giving it access to the
  production database,
  and mounting it in a website hosted at the production domain;
  e.g. :kbd:`randopony.randonneurs.bc.ca`.

Most of the deployment and management activities described in this section
have been implemented as Fabric_ tasks,
so,
Fabric_ needs to be installed in the local virtualenv from which ou are working,
and you ned to have ssh key authentication working on Webfaction.

.. _Fabric: http://docs.fabfile.org/


.. _WebfactionEnvironment-section:

Webfaction Environment
----------------------

Use the Webfaction control panel to:

#. Create staging and production sub-domains:
   :kbd:`randopony.bcrandonneur.webfactional.com`
   and :kbd:`randopony.randonneurs.bc.ca`

#. Create a staging application,
   initially just a Pyramid 1.4/Python 2.7 application named to reflect the
   release that is being prepared;
   e.g. :kbd:`randopony2013r1`.
   Make note of the port number that is assigned to the application.

#. Create a website with the same name as the application and host it at
   :kbd:`randopony.bcrandonneur.webfactional.com` with the application mounted
   at :kbd:`/`


Initial Staging Deployment
--------------------------

If the app is being deployed to the staging environment for the first time in a
newly created Webfaction application directory:

#. Edit :file:`staging.ini` and :file:`production.ini` to set the port number
   in the :kbd:`server:main` section to the port that Webfaction provided for
   the application;
   e.g.

   .. code-block:: ini

      [server:main]
      use = egg:waitress#main
      host = 127.0.0.1
      port = 19306

#. Edit :file:`fabfile.py` to set the module level values appropriately.
   In particular,
   the sum of :data:`app_name` and :data:`staging_release` should equal the
   name of the Webfaction application you created in the
   :ref:`WebfactionEnvironment-section`;
   e.g.

   .. code-block:: python

      env.user = 'bcrandonneur'
      env.hosts = ['bcrandonneur.webfactional.com']
      app_name = 'randopony'
      staging_release = '2013r1'
      staging_dir = (
          '/home/{0}/webapps/{1}{2}'.format(env.user, app_name, staging_release))

#. Prepare the staging environment with:

   .. code-block:: python

      (randopony-tetra)randopony-tetra$ fab init_staging

   That launchs a squence of Fabric tasks to:

   * Upload the code via :program:`rsync`
     (:kbd:`rsuync_code` task)

   * Install the RandoPony app and its dependencies in the Webfaction
     ::kbd:`staging_dir` and its associated :program:`virtualenv` directories
     (:kbd:`install_app` task)

   * Create the :file:`RandoPony-staging.sqlite` database,
     and initialize it with link and email address records that the app
     requires
     (:kbd:`init_staging_db` task)

#. :program:`ssh` into Webfaction and do the following:

   * Create,
     adjust permissions of,
     and populate the :file:`randopony-tetra/randppony/private_credentials.py`
     file:

     .. code-block:: sh

        [bcrandonneur@web246 randopony]$ cd $HOME/webapps/randopony2013r1
        [bcrandonneur@web246 randopony]$ cd randopony-tetra/randopony
        [bcrandonneur@web246 randopony]$ touch private_credentials.py
        [bcrandonneur@web246 randopony]$ chmod 600 private_credentials.py

     The contents of :file:`private_credentials.py` should be:

     .. code-block:: python

        """RandoPony app credentials.
        """

        persona_secret = ''

        google_drive_username = ''
        google_drive_password = ''

        email_host_username = ''
        email_host_password = ''

     :kbd:`uuid.uuid4()` is a convenient way to generate a random string
     for :kbd:`persona_secret`.
     The Google drive credentials are those of the account where the rider
     list spreadsheet templates are stored and the event rider lists
     will be maintained.
     The email host credentials are those of the Webfaction account that
     will be used to send email from the RandoPony app.
