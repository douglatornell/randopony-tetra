"""Fabric tasks for RandoPony-tetra web app.
"""
import os
from fabric.api import (
    cd,
    env,
    run,
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
    install_app()
    restart_app()


@task
def init():
    """Prepare initial deployment to webfaction
    """
    rsync_code()
    install_app()


@task
def rsync_code():
    """rsync project code to webfaction
    """
    exclusions = (
        'build',
        'development.ini',
        'docs',
        'fabfile.py',
        'htmlcov',
        'MANIFEST.in',
        'RandoPony.egg-info',
        'requirements',
        'temp',
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
def install_app():
    """Install app on webfaction
    """
    code_dir = os.path.basename(os.getcwd())
    with cd(app_dir):
        run('bin/easy_install -U {}'.format(code_dir))


@task
def restart_app():
    """Restart app on webfaction
    """
    pass