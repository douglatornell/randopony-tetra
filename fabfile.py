"""Fabric tasks for RandoPony-tetra web app.
"""
from time import sleep
from fabric.api import (
    cd,
    env,
    run,
    task,
    )
from fabric.contrib.files import (
    exists,
    sed,
    )
from fabric.contrib.project import rsync_project


env.user = 'bcrandonneur'
env.hosts = ['bcrandonneur.webfactional.com']
project_name = 'randopony-tetra'
app_name = 'randopony'
staging_release = '2013r1'
staging_dir = (
    '/home/{0}/webapps/{1}{2}'.format(env.user, app_name, staging_release))


@task(default=True)
def deploy_staging():
    """Deploy code to Webfaction staging app and restart it
    """
    rsync_code()
    install_app()
    restart_app()
    restart_staging_supervisor()


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
        'mail',
        'RandoPony.egg-info',
        'requirements.txt',
        'setup.cfg',
        'temp',
        '**/__pycache__',
        '*.sublime-*',
        '.coverage',
        '.coveragerc',
        '*.log',
        '*.pid',
        '*.sqlite',
        '.DS_Store',
        '.hg*',
        '*.pyc',
        '*~',
        )
    rsync_project(
        remote_dir=staging_dir,
        exclude=exclusions,
        delete=True,
        extra_opts='--links',
        )


@task
def install_app():
    """Install staging app on Webfaction
    """
    with cd(staging_dir):
        run('rm -f development.ini production.ini')
        run('rm -rf myapp')
        run('bin/easy_install -U {}'.format(project_name))
        run('chmod 400 lib/python2.7/site-packages/RandoPony-{}-py2.7.egg/'
            'randopony/private_credentials.py'.format(staging_release))
        run('ln -sf {}/staging.ini'.format(project_name))
        run('ln -sf {}/randopony'.format(project_name))
        sed('bin/start', 'development.ini', 'staging.ini')


@task
def init_staging_db():
    """Initialize staging database on Webfaction
    """
    with cd(staging_dir):
        run('bin/initialize_RandoPony_db staging.ini')


@task
def restart_app():
    """Restart app on webfaction
    """
    with cd(staging_dir):
        run('bin/restart')


@task
def start_app():
    """Start app on webfaction
    """
    with cd(staging_dir):
        run('bin/start')


@task
def stop_app():
    """Stop app on webfaction
    """
    with cd(staging_dir):
        run('bin/stop')


@task
def tail_staging_app_log():
    """Tail the staging app log file
    """
    with cd(staging_dir):
        run('tail pyramid.log')


@task
def restart_staging_supervisor():
    """Restart supervisord daemon
    """
    with cd(staging_dir):
        stop_staging_supervisor()
        while exists('supervisord.pid'):
            sleep(1)
        sleep(3)
        start_staging_supervisor()


@task
def start_staging_supervisor():
    """Start supervisord daemon
    """
    with cd(staging_dir):
        run('bin/supervisord -c staging.ini')


@task
def stop_staging_supervisor():
    """Stop supervisord daemon
    """
    with cd(staging_dir):
        run('kill $(cat supervisord.pid)')


@task
def tail_staging_supervisor_log():
    """Tail the staging supervisord log file
    """
    with cd(staging_dir):
        run('tail supervisord.log')


@task
def tail_staging_celery_log():
    """Tail the staging celery log file
    """
    with cd(staging_dir):
        run('tail celery.log')
