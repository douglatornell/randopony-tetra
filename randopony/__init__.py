from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.config import Configurator
from pyramid.security import ALL_PERMISSIONS
from pyramid.security import Allow
from sqlalchemy import engine_from_config
from .models import (
    DBSession,
    Base,
    User,
    )


USERS = {
    'djl@douglatornell.ca': User('djl@douglatornell.ca'),
    'stoker@telus.net': User('stoker@telus.net'),
}


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
        callback=groupfinder)
    config.set_authentication_policy(authn_policy)


def map_routes(config):
    """Routes map for RandoPony.
    """
    config.add_route('home', '/')
    # admin routes
    config.add_route('admin.home', '/admin')


class Root(object):
    """Simplest possible resource tree to map groups to permissions.
    """
    __acl__ = [
        (Allow, 'g:admin', ALL_PERMISSIONS),
    ]

    def __init__(self, request):
        self.request = request


def groupfinder(userid, request):
    user = USERS.get(userid)
    if user:
        return ['g:admin']
