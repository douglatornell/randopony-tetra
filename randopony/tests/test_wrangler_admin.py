# -*- coding: utf-8 -*-
"""Tests for RandoPony administrator (aka wrangler) admin views and
functionality.
"""
import unittest
try:
    from unittest.mock import MagicMock
except ImportError:                      # pragma: no cover
    from mock import MagicMock
from pyramid import testing
from sqlalchemy import create_engine
from ..models.meta import (
    Base,
    DBSession,
)


class TestWranglerCreate(unittest.TestCase):
    """Unit tests for administrator (aka pony wrangler) object creation
       admin interface views.

       *TODO*: Add integration tests:

         * form renders empty email input control
         * POST with valid email address adds record to database
         * POST with email address already in db fails gracefully
    """
    def _get_target_class(self):
        from ..views.admin.wrangler import WranglerCreate
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

    def test_list_url(self):
        """list_url returns expected wranglers list URL
        """
        self.config.add_route('admin.list', '/admin/{list}/')
        request = testing.DummyRequest()
        create = self._make_one(request)
        url = create.list_url()
        self.assertEqual(url, 'http://example.com/admin/wranglers/')

    def test_show(self):
        """show returns expected template variables
        """
        from .. import __pkg_metadata__ as version
        self.config.add_route('admin.list', '/admin/{list}/')
        request = testing.DummyRequest()
        create = self._make_one(request)
        mock_form = MagicMock(name='form')
        tmpl_vars = create.show(mock_form)
        self.assertEqual(
            tmpl_vars,
            {
                'version': version.number + version.release,
                'form': mock_form.render(),
                'list_url': 'http://example.com/admin/wranglers/',
            })

    def test_add_success(self):
        """create wrangler success adds persona email to database
        """
        from ..models import Administrator
        self.config.add_route('admin.list', '/admin/{list}/')
        request = testing.DummyRequest()
        create = self._make_one(request)
        url = create.add_success({'persona_email': 'tom@example.com'})
        wrangler = DBSession.query(Administrator).first()
        self.assertEqual(wrangler.persona_email, 'tom@example.com')
        self.assertEqual(url.location, 'http://example.com/admin/wranglers/')

    def test_failure(self):
        """create wrangler failure returns expected template variables
        """
        from .. import __pkg_metadata__ as version
        self.config.add_route('admin.list', '/admin/{list}/')
        request = testing.DummyRequest()
        create = self._make_one(request)
        mock_val_err = MagicMock(name='ValidationError')
        tmpl_vars = create.failure(mock_val_err)
        self.assertEqual(
            tmpl_vars,
            {
                'version': version.number + version.release,
                'form': mock_val_err.render(),
                'list_url': 'http://example.com/admin/wranglers/',
            })


class TestWranglerEdit(unittest.TestCase):
    """Unit tests for administrator (aka pony wrangler) object edit
       admin interface views.

       *TODO*: Add integration tests:

         * form renders populated email input control
         * POST with valid email address updates record in database
    """
    def _get_target_class(self):
        from ..views.admin.wrangler import WranglerEdit
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
        admin = Administrator(persona_email='tom@example.com')
        DBSession.add(admin)
        self.config.add_route('admin.list', '/admin/{list}/')
        request = testing.DummyRequest()
        request.matchdict['item'] = 'tom@example.com'
        edit = self._make_one(request)
        appstruct = edit.appstruct()
        self.assertEqual(
            appstruct, {
                'id': 1,
                'persona_email': 'tom@example.com',
            })

    def test_show(self):
        """admin edit wrangler show returns expected template variables
        """
        from .. import __pkg_metadata__ as version
        from ..models import Administrator
        admin = Administrator(persona_email='tom@example.com')
        DBSession.add(admin)
        self.config.add_route('admin.list', '/admin/{list}/')
        request = testing.DummyRequest()
        request.matchdict['item'] = 'tom@example.com'
        edit = self._make_one(request)
        mock_form = MagicMock(name='form')
        tmpl_vars = edit.show(mock_form)
        self.assertEqual(
            tmpl_vars,
            {
                'version': version.number + version.release,
                'form': mock_form.render(),
                'list_url': 'http://example.com/admin/wranglers/',
            })

    def test_save_success(self):
        """admin edit wrangler success updates persona email in database
        """
        from ..models import Administrator
        admin = Administrator(persona_email='tom@example.com')
        DBSession.add(admin)
        self.config.add_route('admin.list', '/admin/{list}/')
        request = testing.DummyRequest()
        edit = self._make_one(request)
        url = edit.save_success({
            'id': 1,
            'persona_email': 'harry@example.com',
        })
        wrangler = DBSession.query(Administrator).first()
        self.assertEqual(wrangler.persona_email, 'harry@example.com')
        self.assertEqual(
            url.location, 'http://example.com/admin/wranglers/')

    def test_failure(self):
        """admin edit wrangler failure returns expected template variables
        """
        from .. import __pkg_metadata__ as version
        self.config.add_route('admin.list', '/admin/{list}/')
        request = testing.DummyRequest()
        edit = self._make_one(request)
        mock_val_err = MagicMock(name='ValidationError')
        tmpl_vars = edit.failure(mock_val_err)
        self.assertEqual(
            tmpl_vars,
            {
                'version': version.number + version.release,
                'form': mock_val_err.render(),
                'list_url': 'http://example.com/admin/wranglers/',
            })
