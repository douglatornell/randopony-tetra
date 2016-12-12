import os

from celery import current_app as celery
from pyramid.session import SignedCookieSessionFactory

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.settings import asbool
from sqlalchemy import engine_from_config
from stormpath.client import Client

from . import (
    celery_config,
    credentials,
)
from .models import Administrator
from .models.meta import (
    DBSession,
    Base,
)
from .views.admin import core as admin_core


def main(global_config, **settings):  # pragma: no cover
    """ Configure RandoPony and return its Pyramid WSGI application.
    """
    authn_policy = AuthTktAuthenticationPolicy(
        credentials.auth_tkt_secret,
        hashalg='sha512',
        callback=admin_core.group_finder,
    )
    authz_policy = ACLAuthorizationPolicy()
    session_factory = SignedCookieSessionFactory(
        credentials.session_cookie_secret)
    stormpath_client = Client(
        api_key_file=os.path.abspath('stormpath-apikey.properties'))
    settings.update({
        'google_drive.username': credentials.google_drive_username,
        'google_drive.password': credentials.google_drive_password,
        'stormpath_app':
            stormpath_client.applications.search({'name': 'RandoPony'})[0],
    })
    if asbool(settings.get('production_deployment', 'false')):
        settings.update({'mail.username': credentials.email_host_username})
        settings.update({'mail.password': credentials.email_host_password})
    config = Configurator(
        settings=settings,
        authentication_policy=authn_policy,
        authorization_policy=authz_policy,
        session_factory=session_factory,
        root_factory=admin_core.ACLFactory,
    )
    config.include('pyramid_deform')
    config.include('pyramid_mailer')
    config.include('pyramid_mako')
    config.include('pyramid_tm')
    config.add_static_view('static', 'static', cache_max_age=3600)
    map_routes(config)
    config.scan()
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    celery.config_from_object(celery_config)
    return config.make_wsgi_app()


def map_routes(config):               # pragma: no cover
    """Routes map for RandoPony.
    """
    # public site routes
    config.add_route('home', '/')
    config.add_route('organizer-info', '/organizer-info/')
    config.add_route('about', '/about-pony/')
    # brevet routes
    config.add_route('region.list', '/brevets/')
    config.add_route('brevet.list', '/brevets/{region}/')
    config.add_route('brevet', '/brevets/{region}/{distance}/{date}')
    config.add_route(
        'brevet.entry',
        '/brevets/{region}/{distance}/{date}/entry')
    config.add_route(
        'brevet.rider_emails',
        '/brevets/{region}/{distance}/{date}/rider_emails/{uuid}')
    # legacy routes to cover when /brevets/ was /register/
    config.add_route('register', '/register/')
    config.add_route('register.region', '/register/{region}-events/')
    config.add_route('register.brevet', '/register/{region}{distance}/{date}/')
    # populaire routes
    config.add_route('populaire.list', '/populaires/')
    config.add_route('populaire', '/populaires/{short_name}')
    config.add_route('populaire.entry', '/populaires/{short_name}/entry')
    config.add_route(
        'populaire.rider_emails',
        '/populaires/{short_name}/rider_emails/{uuid}')
    # admin core routes
    config.add_route('admin.login', 'admin/login')
    config.add_route('admin.login.handler', 'admin/login.handler')
    config.add_route('admin.logout', 'admin/logout')
    config.add_route('admin.home', '/admin/')
    config.add_route('admin.list', '/admin/{list}/')
    config.add_route('admin.delete', '/admin/{list}/{item}/delete')
    # brevet admin routes
    config.add_route('admin.brevets.create', '/admin/brevets/new')
    config.add_route('admin.brevets.edit', '/admin/brevets/{item}/edit')
    config.add_route('admin.brevets.view', '/admin/brevets/{item}')
    config.add_route(
        'admin.brevets.create_rider_list',
        'admin/brevet/{item}/create_rider_list')
    config.add_route(
        'admin.brevets.email_to_organizer',
        'admin.brevet/{item}/email_to_organizer')
    config.add_route(
        'admin.brevets.email_to_webmaster',
        'admin.brevet/{item}/email_to_webmaster')
    config.add_route(
        'admin.brevets.setup_123',
        'admin.brevet/{item}/setup_123')
    # populaire admin routes
    config.add_route('admin.populaires.create', '/admin/populaire/new')
    config.add_route('admin.populaires.edit', '/admin/populaire/{item}/edit')
    config.add_route('admin.populaires.view', '/admin/populaire/{item}')
    config.add_route(
        'admin.populaires.create_rider_list',
        'admin/populaire/{item}/create_rider_list')
    config.add_route(
        'admin.populaires.email_to_organizer',
        'admin.populaire/{item}/email_to_organizer')
    config.add_route(
        'admin.populaires.email_to_webmaster',
        'admin.populaire/{item}/email_to_webmaster')
    config.add_route(
        'admin.populaires.setup_123',
        'admin.populaire/{item}/setup_123')
    # administrators (aka pony wranglers) admin routes
    config.add_route('admin.wranglers.create', '/admin/wranglers/new')
    config.add_route('admin.wranglers.edit', '/admin/wranglers/{item}')
