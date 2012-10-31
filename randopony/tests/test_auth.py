# -*- coding: utf-8 -*-
"""Unit tests for RandoPony auth configuration.
"""
import unittest
from pyramid import testing
from sqlalchemy import create_engine
import transaction
from ..models import DBSession


class TestAuthConfig(unittest.TestCase):
    """Unit tests for auth configuration.
    """
    def setUp(self):
        from ..models import (
            Base,
            )
        self.config = testing.setUp()
        engine = create_engine('sqlite://')
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_acl(self):
        """ACL gives admin group all permissions
        """
        from pyramid.security import ALL_PERMISSIONS
        from pyramid.security import Allow
        from .. import Root
        request = testing.DummyRequest()
        root = Root(request)
        self.assertEqual(root.__acl__, [(Allow, 'g:admin', ALL_PERMISSIONS)])

    def test_groupfinder_known_user_admin_group(self):
        """groupfinder returns admin group for known user"""
        from .. import groupfinder
        from ..models import Administrator
        with transaction.manager:
            admin = Administrator(persona_email='tom@example.com')
            DBSession.add(admin)
        request = testing.DummyRequest()
        groups = groupfinder('tom@example.com', request)
        self.assertEqual(groups, ['g:admin'])

    def test_groupfinder_unkown_user(self):
        """groupfinder returns None for unknown user"""
        from .. import groupfinder
        request = testing.DummyRequest()
        self.assertIsNone(groupfinder('harry@example.com', request))
