# -*- coding: utf-8 -*-
"""Tests for RandoPony admin views and functionality.
"""
import unittest
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


class TestWranglerCreate(unittest.TestCase):
    """Unit tests for administrator (aka pony wrangler) object creation
       admin interface views.

       *TODO*: Add integration tests:

         * form renders empty email input control
         * POST with valid email address adds record to database
         * POST with email address already in db fails gracefully
    """
    def _get_target_class(self):
        from ..views.admin import WranglerCreate
        return WranglerCreate

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

    def test_add_success(self):
        """admin add wrangler success adds persona email to database
        """
        from ..models import Administrator
        self.config.add_route('admin.list', '/admin/wranglers/')
        request = testing.DummyRequest()
        create = self._make_one(request)
        create.add_success({'persona_email': 'tom@example.com'})
        wrangler = DBSession.query(Administrator).first()
        self.assertEqual(wrangler.persona_email, 'tom@example.com')


class TestWranglerEdit(unittest.TestCase):
    """Unit tests for administrator (aka pony wrangler) object edit
       admin interface views.

       *TODO*: Add integration tests:

         * form renders populated email input control
         * POST with valid email address updates record in database
    """
    def _get_target_class(self):
        from ..views.admin import WranglerEdit
        return WranglerEdit

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

    def test_appstruct(self):
        """admin edit wrangler appstruct method returns dict to populate form
        """
        from ..models import Administrator
        with transaction.manager:
            admin = Administrator(persona_email='tom@example.com')
            DBSession.add(admin)
        self.config.add_route('admin.list', '/admin/wranglers/')
        request = testing.DummyRequest()
        request.matchdict['item'] = 'tom@example.com'
        edit = self._make_one(request)
        appstruct = edit.appstruct()
        self.assertEqual(
            appstruct, {
                'id': 1,
                'persona_email': 'tom@example.com',
            })

    def test_save_success(self):
        """admin edit wrangler success updates persona email in database
        """
        from ..models import Administrator
        with transaction.manager:
            admin = Administrator(persona_email='tom@example.com')
            DBSession.add(admin)
        self.config.add_route('admin.list', '/admin/wranglers/')
        request = testing.DummyRequest()
        edit = self._make_one(request)
        edit.save_success({
            'id': 1,
            'persona_email': 'harry@example.com',
            })
        wrangler = DBSession.query(Administrator).first()
        self.assertEqual(wrangler.persona_email, 'harry@example.com')
