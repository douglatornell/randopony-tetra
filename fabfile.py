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
staging_release = '2013r1'
staging_dir = (
    '/home/{0}/webapps/{1}{2}'.format(env.user, app_name, staging_release))


@task(default=True)
def deploy():
    """Deploy code to Webfaction staging app and restart it
    """
    rsync_code()
    install_app()
    restart_app()


@task
def init_staging():
    """Initial staging deployment to Webfaction
    """
    rsync_code()
    install_app()
    init_staging_db()


@task
def rsync_code():
    """rsync project code to Webfaction staging app
    """
    exclusions = (
        'build',
        'development.ini',
        'docs',
        'fabfile.py',
        'htmlcov',
        'MANIFEST.in',
        'randopony/private_credentials.py',
        'RandoPony.egg-info',
        'requirements',
        'temp',
        '**/__pycache__',
        '*.sublime-*',
        '.coveragerc',
        '*.log',
        '*.pid',
        '*.sqlite',
        '.DS_Store',
        '.hg*',
        '*.pyc',
        '*~',
        )
    rsync_project(remote_dir=staging_dir, exclude=exclusions, delete=True)


@task
def install_app():
    """Install staging app on Webfaction
    """
    code_dir = os.path.basename(os.getcwd())
    with cd(staging_dir):
        run('bin/easy_install -U {}'.format(code_dir))


@task
def init_staging_db():
    """Initialize staging database on Webfaction
    """
    with cd(os.path.join(staging_dir, 'randopony-tetra')):
        run('../bin/initialize_RandoPony_db staging.ini')


@task
def restart_app():
    """Restart app on webfaction
    """
    pass