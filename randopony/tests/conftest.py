# -*- coding: utf-8 -*-
"""Fixtures for RandoPony app test suite.
"""
import pytest
from pyramid import testing
from sqlalchemy import create_engine

from ..models.meta import (
    Base,
    DBSession,
)


@pytest.yield_fixture(scope='function')
def db_session():
    engine = create_engine('sqlite://')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    yield DBSession
    DBSession.remove()


@pytest.yield_fixture(scope='function')
def pyramid_config():
    config = testing.setUp(request=testing.DummyRequest())
    config.registry.settings['timezone'] = 'Canada/Pacific'
    config.registry.settings['mako.directories'] = 'randopony:templates'
    config.include('pyramid_mako')
    yield config
    testing.tearDown()


@pytest.fixture(scope='session')
def core_model():
    from ..models import core
    return core


@pytest.fixture(scope='session')
def link_model():
    from ..models import Link
    return Link


@pytest.fixture(scope='session')
def email_address_model():
    from ..models import EmailAddress
    return EmailAddress


@pytest.fixture(scope='session')
def brevet_model():
    from ..models import Brevet
    return Brevet


@pytest.fixture(scope='session')
def brevet_rider_model():
    from ..models import BrevetRider
    return BrevetRider


@pytest.fixture(scope='session')
def pop_model():
    from ..models import Populaire
    return Populaire


@pytest.fixture(scope='session')
def pop_rider_model():
    from ..models import PopulaireRider
    return PopulaireRider


@pytest.fixture(scope='module')
def views_core_module():
    from ..views.site import core
    return core

