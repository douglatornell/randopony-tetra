from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.config import Configurator
from pyramid.security import ALL_PERMISSIONS
from pyramid.security import Allow
from sqlalchemy import engine_from_config
from sqlalchemy.orm.exc import NoResultFound
from .models import (
    DBSession,
    Base,
    Administrator,
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


def main(global_config, **settings):
    """ Configure RandoPony and return its Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(
        settings=settings,
        root_factory=Root)
    config.add_static_view('static', 'static', cache_max_age=3600)
    auth_config(config, settings)
    map_routes(config)
    config.scan()
    return config.make_wsgi_app()


def auth_config(config, settings):
    """Authentication configuration.
    """
    config.include('pyramid_persona')
    authn_policy = AuthTktAuthenticationPolicy(
        settings['persona.secret'],
        hashalg='sha512',
        callback=groupfinder)
    config.set_authentication_policy(authn_policy)


def map_routes(config):
    """Routes map for RandoPony.
    """
    config.add_route('home', '/')
    # admin core routes
    config.add_route('admin.home', '/admin')
    config.add_route('admin.list', '/admin/{list}/')
    config.add_route('admin.delete', '/admin/{list}/{item}/delete')
    # brevet admin routes
    config.add_route(
        'admin.brevets.create',
        '/admin/brevets/new',
        )
    config.add_route(
        'admin.brevets.edit',
        '/admin/brevets/{item}/edit',
        )
    config.add_route(
        'admin.brevets.view',
        '/admin/brevets/{item}',
        )
    # administrators (aka pony wranglers) admin routes
    config.add_route(
        'admin.wranglers.create',
        '/admin/wranglers/new',
        )
    config.add_route(
        'admin.wranglers.edit',
        '/admin/wranglers/{item}',
        )
