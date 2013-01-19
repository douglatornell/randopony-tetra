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


Environment
-----------

Use the Webfaction control panel to:

#. Create staging and deployment sub-domains:
   :kbd:`randopony.bcrandonneur.webfactional.com`
   and :kbd:`randopony.randonneurs.bc.ca`

#. Create applications to mount on those domains,
   initially just a Pyramid 1.4/Python 2.7 application called
   :kbd:`randopony2013`

#. Create a website called :kbd:`randopony2013` hosted at
   :kbd:`randopony.bcrandonneur.webfactional.com` with the :kbd:`randopony2013`
   application mounted at :kbd:`/`