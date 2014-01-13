"""Fabric tasks for RandoPony-tetra web app.
"""
from getpass import getpass
from time import sleep
import xmlrpclib
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
from fabric.contrib.console import confirm
from fabric.contrib.project import rsync_project


env.user = 'bcrandonneur'
env.hosts = ['bcrandonneur.webfactional.com']
project_name = 'randopony-tetra'
app_name = 'randopony'
staging_release = '2014r1'
staging_dir = (
    '/home/{0}/webapps/{1}{2}'.format(env.user, app_name, staging_release))
env.production_release = '2013r3'
env.production_dir = (
    '/home/{0}/webapps/{1}{2}'
    .format(env.user, app_name, env.production_release))
release_dirs = {
    'staging': staging_dir,
    'production': env.production_dir,
}
staging_domain = '.'.join((app_name, env.hosts[0]))
production_domain = '.'.join((app_name, 'randonneurs.bc.ca'))


@task(default=True)
def deploy_staging():
    """Deploy code to Webfaction staging app and restart it
    """
    rsync_code()
    install_app()
    restart_app(release='staging')
    restart_staging_supervisor()


@task
def promote_staging_to_production():
    """Promote staging deployment to production
    """
    if env.production_release is None:
        confirmation = confirm(
            'Create a new production deployment from {}'
            .format(staging_release))
    else:
        confirmation = confirm(
            'Promote {0} deployment to production with data from {1}'
            .format(staging_release, env.production_release))
    if not confirmation:
        return
    stop_app(release='staging')
    stop_staging_supervisor()
    password = getpass('Webfaction password for API calls: ')
    server = xmlrpclib.ServerProxy('https://api.webfaction.com/')
    session_id, account = server.login(env.user, password)
    sites = server.list_websites(session_id)
    files_to_delete = (
        'RandoPony-staging.sqlite '
        'celery.sqlite '
        'supervisord.log '
        'celery.log '
        'pyramid.log '
        'staging.ini '
        .split())
    with cd(staging_dir):
        for delete_file in files_to_delete:
            run('rm -f {}'.format(delete_file))
        run('ln -sf {}/production.ini'.format(project_name))
        sed('bin/start', 'staging.ini', 'production.ini')
        if env.production_release is None:
            run('bin/initialize_RandoPony_db production.ini')
        else:
            stop_app(release='production')
            stop_production_supervisor()
            site = [
                site for site in sites
                if site['name'] == app_name + env.production_release][0]
            server.update_website(
                session_id, site['name'], site['ip'], site['https'],
                [], *site['website_apps'])
            run('cp {0}/RandoPony-production.sqlite {0}/celery.sqlite {1}'
                .format(env.production_dir, staging_dir))
    site = [
        site for site in sites
        if site['name'] == app_name + staging_release][0]
    server.update_website(
        session_id, site['name'], site['ip'], site['https'],
        [production_domain], *site['website_apps'])
    # Staging is now production
    env.production_release = staging_release
    env.production_dir = staging_dir
    start_app(release='production')
    start_production_supervisor()


@task
def init_staging():
    """Initial staging deployment to Webfaction
    """
    init_staging_app()
    rsync_code()
    install_app()
    init_staging_db()


@task
def init_staging_app():
    """Create & initialize a new staging app on Webfaction
    """
    password = getpass('Webfaction password for API calls: ')
    server = xmlrpclib.ServerProxy('https://api.webfaction.com/')
    session_id, account = server.login(env.user, password)
    server.create_app(session_id, app_name + staging_release, 'pyramid_14_27')
    machines = server.list_ips(session_id)
    ip = machines[0]['ip']
    server.create_website(
        session_id, app_name + staging_release, ip, False, [staging_domain],
        (app_name + staging_release, '/'))


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
def restart_app(release):
    """Restart app on webfaction
    """
    with cd(release_dirs[release]):
        run('bin/restart')


@task
def start_app(release):
    """Start app on webfaction
    """
    with cd(release_dirs[release]):
        run('bin/start')


@task
def stop_app(release):
    """Stop app on webfaction
    """
    with cd(release_dirs[release]):
        if exists('pyramid.pid'):
            run('bin/stop')
            sleep(3)
            run('rm pyramid.pid')


@task
def tail_app_log(release):
    """Tail the app log file
    """
    with cd(release_dirs[release]):
        run('tail pyramid.log')


@task
def restart_staging_supervisor():
    """Restart staging supervisord daemon
    """
    with cd(staging_dir):
        stop_staging_supervisor()
        while exists('supervisord.pid'):
            sleep(1)
        sleep(3)
        start_staging_supervisor()


@task
def start_staging_supervisor():
    """Start staging supervisord daemon
    """
    with cd(staging_dir):
        run('bin/supervisord -c staging.ini')


@task
def stop_staging_supervisor():
    """Stop staging supervisord daemon
    """
    with cd(staging_dir):
        if exists('supervisord.pid'):
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


@task
def restart_production_supervisor():
    """Restart production supervisord daemon
    """
    with cd(env.production_dir):
        stop_production_supervisor()
        while exists('supervisord.pid'):
            sleep(1)
        sleep(3)
        start_production_supervisor()


@task
def start_production_supervisor():
    """Start production supervisord daemon
    """
    with cd(env.production_dir):
        run('bin/supervisord -c production.ini')


@task
def stop_production_supervisor():
    """Stop production supervisord daemon
    """
    with cd(env.production_dir):
        while exists('supervisord.pid'):
            run('kill $(cat supervisord.pid)')
            sleep(1)


@task
def tail_production_supervisor_log():
    """Tail the production supervisord log file
    """
    with cd(env.production_dir):
        run('tail $HOME/logs/user/randopony_supervisord.log')


@task
def tail_production_celery_log():
    """Tail the production celery log file
    """
    with cd(env.production_dir):
        run('tail $HOME/logs/user/randopony_celery.log')

@task
def ps():
    """Process status for bcrandonneur user
    """
    run('ps -u {.user} -o pid,rss,command'.format(env))
