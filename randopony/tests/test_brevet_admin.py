# -*- coding: utf-8 -*-
"""Tests for RandoPony brevet admin views and functionality.
"""
from datetime import datetime
import unittest
from unittest.mock import MagicMock
from pyramid import testing
from sqlalchemy import create_engine
import transaction
from ..models.meta import (
    Base,
    DBSession,
    )


class TestBrevetDetails(unittest.TestCase):
    """Unit test for brevet details view.
    """
    def setUp(self):
        self.config = testing.setUp()
        engine = create_engine('sqlite://')
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_brevet_details(self):
        """brevet_details view has expected template vsriables
        """
        from ..models import Brevet
        from ..views.admin.brevet import brevet_details
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
        request = testing.DummyRequest()
        request.matchdict['item'] = brevet_id
        tmpl_vars = brevet_details(request)
        self.assertTrue(tmpl_vars['logout_btn'])
        self.assertEqual(str(tmpl_vars['brevet']), brevet_id)


class TestBrevetCreate(unittest.TestCase):
    """Unit tests for brevet object creation admin interface views.

       *TODO*: Add integration tests:

         * form renders expected controls with expected default values
         * POST with valid data adds record to database
         * POST with brevet that is already in db fails gracefully
    """
    def _get_target_class(self):
        from ..views.admin.brevet import BrevetCreate
        return BrevetCreate

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
        """list_url returns expected brevets list URL
        """
        self.config.add_route('admin.list', '/admin/{list}/')
        request = testing.DummyRequest()
        create = self._make_one(request)
        url = create.list_url()
        self.assertEqual(url, 'http://example.com/admin/brevets/')

    def test_show(self):
        """show returns expected template variables
        """
        self.config.add_route('admin.list', '/admin/{list}/')
        request = testing.DummyRequest()
        create = self._make_one(request)
        tmpl_vars = create.show(MagicMock(name='form'))
        self.assertTrue(tmpl_vars['logout_btn'])
        self.assertEqual(
            tmpl_vars['cancel_url'], 'http://example.com/admin/brevets/')

    def test_add_success(self):
        """admin create brevet success adds brevet to database
        """
        from ..models import Brevet
        self.config.add_route('admin.list', '/admin/{list}/')
        self.config.add_route('admin.brevets.view', '/admin/brevets/{item}')
        request = testing.DummyRequest()
        create = self._make_one(request)
        url = create.add_success({
            'region': 'LM',
            'distance': 200,
            'date_time': datetime(2012, 11, 11, 7, 0),
            'route_name': '11th Hour',
            'start_locn': 'Bean Around the World Coffee, Lonsdale Quay, '
                          '123 Carrie Cates Ct, North Vancouver',
            'organizer_email': 'tracy@example.com',
            })
        brevet = DBSession.query(Brevet).first()
        self.assertEqual(str(brevet), 'LM200 11Nov2012')
        self.assertEqual(
            url.location, 'http://example.com/admin/brevets/LM200%2011Nov2012')

    def test_failure(self):
        """create brevet failure returns expected template variables
        """
        self.config.add_route('admin.list', '/admin/{list}/')
        request = testing.DummyRequest()
        create = self._make_one(request)
        tmpl_vars = create.failure(MagicMock(name='ValidationError'))
        self.assertTrue(tmpl_vars['logout_btn'])
        self.assertEqual(
            tmpl_vars['cancel_url'], 'http://example.com/admin/brevets/')


class TestBrevetEdit(unittest.TestCase):
    """Unit tests for brevet object edit admin interface views.

       *TODO*: Add integration tests:

         * form renders populated controls
         * POST with valid data updates record in database
    """
    def _get_target_class(self):
        from ..views.admin.brevet import BrevetEdit
        return BrevetEdit

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
        """admin brevet edit appstruct returns dict to populate form
        """
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
            DBSession.add(brevet)
        request = testing.DummyRequest()
        request.matchdict['item'] = 'LM200 11Nov2012'
        edit = self._make_one(request)
        appstruct = edit.appstruct()
        self.assertEqual(
            appstruct, {
                'id': 1,
                'region': 'LM',
                'distance': 200,
                'date_time': datetime(2012, 11, 11, 7, 0),
                'route_name': '11th Hour',
                'start_locn': 'Bean Around the World Coffee, Lonsdale Quay, '
                              '123 Carrie Cates Ct, North Vancouver',
                'start_map_url': 'https://maps.google.com/maps?q='
                                 'Bean+Around+the+World+Coffee,+Lonsdale+Quay,'
                                 '+123+Carrie+Cates+Ct,+North+Vancouver',
                'organizer_email': 'tracy@example.com',
                'registration_end': datetime(2012, 11, 10, 12, 0),
            })

    def test_show(self):
        """admin brevet edit show returns expected template variables
        """
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
            DBSession.add(brevet)
        self.config.add_route('admin.brevets.view', '/admin/brevets/{item}')
        request = testing.DummyRequest()
        request.matchdict['item'] = 'LM200 11Nov2012'
        edit = self._make_one(request)
        tmpl_vars = edit.show(MagicMock(name='form'))
        self.assertTrue(tmpl_vars['logout_btn'])
        self.assertEqual(
            tmpl_vars['cancel_url'],
            'http://example.com/admin/brevets/LM200%2011Nov2012')

    def test_save_success(self):
        """admin edit brevet save success updates brevet in database
        """
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
            DBSession.add(brevet)
        self.config.add_route('admin.brevets.view', '/admin/brevets/{item}')
        request = testing.DummyRequest()
        request.matchdict['item'] = 'LM200 11Nov2012'
        edit = self._make_one(request)
        url = edit.save_success({
                'id': 1,
                'region': 'LM',
                'distance': 200,
                'date_time': datetime(2012, 11, 11, 7, 0),
                'route_name': '11th Hour',
                'start_locn': 'Bean Around the World Coffee, Lonsdale Quay, '
                              '123 Carrie Cates Ct, North Vancouver',
                'start_map_url': 'https://maps.google.com/maps?q='
                                 'Bean+Around+the+World+Coffee,+Lonsdale+Quay,'
                                 '+123+Carrie+Cates+Ct,+North+Vancouver',
                'organizer_email': 'tom@example.com',
                'registration_end': datetime(2012, 11, 10, 12, 0),
            })
        brevet = DBSession.query(Brevet).first()
        self.assertEqual(brevet.organizer_email, 'tom@example.com')
        self.assertEqual(
            url.location, 'http://example.com/admin/brevets/LM200%2011Nov2012')

    def test_failure(self):
        """edit brevet failure returns expected template variables
        """
        self.config.add_route('admin.brevets.view', '/admin/brevets/{item}')
        request = testing.DummyRequest()
        request.matchdict['item'] = 'LM200 11Nov2012'
        create = self._make_one(request)
        tmpl_vars = create.failure(MagicMock(name='ValidationError'))
        self.assertTrue(tmpl_vars['logout_btn'])
        self.assertEqual(
            tmpl_vars['cancel_url'],
            'http://example.com/admin/brevets/LM200%2011Nov2012')