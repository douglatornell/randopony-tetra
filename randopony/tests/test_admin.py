# -*- coding: utf-8 -*-
"""Tests for RandoPony admin views and functionality.
"""
import unittest
from pyramid import testing
from sqlalchemy import create_engine
import transaction
from ..models import (
    Base,
    DBSession,
    )


class TestAdminViews(unittest.TestCase):
    """Unit tests for admin interface views.
    """
    def _get_target_class(self):
        from ..views.admin import AdminViews
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

    def test_add_wrangler_form(self):
        """admin form to add new wrangler has empty input control
        """
        self.config.add_route('admin.list', '/admin/wranglers/')
        request = testing.DummyRequest()
        request.matchdict['item'] = 'new'
        admin = self._make_one(request)
        tmpl_vars = admin.wrangler()
        self.assertIn(
            '<input type="text" name="persona_email" value=""',
            tmpl_vars['form'])

    def test_add_wrangler(self):
        """admin add wrangler POST adds persona email to database
        """
        from ..models import Administrator
        self.config.add_route('admin.list', '/admin/wranglers/')
        request = testing.DummyRequest(
            post={'add': 'add', 'persona_email': 'tom@example.com'})
        request.matchdict['item'] = 'new'
        admin = self._make_one(request)
        admin.wrangler()
        wrangler = DBSession.query(Administrator).first()
        self.assertEqual(wrangler.persona_email, 'tom@example.com')

    def test_update_wrangler_form(self):
        """admin form to update wrangler has persona email input control value
        """
        self.config.add_route('admin.list', '/admin/wranglers/')
        request = testing.DummyRequest()
        request.matchdict['item'] = 'tom@example.com'
        admin = self._make_one(request)
        tmpl_vars = admin.wrangler()
        self.assertIn(
            '<input type="text" name="persona_email" value="tom@example.com"',
            tmpl_vars['form'])

    def test_update_wrangler(self):
        """admin update wrangler POST changes persona email in database
        """
        from ..models import Administrator
        with transaction.manager:
            admin = Administrator(persona_email='tom@example.com')
            DBSession.add(admin)
        self.config.add_route('admin.list', '/admin/wranglers/')
        request = testing.DummyRequest(
            post={'save': 'save', 'persona_email': 'harry@example.com'})
        request.matchdict['item'] = 'tom@example.com'
        admin = self._make_one(request)
        admin.wrangler()
        wrangler = DBSession.query(Administrator).first()
        self.assertEqual(wrangler.persona_email, 'harry@example.com')

    def test_delete_wrangler_confirmation(self):
        """admin delete confirmation view for wrangler has exp template vars
        """
        self.config.add_route('admin.list', '/admin/wranglers/')
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
        self.config.add_route('admin.list', '/admin/wranglers/')
        request = testing.DummyRequest(post={'delete': 'delete'})
        request.matchdict['list'] = 'wranglers'
        request.matchdict['item'] = 'tom@example.com'
        admin = self._make_one(request)
        admin.delete()
        query = DBSession.query(Administrator)
        with self.assertRaises(NoResultFound):
            query.filter_by(persona_email='tom@example.com').one()
