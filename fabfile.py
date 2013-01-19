"""Fabric tasks for RandoPony-tetra web app.
"""
from fabric.api import (
    env,
    task,
    )
from fabric.contrib.project import rsync_project


env.user = 'bcrandonneur'
env.hosts = ['bcrandonneur.webfactional.com']
app_name = 'randopony'
app_release = '2013'
app_dir = '/home/{0}/webapps/{1}{2}'.format(env.user, app_name, app_release)


@task(default=True)
def deploy():
    """Deploy code to webfaction and restart app
    """
    rsync_code()
    restart_app()


@task
def rsync_code():
    """rsync project code to webfaction
    """
    exclusions = (
        'development.ini',
        'docs',
        'fabfile.py',
        'htmlcov',
        'MANIFEST.in',
        'RandoPony.egg-info',
        'requirements',
        '*.sublime-*',
        '.coveragerc',
        '*.db',
        '.DS_Store',
        '.hg*',
        '*.pyc',
        '*~',
        )
    rsync_project(remote_dir=app_dir, exclude=exclusions, delete=True)


@task
def restart_app():
    """Restart app on webfaction
    """
    pass