# -*- coding: utf-8 -*-
"""Tests for RandoPony public site core views and functionality.
"""
import unittest
try:
    from unittest.mock import patch
except ImportError:                  # pragma: no cover
    from mock import patch
from pyramid import testing
import pytest
from sqlalchemy import create_engine
from ..models.meta import (
    Base,
    DBSession,
)


@pytest.fixture(scope='module')
def site_core_module():
    from ..views.site import core
    return core


class TestSiteViews(unittest.TestCase):
    """Unit tests for public site views.
    """
    def _get_target_class(self):
        from ..views.site.core import SiteViews
        return SiteViews

    def _make_one(self, *args, **kwargs):
        from ..views.site import core
        with patch.object(core, 'get_membership_link'):
            return self._get_target_class()(*args, **kwargs)

    def setUp(self):
        self.config = testing.setUp()
        engine = create_engine('sqlite://')
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_init(self):
        """SiteViews constructor sets request & tmpl_vars attrs
        """
        request = testing.DummyRequest()
        views = self._make_one(request)
        self.assertEqual(views.request, request)
        self.assertIn('brevets', views.tmpl_vars)
        self.assertIn('populaires', views.tmpl_vars)
        self.assertIn('membership_link', views.tmpl_vars)

    def test_home(self):
        """home view has home tab set as active tab
        """
        request = testing.DummyRequest()
        views = self._make_one(request)
        tmpl_vars = views.home()
        self.assertEqual(tmpl_vars['active_tab'], 'home')

    def test_organizer_info(self):
        """organizer_info view has expected tmpl_vars
        """
        from ..models import EmailAddress
        email = EmailAddress(key='admin_email', email='tom@example.com')
        DBSession.add(email)
        request = testing.DummyRequest()
        views = self._make_one(request)
        tmpl_vars = views.organizer_info()
        self.assertEqual(tmpl_vars['active_tab'], 'organizer-info')
        self.assertEqual(tmpl_vars['admin_email'], 'tom@example.com')

    def test_about(self):
        """about view has about tab set as active tab
        """
        request = testing.DummyRequest()
        views = self._make_one(request)
        tmpl_vars = views.about()
        self.assertEqual(tmpl_vars['active_tab'], 'about')

    def test_notfound(self):
        """notfound view has no active tab and 404 status
        """
        request = testing.DummyRequest()
        views = self._make_one(request)
        tmpl_vars = views.notfound()
        self.assertIsNone(tmpl_vars['active_tab'])
        self.assertEqual(request.response.status, '404 Not Found')


@pytest.mark.usefixtures('db_session', 'site_core_module')
class TestGetMembershipLink(object):
    """Unit test for get_membership_link() function.
    """
    def test_get_membership_link(self, db_session, site_core_module):
        """returns club membership sign-up site URL from database
        """
        from ..models import Link
        link = Link(key='membership_link', url='https://membership_link/')
        db_session.add(link)
        membership_link = site_core_module.get_membership_link()
        assert membership_link == 'https://membership_link/'
