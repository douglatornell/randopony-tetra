# -*- coding: utf-8 -*-
"""Fixtures for RandoPony app test suite.
"""
import pytest
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
