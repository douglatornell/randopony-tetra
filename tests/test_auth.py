"""Unit tests for RandoPony auth configuration.
"""
import unittest

from pyramid import security
from pyramid import testing
from sqlalchemy import create_engine

from randopony.models.meta import (
    Base,
    DBSession,
)


class TestAuthConfig(unittest.TestCase):
    """Unit tests for auth configuration.
    """
    def setUp(self):
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
        from randopony.views.admin.core import ACLFactory
        request = testing.DummyRequest()
        root = ACLFactory(request)
        self.assertEqual(
            root.__acl__,
            [(security.Allow, security.Authenticated, 'authenticated')])

    def test_groupfinder_known_user_admin_group(self):
        """groupfinder returns admin group for known user"""
        from randopony.views.admin.core import group_finder
        from randopony.models import Administrator
        admin = Administrator(email='tom@example.com', password_hash='hash')
        DBSession.add(admin)
        request = testing.DummyRequest()
        groups = group_finder('tom@example.com', request)
        self.assertEqual(groups, [security.Authenticated])
