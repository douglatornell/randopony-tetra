from celery import current_app as celery
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.config import Configurator
from pyramid.security import ALL_PERMISSIONS
from pyramid.security import Allow
from sqlalchemy import engine_from_config
from sqlalchemy.orm.exc import NoResultFound
import celery_config
from .credentials import (
    persona_secret,
    google_drive_username,
    google_drive_password,
    email_host_username,
    email_host_password,
    )
from .models import Administrator
from .models.meta import (
    DBSession,
    Base,
    )


class Root(object):
    """Simplest possible resource tree to map groups to permissions.
    """
    __acl__ = [
        (Allow, 'g:admin', ALL_PERMISSIONS),
    ]

    def __init__(self, request):
        self.request = request


def groupfinder(userid, request):
    """Check userid against Administrator data model.

    If userid is a known Persona email address, the user is an admin.
    """
    query = DBSession.query(Administrator).\
                filter(Administrator.persona_email == userid)
    try:
        query.one()
        return ['g:admin']
    except NoResultFound:
        return None


def main(global_config, **settings):  # pragma: no cover
    """ Configure RandoPony and return its Pyramid WSGI application.
    """
    settings.update({
        'persona.secret': persona_secret,
        'google_drive.username': google_drive_username,
        'google_drive.password': google_drive_password,
        })
    if email_host_username:
        settings.update({'mail.username': email_host_username})
    if email_host_password:
        settings.update({'mail.password': email_host_password})
    config = Configurator(
        settings=settings,
        root_factory=Root)
    config.add_static_view('static', 'static', cache_max_age=3600)
    authn_policy = AuthTktAuthenticationPolicy(
        settings['persona.secret'],
        hashalg='sha512',
        callback=groupfinder)
    config.set_authentication_policy(authn_policy)
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
    config.add_route('admin.home', '/admin/')
    config.add_route('admin.list', '/admin/{list}/')
    config.add_route('admin.delete', '/admin/{list}/{item}/delete')
    # brevet admin routes
    config.add_route('admin.brevets.create', '/admin/brevets/new')
    config.add_route('admin.brevets.edit', '/admin/brevets/{item}/edit')
    config.add_route('admin.brevets.view', '/admin/brevets/{item}')
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
