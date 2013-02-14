# -*- coding: utf-8 -*-
"""Tests for RandoPony public site core views and functionality.
"""
from datetime import datetime
import unittest
try:
    from unittest.mock import (
        MagicMock,
        patch,
        )
except ImportError:                  # pragma: no cover
    from mock import (
        MagicMock,
        patch,
        )
from pyramid import testing
from sqlalchemy import create_engine
from ..models.meta import (
    Base,
    DBSession,
    )


class TestSiteViews(unittest.TestCase):
    """Unit tests for public site views.
    """
    def _get_target_class(self):
        from ..views.site.core import SiteViews
        return SiteViews

    def _make_one(self, *args, **kwargs):
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
