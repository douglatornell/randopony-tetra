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
from pyramid_mailer import get_mailer
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
        self.assertTrue(tmpl_vars['logout_btn'])
        self.assertEqual(tmpl_vars['populaire'], populaire)


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
        self.config.add_route('admin.list', '/admin/{list}/')
        request = testing.DummyRequest()
        create = self._make_one(request)
        tmpl_vars = create.show(MagicMock(name='form'))
        self.assertTrue(tmpl_vars['logout_btn'])
        self.assertEqual(
            tmpl_vars['cancel_url'], 'http://example.com/admin/populaires/')

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
        self.config.add_route('admin.list', '/admin/{list}/')
        request = testing.DummyRequest()
        create = self._make_one(request)
        tmpl_vars = create.failure(MagicMock(name='ValidationError'))
        self.assertTrue(tmpl_vars['logout_btn'])
        self.assertEqual(
            tmpl_vars['cancel_url'], 'http://example.com/admin/populaires/')


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
        tmpl_vars = edit.show(MagicMock(name='form'))
        self.assertTrue(tmpl_vars['logout_btn'])
        self.assertEqual(
            tmpl_vars['cancel_url'],
            'http://example.com/admin/populaires/VicPop')

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
        self.config.add_route(
            'admin.populaires.view', '/admin/populaires/{item}')
        request = testing.DummyRequest()
        request.matchdict['item'] = 'VicPop'
        create = self._make_one(request)
        tmpl_vars = create.failure(MagicMock(name='ValidationError'))
        self.assertTrue(tmpl_vars['logout_btn'])
        self.assertEqual(
            tmpl_vars['cancel_url'],
            'http://example.com/admin/populaires/VicPop')


class TestCreateRiderList(unittest.TestCase):
    """Unit tests for create rider list spreadsheet view.
    """
    def _call_fut(self, *args, **kwargs):
        from ..views.admin.populaire import create_rider_list
        return create_rider_list(*args, **kwargs)

    def setUp(self):
        self.config = testing.setUp(
            settings={
                'google_drive.username': 'randopony',
                'google_drive.password': 'sEcReT',
            })
        self.config.add_route(
            'admin.populaires.view', '/admin/populaire/{item}')
        engine = create_engine('sqlite://')
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_create_rider_list_already_done(self):
        """create_rider_list sets expected flash msgs when rider list exists
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
            google_doc_id='spreadsheet:1234',
            )
        DBSession.add(populaire)
        request = testing.DummyRequest()
        request.matchdict['item'] = 'VicPop'
        resp = self._call_fut(request)
        flash = request.session.pop_flash()
        self.assertEqual(
            flash,
            ['error', 'Rider list spreadsheet already created'])
        self.assertEqual(
            resp.location, 'http://example.com/admin/populaire/VicPop')

    def test_create_rider_list_calls_create_google_drive_list(self):
        """create_rider_list calls _create_google_drive_list w/ expected args
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
        cgdl_patch = patch.object(pop_module, '_create_google_drive_list')
        with cgdl_patch as mock_cgdl:
            self._call_fut(request)
        mock_cgdl.assert_called_once_with(populaire, request)

    def test_create_rider_list_sets_google_doc_id(self):
        """create_rider_list sets google_doc_id attr on populaire instance
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
        cgdl_patch = patch.object(pop_module, '_create_google_drive_list')
        with cgdl_patch as mock_cgdl:
            mock_cgdl.return_value = 'spreadsheet:1234'
            self._call_fut(request)
        self.assertEqual(populaire.google_doc_id, 'spreadsheet:1234')

    def test_create_rider_list_rider_list_created(self):
        """create_rider_list sets exp flash msgs when rider list create_rider_list"""
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
        cgdl_patch = patch.object(pop_module, '_create_google_drive_list')
        with cgdl_patch as mock_cgdl:
            mock_cgdl.return_value = 'spreadsheet:1234'
            resp = self._call_fut(request)
        flash = request.session.pop_flash()
        self.assertEqual(
            flash,
            ['success', 'Rider list spreadsheet created'])
        self.assertEqual(
            resp.location, 'http://example.com/admin/populaire/VicPop')


class TestEmailToOrganizer(unittest.TestCase):
    """Unit tests for email to organizer view.
    """
    def _call_fut(self, *args, **kwargs):
        from ..views.admin.populaire import email_to_organizer
        return email_to_organizer(*args, **kwargs)

    def setUp(self):
        from ..models import EmailAddress
        self.config = testing.setUp(
            settings={
                'mako.directories': 'randopony:templates',
            })
        self.config.include('pyramid_mailer.testing')
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
        from_randopony = EmailAddress(
            key='from_randopony',
            email='randopony@randonneurs.bc.ca',
            )
        admin_email = EmailAddress(
            key='admin_email',
            email='djl@douglatornell.ca',
            )
        DBSession.add_all((from_randopony, admin_email))

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_email_to_organizer_no_google_doc_id(self):
        """email_to_organizer fails w/ exp flash msg if google_doc_id not set
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
        request = testing.DummyRequest()
        request.matchdict['item'] = 'VicPop'
        mailer = get_mailer(request)
        resp = self._call_fut(request)
        self.assertEqual(len(mailer.outbox), 0)
        flash = request.session.pop_flash()
        self.assertEqual(
            flash,
            ['error',
            'Google Drive rider list must be created before email to '
            'organizer(s) can be sent'])
        self.assertEqual(
            resp.location, 'http://example.com/admin/populaire/VicPop')

    def test_email_to_organizer_sends_email(self):
        """email to organizer send email message & sets expected flash message
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
            google_doc_id='spreadsheet:'
                '0AtBTJntkFrPQdFJDN3lvRmVOQW5RXzRZbzRTRFJLYnc',
            )
        DBSession.add(populaire)
        request = testing.DummyRequest()
        request.matchdict['item'] = 'VicPop'
        mailer = get_mailer(request)
        resp = self._call_fut(request)
        self.assertEqual(len(mailer.outbox), 1)
        flash = request.session.pop_flash()
        self.assertEqual(
            flash,
            ['success', 'Email sent to VicPop organizer(s)'])
        self.assertEqual(
            resp.location, 'http://example.com/admin/populaire/VicPop')

    def test_email_to_organizer_message(self):
        """email to organizer has expected content
        """
        from ..models import (
            EmailAddress,
            Populaire,
            )
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
            google_doc_id='spreadsheet:'
                '0AtBTJntkFrPQdFJDN3lvRmVOQW5RXzRZbzRTRFJLYnc',
            )
        DBSession.add(populaire)
        request = testing.DummyRequest()
        request.matchdict['item'] = 'VicPop'
        mailer = get_mailer(request)
        self._call_fut(request)
        msg = mailer.outbox[0]
        self.assertEqual(msg.subject, 'RandoPony URLs for Victoria Populaire')
        from_randopony = (
            DBSession.query(EmailAddress)
            .filter_by(key='from_randopony').first().email)
        self.assertEqual(msg.sender, from_randopony)
        self.assertEqual(msg.recipients, ['mjansson@example.com'])
        self.assertIn(
            'The URL is <http://example.com/populaires/VicPop>.', msg.body)
        self.assertIn(
            'rider list URL is <https://spreadsheets.google.com/ccc?key='
            '0AtBTJntkFrPQdFJDN3lvRmVOQW5RXzRZbzRTRFJLYnc>.',
            msg.body)
        self.assertIn(
            'email address list URL is <http://example.com/populaires/VicPop/'
            'rider_emails/f279f382-57e7-5658-8de2-f4aebcdb0b3d>.',
            msg.body)
        self.assertIn('send email to <djl@douglatornell.ca>.', msg.body)

    def test_email_to_organizer_multi_organizer(self):
        """email to organizer has expected to list for multi-organizer event
        """
        from ..models import Populaire
        populaire = Populaire(
            event_name='Victoria Populaire',
            short_name='VicPop',
            distance='50 km, 100 km',
            date_time=datetime(2011, 3, 27, 10, 0),
            start_locn='University of Victoria, Parking Lot #2 '
                       '(Gabriola Road, near McKinnon Gym)',
            organizer_email='mjansson@example.com, mcroy@example.com',
            registration_end=datetime(2011, 3, 24, 12, 0),
            entry_form_url='http://www.randonneurs.bc.ca/VicPop/'
                           'VicPop11_registration.pdf',
            google_doc_id='spreadsheet:'
                '0AtBTJntkFrPQdFJDN3lvRmVOQW5RXzRZbzRTRFJLYnc',
            )
        DBSession.add(populaire)
        request = testing.DummyRequest()
        request.matchdict['item'] = 'VicPop'
        mailer = get_mailer(request)
        self._call_fut(request)
        msg = mailer.outbox[0]
        self.assertEqual(
            msg.recipients, ['mjansson@example.com', 'mcroy@example.com'])
