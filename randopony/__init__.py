from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .models import (
    DBSession,
    Base,
    )


def main(global_config, **settings):
    """ Configure RandoPony and return its Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings)
    config.include('pyramid_persona')
    config.add_static_view('static', 'static', cache_max_age=3600)
    map_routes(config)
    config.scan()
    return config.make_wsgi_app()


def map_routes(config):
    """Routes map for RandoPony.
    """
    config.add_route('home', '/')
    # admin routes
    config.add_route('admin', '/admin')
