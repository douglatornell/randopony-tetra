# -*- coding: utf-8 -*-
"""Tests for RandoPony public site core views and functionality.
"""
from datetime import datetime
import unittest
try:
    from unittest.mock import patch
except ImportError:                  # pragma: no cover
    from mock import patch           # pragma: no cover
from pyramid import testing
from sqlalchemy import create_engine
import transaction
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
        with transaction.manager:
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

    def test_region_list(self):
        """region_list view has expected tmpl_vars
        """
        from ..models import (
            Brevet,
            EmailAddress,
            )
        email = EmailAddress(key='admin_email', email='tom@example.com')
        with transaction.manager:
            DBSession.add(email)
        request = testing.DummyRequest()
        views = self._make_one(request)
        tmpl_vars = views.region_list()
        self.assertEqual(tmpl_vars['active_tab'], 'brevets')
        self.assertEqual(tmpl_vars['regions'], Brevet.REGIONS)
        self.assertEqual(
            tmpl_vars['region_brevets'].keys(), Brevet.REGIONS.keys())
        self.assertEqual(tmpl_vars['admin_email'], 'tom@example.com')

    def test_region_list_brevet(self):
        """region_list view has expected tmpl_vars
        """
        from ..models import core
        from ..models import (
            Brevet,
            EmailAddress,
            )
        brevet = Brevet(
            region='LM',
            distance=200,
            date_time=datetime(2012, 11, 11, 7, 0, 0), route_name='11th Hour',
            start_locn='Bean Around the World Coffee, Lonsdale Quay, '
                       '123 Carrie Cates Ct, North Vancouver',
            organizer_email='tracy@example.com',
            )
        brevet_id = str(brevet)
        email = EmailAddress(key='admin_email', email='tom@example.com')
        with transaction.manager:
            DBSession.add(brevet)
            DBSession.add(email)
        request = testing.DummyRequest()
        with patch.object(core, 'datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2012, 11, 1, 12, 55, 42)
            views = self._make_one(request)
            tmpl_vars = views.region_list()
        self.assertEqual(
            str(tmpl_vars['region_brevets']['LM'].one()), brevet_id)

    def test_brevet_list(self):
        """brevet_list view has expected tmpl_vars
        """
        from ..models import core
        from ..models import (
            Brevet,
            EmailAddress,
            )
        brevet = Brevet(
            region='LM',
            distance=200,
            date_time=datetime(2012, 11, 11, 7, 0, 0), route_name='11th Hour',
            start_locn='Bean Around the World Coffee, Lonsdale Quay, '
                       '123 Carrie Cates Ct, North Vancouver',
            organizer_email='tracy@example.com',
            )
        brevet_id = str(brevet)
        email = EmailAddress(key='admin_email', email='tom@example.com')
        with transaction.manager:
            DBSession.add(brevet)
            DBSession.add(email)
        request = testing.DummyRequest()
        request.matchdict['region'] = 'LM'
        with patch.object(core, 'datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2012, 11, 1, 12, 55, 42)
            views = self._make_one(request)
            tmpl_vars = views.brevet_list()
        self.assertEqual(tmpl_vars['active_tab'], 'brevets')
        self.assertEqual(tmpl_vars['region'], 'LM')
        self.assertEqual(tmpl_vars['regions'], Brevet.REGIONS)
        self.assertEqual(
            str(tmpl_vars['region_brevets'].one()), brevet_id)
        self.assertEqual(
            tmpl_vars['image'], {
                'file': 'LowerMainlandQuartet.jpg',
                'alt': 'Harrison Hotsprings Road',
                'credit': 'Nobo Yonemitsu',
            })

    def test_populaire_list(self):
        """populaire_list view has expected tmpl_vars
        """
        from ..models import EmailAddress
        email = EmailAddress(key='admin_email', email='tom@example.com')
        with transaction.manager:
            DBSession.add(email)
        request = testing.DummyRequest()
        views = self._make_one(request)
        tmpl_vars = views.populaire_list()
        self.assertEqual(tmpl_vars['active_tab'], 'populaires')
        self.assertEqual(tmpl_vars['admin_email'], 'tom@example.com')
