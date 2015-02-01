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
