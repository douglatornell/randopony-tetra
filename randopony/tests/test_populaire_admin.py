# -*- coding: utf-8 -*-
"""Tests for RandoPony populaire admin views and functionality.
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


class TestPopulaireDetails(unittest.TestCase):
    """Unit test for populaire details view.
    """
    def setUp(self):
        self.config = testing.setUp()
        engine = create_engine('sqlite://')
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_populaire_details(self):
        """populaire_details view has expected template vsriables
        """
        from .. import __pkg_metadata__ as version
        from ..models import Populaire
        from ..views.admin.populaire import populaire_details
        populaire = Populaire(
            event_name='Victoria Populaire',
            short_name='VicPop',
            distance='50 km, 100 km',
            date_time=datetime(2011, 3, 27, 10, 0),
            start_locn='University of Victoria, Parking Lot #2 '
                       'Gabriola Road, near McKinnon Gym)',
            organizer_email='mjansson@example.com',
            registration_end=datetime(2011, 3, 24, 12, 0),
            entry_form_url='http://www.randonneurs.bc.ca/VicPop/'
                           'VicPop11_registration.pdf',
        )
        DBSession.add(populaire)
        request = testing.DummyRequest()
        request.matchdict['item'] = str(populaire)
        tmpl_vars = populaire_details(request)
        self.assertEqual(
            tmpl_vars,
            {
                'version': version.number + version.release,
                'logout_btn': True,
                'populaire': populaire,
            })


class TestPopulaireCreate(unittest.TestCase):
    """Unit tests for populaire object creation admin interface views.

       *TODO*: Add integration tests:

         * form renders expected controls with expected default values
         * POST with valid data adds record to database
         * POST with populaire that is already in db fails gracefully
    """
    def _get_target_class(self):
        from ..views.admin.populaire import PopulaireCreate
        return PopulaireCreate

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
        """list_url returns expected populaires list URL
        """
        self.config.add_route('admin.list', '/admin/{list}/')
        request = testing.DummyRequest()
        create = self._make_one(request)
        url = create.list_url()
        self.assertEqual(url, 'http://example.com/admin/populaires/')

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
                'cancel_url': 'http://example.com/admin/populaires/',
            })

    def test_add_success(self):
        """admin create populaire success adds populaire to database
        """
        from ..models import Populaire
        self.config.add_route('admin.list', '/admin/{list}/')
        self.config.add_route('admin.populaires.view', '/admin/populaires/{item}')
        request = testing.DummyRequest()
        create = self._make_one(request)
        url = create.add_success({
            'event_name': 'Victoria Populaire',
            'short_name': 'VicPop',
            'distance': '50 km, 100 km',
            'date_time': datetime(2011, 3, 27, 10, 0),
            'start_locn': 'University of Victoria, Parking Lot #2 '
                          '(Gabriola Road, near McKinnon Gym)',
            'organizer_email': 'mjansson@example.com',
            'registration_end': datetime(2011, 3, 24, 12, 0),
            'entry_form_url': 'http://www.randonneurs.bc.ca/VicPop/'
                              'VicPop11_registration.pdf',
        })
        populaire = DBSession.query(Populaire).first()
        self.assertEqual(str(populaire), 'VicPop')
        self.assertEqual(
            url.location, 'http://example.com/admin/populaires/VicPop')

    def test_failure(self):
        """create populaire failure returns expected template variables
        """
        from .. import __pkg_metadata__ as version
        self.config.add_route('admin.list', '/admin/{list}/')
        request = testing.DummyRequest()
        create = self._make_one(request)
        mock_val_error = MagicMock(name='ValidationError')
        tmpl_vars = create.failure(mock_val_error)
        self.assertEqual(
            tmpl_vars,
            {
                'version': version.number + version.release,
                'logout_btn': True,
                'form': mock_val_error.render(),
                'cancel_url': 'http://example.com/admin/populaires/',
            })


class TestPopulaireEdit(unittest.TestCase):
    """Unit tests for populaire object edit admin interface views.

       *TODO*: Add integration tests:

         * form renders populated controls
         * POST with valid data updates record in database
    """
    def _get_target_class(self):
        from ..views.admin.populaire import PopulaireEdit
        return PopulaireEdit

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
        """admin populaire edit appstruct returns dict to populate form
        """
        from ..models import Populaire
        populaire = Populaire(
            event_name='Victoria Populaire',
            short_name='VicPop',
            distance='50 km, 100 km',
            date_time=datetime(2011, 3, 27, 10, 0),
            start_locn='University of Victoria, Parking Lot #2 '
                       '(Gabriola Road, near McKinnon Gym)',
            organizer_email='mjansson@example.com',
            registration_end=datetime(2011, 3, 24, 12, 0),
            entry_form_url='http://www.randonneurs.bc.ca/VicPop/'
                           'VicPop11_registration.pdf',
        )
        DBSession.add(populaire)
        self.config.add_route(
            'admin.populaires.view', '/admin/populaires/{item}')
        request = testing.DummyRequest()
        request.matchdict['item'] = 'VicPop'
        edit = self._make_one(request)
        appstruct = edit.appstruct()
        self.maxDiff = None
        self.assertEqual(
            appstruct, {
                'id': 1,
                'event_name': 'Victoria Populaire',
                'short_name': 'VicPop',
                'distance': '50 km, 100 km',
                'date_time': datetime(2011, 3, 27, 10, 0),
                'start_locn': 'University of Victoria, Parking Lot #2 '
                              '(Gabriola Road, near McKinnon Gym)',
                'start_map_url': 'https://maps.google.com/maps?q='
                                 'University+of+Victoria,+Parking+Lot+#2'
                                 '+(Gabriola+Road,+near+McKinnon+Gym)',
                'organizer_email': 'mjansson@example.com',
                'registration_end': datetime(2011, 3, 24, 12, 0),
                'entry_form_url': 'http://www.randonneurs.bc.ca/VicPop/'
                                  'VicPop11_registration.pdf',
            })

    def test_show(self):
        """admin populaire edit show returns expected template variables
        """
        from .. import __pkg_metadata__ as version
        from ..models import Populaire
        populaire = Populaire(
            event_name='Victoria Populaire',
            short_name='VicPop',
            distance='50 km, 100 km',
            date_time=datetime(2011, 3, 27, 10, 0),
            start_locn='University of Victoria, Parking Lot #2 '
                       '(Gabriola Road, near McKinnon Gym)',
            organizer_email='mjansson@example.com',
            registration_end=datetime(2011, 3, 24, 12, 0),
            entry_form_url='http://www.randonneurs.bc.ca/VicPop/'
                           'VicPop11_registration.pdf',
        )
        DBSession.add(populaire)
        self.config.add_route(
            'admin.populaires.view', '/admin/populaires/{item}')
        request = testing.DummyRequest()
        request.matchdict['item'] = 'VicPop'
        edit = self._make_one(request)
        mock_form = MagicMock(name='form')
        tmpl_vars = edit.show(mock_form)
        self.assertEqual(
            tmpl_vars,
            {
                'version': version.number + version.release,
                'logout_btn': True,
                'form': mock_form.render(),
                'cancel_url': 'http://example.com/admin/populaires/VicPop',
            })

    def test_save_success(self):
        """admin edit populaire save success updates populaire in database
        """
        from ..models import Populaire
        populaire = Populaire(
            event_name='Victoria Populaire',
            short_name='VicPop',
            distance='50 km, 100 km',
            date_time=datetime(2011, 3, 27, 10, 0),
            start_locn='University of Victoria, Parking Lot #2 '
                       '(Gabriola Road, near McKinnon Gym)',
            organizer_email='mjansson@example.com',
            registration_end=datetime(2011, 3, 24, 12, 0),
            entry_form_url='http://www.randonneurs.bc.ca/VicPop/'
                           'VicPop11_registration.pdf',
        )
        DBSession.add(populaire)
        self.config.add_route(
            'admin.populaires.view', '/admin/populaires/{item}')
        request = testing.DummyRequest()
        request.matchdict['item'] = 'VicPop'
        edit = self._make_one(request)
        url = edit.save_success({
            'id': 1,
            'event_name': 'Victoria Populaire',
            'short_name': 'VicPop',
            'distance': '50 km, 100 km',
            'date_time': datetime(2011, 3, 27, 10, 0),
            'start_locn': 'University of Victoria, Parking Lot #2 '
                          '(Gabriola Road, near McKinnon Gym)',
            'start_map_url': 'https://maps.google.com/maps?q='
                             'University+of+Victoria,+Parking+Lot+#2'
                             '+(Gabriola+Road,+near+McKinnon+Gym)',
            'organizer_email': 'tom@example.com',
            'registration_end': datetime(2011, 3, 24, 12, 0),
            'entry_form_url': 'http://www.randonneurs.bc.ca/VicPop/'
                              'VicPop11_registration.pdf',
        })
        populaire = DBSession.query(Populaire).first()
        self.assertEqual(populaire.organizer_email, 'tom@example.com')
        self.assertEqual(
            url.location, 'http://example.com/admin/populaires/VicPop')

    def test_failure(self):
        """edit populaire failure returns expected template variables
        """
        from .. import __pkg_metadata__ as version
        self.config.add_route(
            'admin.populaires.view', '/admin/populaires/{item}')
        request = testing.DummyRequest()
        request.matchdict['item'] = 'VicPop'
        create = self._make_one(request)
        mock_val_error = MagicMock(name='ValidationError')
        tmpl_vars = create.failure(mock_val_error)
        self.assertEqual(
            tmpl_vars,
            {
                'version': version.number + version.release,
                'logout_btn': True,
                'form': mock_val_error.render(),
                'cancel_url': 'http://example.com/admin/populaires/VicPop',
            })


class TestSetup123(unittest.TestCase):
    """Unit tests for combined 3-step setup admin function view.
    """
    def _call_setup_123(self, *args, **kwargs):
        from ..views.admin.populaire import setup_123
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
            'admin.populaires.view', '/admin/populaire/{item}')
        self.config.add_route(
            'populaire', '/populaires/{short_name}')
        self.config.add_route(
            'populaire.rider_emails',
            '/populaires/{short_name}/rider_emails/{uuid}')
        engine = create_engine('sqlite://')
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_setup_123(self):
        """setup_123 calls expected 3 setup steps
        """
        from ..models import Populaire
        from ..views.admin import populaire as pop_module
        populaire = Populaire(
            event_name='Victoria Populaire',
            short_name='VicPop',
            distance='50 km, 100 km',
            date_time=datetime(2011, 3, 27, 10, 0),
            start_locn='University of Victoria, Parking Lot #2 '
                       '(Gabriola Road, near McKinnon Gym)',
            organizer_email='mjansson@example.com',
            registration_end=datetime(2011, 3, 24, 12, 0),
            entry_form_url='http://www.randonneurs.bc.ca/VicPop/'
                           'VicPop11_registration.pdf',
        )
        DBSession.add(populaire)
        request = testing.DummyRequest()
        request.matchdict['item'] = 'VicPop'
        patch_crl = patch.object(pop_module, '_create_rider_list')
        patch_eto = patch.object(pop_module, '_email_to_organizer')
        patch_etw = patch.object(pop_module, '_email_to_webmaster')
        with patch_crl as mock_crl, patch_eto as mock_eto, patch_etw as mock_etw:
            mock_crl.return_value = 'success'
            resp = self._call_setup_123(request)
        mock_crl.assert_called_once_with(request, populaire)
        mock_eto.assert_called_once_with(request, populaire)
        mock_etw.assert_called_once_with(request, populaire)
        self.assertEqual(
            resp.location, 'http://example.com/admin/populaire/VicPop')

    def test_setup_123_error_create_rider_list_already_done(self):
        """setup_123 stops w/ exp flash msg if rider list doc id is setup
        """
        from ..models import Populaire
        from ..views.admin import populaire as pop_module
        populaire = Populaire(
            event_name='Victoria Populaire',
            short_name='VicPop',
            distance='50 km, 100 km',
            date_time=datetime(2011, 3, 27, 10, 0),
            start_locn='University of Victoria, Parking Lot #2 '
                       '(Gabriola Road, near McKinnon Gym)',
            organizer_email='mjansson@example.com',
            registration_end=datetime(2011, 3, 24, 12, 0),
            entry_form_url='http://www.randonneurs.bc.ca/VicPop/'
                           'VicPop11_registration.pdf',
            google_doc_id='spreadsheet:1234',
        )
        DBSession.add(populaire)
        request = testing.DummyRequest()
        request.matchdict['item'] = 'VicPop'
        patch_eto = patch.object(pop_module, '_email_to_organizer')
        patch_etw = patch.object(pop_module, '_email_to_webmaster')
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
            Populaire,
        )
        from ..views.admin import populaire as pop_module
        populaire = Populaire(
            event_name='Victoria Populaire',
            short_name='VicPop',
            distance='50 km, 100 km',
            date_time=datetime(2011, 3, 27, 10, 0),
            start_locn='University of Victoria, Parking Lot #2 '
                       '(Gabriola Road, near McKinnon Gym)',
            organizer_email='mjansson@example.com',
            registration_end=datetime(2011, 3, 24, 12, 0),
            entry_form_url='http://www.randonneurs.bc.ca/VicPop/'
                           'VicPop11_registration.pdf',
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
            (populaire, from_randopony, admin_email, club_webmaster))
        request = testing.DummyRequest()
        request.matchdict['item'] = 'VicPop'
        crl_patch = patch.object(pop_module, '_create_rider_list')
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
                'Email sent to VicPop organizer(s)',
                'Email with VicPop page URL sent to webmaster',
            ])
