# -*- coding: utf-8 -*-
"""Tests for RandoPony admin views and functionality.
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


class TestCoreAdminViews(unittest.TestCase):
    """Unit tests for core admin interface views.
    """
    def _get_target_class(self):
        from ..views.admin.core import AdminViews
        return AdminViews

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

    def test_home_logout_button(self):
        """admin home view has logout button
        """
        request = testing.DummyRequest()
        admin = self._make_one(request)
        tmpl_vars = admin.home()
        self.assertEqual(tmpl_vars, {'logout_btn': True})

    def test_wranglers_list(self):
        """admin wranglers view has expected template variables
        """
        request = testing.DummyRequest()
        request.matchdict['list'] = 'wranglers'
        admin = self._make_one(request)
        tmpl_vars = admin.items_list()
        self.assertTrue(tmpl_vars['logout_btn'])
        self.assertEqual(tmpl_vars['list'], 'wranglers')
        self.assertEqual(tmpl_vars['list_title'], 'Pony Wranglers')
        self.assertEqual(tmpl_vars['action'], 'edit')

    def test_wranglers_list_order(self):
        """admin wranglers list is alpha ordered by persona email"""
        from ..models import Administrator
        with transaction.manager:
            admin = Administrator(persona_email='tom@example.com')
            DBSession.add(admin)
            admin = Administrator(persona_email='harry@example.com')
            DBSession.add(admin)
        request = testing.DummyRequest()
        request.matchdict['list'] = 'wranglers'
        admin = self._make_one(request)
        tmpl_vars = admin.items_list()
        admins = [admin.persona_email for admin in tmpl_vars['items'].all()]
        self.assertEqual(
            admins, 'harry@example.com tom@example.com'.split())

    def test_delete_cancel(self):
        """admin delete cancel leaves item in database
        """
        from ..models import Administrator
        with transaction.manager:
            admin = Administrator(persona_email='tom@example.com')
            DBSession.add(admin)
        self.config.add_route('admin.list', '/admin/{list}/')
        request = testing.DummyRequest(post={'cancel': 'cancel'})
        request.matchdict['list'] = 'wranglers'
        request.matchdict['item'] = 'tom@example.com'
        admin = self._make_one(request)
        admin.delete()
        wrangler = DBSession.query(Administrator).first()
        self.assertEqual(wrangler.persona_email, 'tom@example.com')

    def test_delete_wrangler_confirmation(self):
        """admin delete confirmation view for wrangler has exp template vars
        """
        self.config.add_route('admin.list', '/admin/{list}/')
        request = testing.DummyRequest()
        request.matchdict['list'] = 'wranglers'
        request.matchdict['item'] = 'tom@example.com'
        admin = self._make_one(request)
        tmpl_vars = admin.delete()
        self.assertEqual(
            tmpl_vars,
            {
                'logout_btn': True,
                'list': 'wranglers',
                'item': 'tom@example.com',
                'item_type': 'administrator',
            })

    def test_delete_wrangler(self):
        """admin delete for wrangler deletes item from database
        """
        from sqlalchemy.orm.exc import NoResultFound
        from ..models import Administrator
        with transaction.manager:
            admin = Administrator(persona_email='tom@example.com')
            DBSession.add(admin)
        self.config.add_route('admin.list', '/admin/{list}/')
        request = testing.DummyRequest(post={'delete': 'delete'})
        request.matchdict['list'] = 'wranglers'
        request.matchdict['item'] = 'tom@example.com'
        admin = self._make_one(request)
        admin.delete()
        query = DBSession.query(Administrator)
        with self.assertRaises(NoResultFound):
            query.filter_by(persona_email='tom@example.com').one()

    def test_delete_brevet(self):
        """admin delete for brevet deletes item from database
        """
        from sqlalchemy.orm.exc import NoResultFound
        from ..models import core
        from ..models import Brevet
        with transaction.manager:
            brevet = Brevet(
                region='LM',
                distance=200,
                date_time=datetime(2012, 11, 11, 7, 0, 0),
                route_name='11th Hour',
                start_locn='Bean Around the World Coffee, Lonsdale Quay, '
                           '123 Carrie Cates Ct, North Vancouver',
                organizer_email='tracy@example.com',
                )
            brevet_id = str(brevet)
            DBSession.add(brevet)
        self.config.add_route('admin.list', '/admin/{list}/')
        request = testing.DummyRequest(post={'delete': 'delete'})
        request.matchdict['list'] = 'brevets'
        request.matchdict['item'] = brevet_id
        with patch.object(core, 'datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2012, 11, 1, 12, 55, 42)
            admin = self._make_one(request)
        admin.delete()
        with self.assertRaises(NoResultFound):
            Brevet.get_current().one()
