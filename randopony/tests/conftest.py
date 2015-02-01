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
    yield config
    testing.tearDown()
