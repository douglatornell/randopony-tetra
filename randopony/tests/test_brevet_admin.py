# -*- coding: utf-8 -*-
"""Tests for RandoPony brevet admin views and functionality.
"""
from datetime import datetime
import unittest
try:
    from unittest.mock import (
        MagicMock,
        patch,
    )
except ImportError:                      # pragma: no cover
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
        from .. import __pkg_metadata__ as version
        from ..models import Brevet
        from ..views.admin.brevet import brevet_details
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
        request.matchdict['item'] = str(brevet)
        tmpl_vars = brevet_details(request)
        self.assertEqual(
            tmpl_vars,
            {
                'version': version.number + version.release,
                'logout_btn': True,
                'brevet': brevet,
            })


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
                'logout_btn': True,
                'form': mock_form.render(),
                'cancel_url': 'http://example.com/admin/brevets/'
            })

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
                'logout_btn': True,
                'form': mock_val_err.render(),
                'cancel_url': 'http://example.com/admin/brevets/'
            })


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
        from .. import __pkg_metadata__ as version
        from ..models import Brevet
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
        mock_form = MagicMock(name='form')
        tmpl_vars = edit.show(mock_form)
        self.assertEqual(
            tmpl_vars,
            {
                'version': version.number + version.release,
                'logout_btn': True,
                'form': mock_form.render(),
                'cancel_url':
                    'http://example.com/admin/brevets/LM200%2011Nov2012'
            })

    def test_save_success(self):
        """admin edit brevet save success updates brevet in database
        """
        from ..models import Brevet
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
        from .. import __pkg_metadata__ as version
        self.config.add_route('admin.brevets.view', '/admin/brevets/{item}')
        request = testing.DummyRequest()
        request.matchdict['item'] = 'LM200 11Nov2012'
        edit = self._make_one(request)
        mock_val_err = MagicMock(name='ValidationError')
        tmpl_vars = edit.failure(mock_val_err)
        self.assertEqual(
            tmpl_vars,
            {
                'version': version.number + version.release,
                'logout_btn': True,
                'form': mock_val_err.render(),
                'cancel_url':
                    'http://example.com/admin/brevets/LM200%2011Nov2012'
            })


class TestCreateRiderList(unittest.TestCase):
    """Unit tests for _create_rider_list.
    """
    def _call_create_rider_list(self, *args, **kwargs):
        from ..views.admin.brevet import _create_rider_list
        return _create_rider_list(*args, **kwargs)

    def setUp(self):
        self.config = testing.setUp(
            settings={
                'google_drive.username': 'randopony',
                'google_drive.password': 'sEcReT',
            })
        engine = create_engine('sqlite://')
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_create_rider_list_already_exists(self):
        """_create_rider_list returns expected flash when rider list exists
        """
        from ..models import Brevet
        from ..views.admin.brevet import google_drive
        brevet = Brevet(
            region='VI',
            distance=200,
            date_time=datetime(2013, 3, 3, 7, 0),
            route_name='Chilly 200',
            start_locn='Chez Croy, 3131 Millgrove St, Victoria',
            organizer_email='mcroy@example.com',
            registration_end=datetime(2013, 3, 2, 12, 0),
            google_doc_id='spreadsheet:1234',
        )
        DBSession.add(brevet)
        request = testing.DummyRequest()
        patch_crl = patch.object(google_drive, 'create_rider_list')
        with patch_crl as mock_crl:
            mock_crl.return_value = [
                'error',
                'Rider list spreadsheet already created',
            ]
            flash = self._call_create_rider_list(request, brevet)
        self.assertEqual(
            flash, [
                'error', 'Rider list spreadsheet already created',
            ])

    def test_create_rider_list_success(self):
        """rider list spreadsheet updated w/ info question upon create success
        """
        from ..models import Brevet
        from ..views.admin.brevet import google_drive
        brevet = Brevet(
            region='VI',
            distance=200,
            date_time=datetime(2013, 3, 3, 7, 0),
            route_name='Chilly 200',
            start_locn='Chez Croy, 3131 Millgrove St, Victoria',
            organizer_email='mcroy@example.com',
            registration_end=datetime(2013, 3, 2, 12, 0),
            google_doc_id='spreadsheet:1234',
        )
        DBSession.add(brevet)
        request = testing.DummyRequest()
        patch_crl = patch.object(google_drive, 'create_rider_list')
        patch_urliq = patch.object(
            google_drive, 'update_rider_list_info_question')
        with patch_crl as mock_crl, patch_urliq as mock_urliq:
            mock_crl.return_value = [
                'success', 'Rider list spreadsheet created',
            ]
            mock_urliq.return_value = [
                'success', 'Rider list info question column updated',
            ]
            flash = self._call_create_rider_list(request, brevet)
        self.assertEqual(
            flash, [
                'success',
                'Rider list spreadsheet created',
                'success',
                'Rider list info question column updated',
            ])


class TestSetup123(unittest.TestCase):
    """Unit tests for combined 3-step setup admin function view.
    """
    def _call_setup_123(self, *args, **kwargs):
        from ..views.admin.brevet import setup_123
        return setup_123(*args, **kwargs)

    def setUp(self):
        self.config = testing.setUp(
            settings={
                'google_drive.username': 'randopony',
                'google_drive.password': 'sEcReT',
                'mako.directories': 'randopony:templates',
            })
        self.config.include('pyramid_mailer.testing')
        self.config.include('pyramid_mako')
        self.config.add_route(
            'admin.brevets.view', '/admin/brevets/{item}')
        self.config.add_route(
            'brevet', '/brevets/{region}/{distance}/{date}')
        self.config.add_route(
            'brevet.rider_emails',
            '/brevets/{region}/{distance}/{date}/rider_emails/{uuid}')
        engine = create_engine('sqlite://')
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_setup_123(self):
        """setup_123 calls expected 3 setup steps
        """
        from ..models import Brevet
        from ..views.admin import brevet as brevet_module
        brevet = Brevet(
            region='VI',
            distance=200,
            date_time=datetime(2013, 3, 3, 7, 0),
            route_name='Chilly 200',
            start_locn='Chez Croy, 3131 Millgrove St, Victoria',
            organizer_email='mcroy@example.com',
            registration_end=datetime(2013, 3, 2, 12, 0),
            google_doc_id='spreadsheet:1234',
        )
        DBSession.add(brevet)
        request = testing.DummyRequest()
        request.matchdict['item'] = 'VI200 03Mar2013'
        date = '03Mar2013'
        patch_crl = patch.object(brevet_module, '_create_rider_list')
        patch_eto = patch.object(brevet_module, '_email_to_organizer')
        patch_etw = patch.object(brevet_module, '_email_to_webmaster')
        with patch_crl as mock_crl, patch_eto as mock_eto, patch_etw as mock_etw:
            mock_crl.return_value = 'success'
            resp = self._call_setup_123(request)
        mock_crl.assert_called_once_with(request, brevet)
        mock_eto.assert_called_once_with(request, brevet, date)
        mock_etw.assert_called_once_with(request, brevet, date)
        self.assertEqual(
            resp.location, 'http://example.com/admin/brevets/VI200%2003Mar2013')

    def test_setup_123_error_create_rider_list_already_done(self):
        """setup_123 stops w/ exp flash msg if rider list doc id is setup
        """
        from ..models import Brevet
        from ..views.admin import brevet as brevet_module
        brevet = Brevet(
            region='VI',
            distance=200,
            date_time=datetime(2013, 3, 3, 7, 0),
            route_name='Chilly 200',
            start_locn='Chez Croy, 3131 Millgrove St, Victoria',
            organizer_email='mcroy@example.com',
            registration_end=datetime(2013, 3, 2, 12, 0),
            google_doc_id='spreadsheet:1234',
        )
        DBSession.add(brevet)
        request = testing.DummyRequest()
        request.matchdict['item'] = 'VI200 03Mar2013'
        patch_eto = patch.object(brevet_module, '_email_to_organizer')
        patch_etw = patch.object(brevet_module, '_email_to_webmaster')
        with patch_eto as mock_eto, patch_etw as mock_etw:
            self._call_setup_123(request)
        self.assertFalse(mock_eto.called)
        self.assertFalse(mock_etw.called)
        flash = request.session.pop_flash()
        self.assertEqual(
            flash,
            ['error', 'Rider list spreadsheet already created'])

    def test_setup_123_success_flash(self):
        """setup_123 sets expected flash message on success
        """
        from ..models import (
            EmailAddress,
            Brevet,
        )
        from ..views.admin import brevet as brevet_module
        brevet = Brevet(
            region='VI',
            distance=200,
            date_time=datetime(2013, 3, 3, 7, 0),
            route_name='Chilly 200',
            start_locn='Chez Croy, 3131 Millgrove St, Victoria',
            organizer_email='mcroy@example.com',
            registration_end=datetime(2013, 3, 2, 12, 0),
            google_doc_id='spreadsheet:1234',
        )
        from_randopony = EmailAddress(
            key='from_randopony',
            email='randopony@randonneurs.bc.ca',
        )
        admin_email = EmailAddress(
            key='admin_email',
            email='djl@douglatornell.ca',
        )
        club_webmaster = EmailAddress(
            key='club_webmaster',
            email='webmaster@randonneurs.bc.ca',
        )
        DBSession.add_all(
            (brevet, from_randopony, admin_email, club_webmaster))
        request = testing.DummyRequest()
        request.matchdict['item'] = 'VI200 03Mar2013'
        crl_patch = patch.object(brevet_module, '_create_rider_list')
        with crl_patch as mock_crl:
            mock_crl.return_value = [
                'success', 'Rider list spreadsheet created']
            self._call_setup_123(request)
        flash = request.session.pop_flash()
        self.assertEqual(
            flash,
            [
                'success',
                'Rider list spreadsheet created',
                'Email sent to VI200 03Mar2013 organizer(s)',
                'Email with VI200 03Mar2013 page URL sent to webmaster',
            ])
