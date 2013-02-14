# -*- coding: utf-8 -*-
"""Tests for RandoPony public site populaire views and functionality.
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
from pyramid_mailer import get_mailer
from sqlalchemy import create_engine
from ..models.meta import (
    Base,
    DBSession,
    )


class TestPopulaireViews(unittest.TestCase):
    """Unit tests for public site populaire views.

    *TODO*: Add integrations tests:

      * Registration closed & no register button rendered after registration_end
      * Past event template is rendered for events more than 7 days in the past
    """
    def _get_target_class(self):
        from ..views.site.populaire import PopulaireViews
        return PopulaireViews

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

    def test_populaire_list(self):
        """populaire_list view has expected tmpl_vars
        """
        from ..models import EmailAddress
        self.config.registry.settings['timezone'] = 'Canada/Pacific'
        email = EmailAddress(key='admin_email', email='tom@example.com')
        DBSession.add(email)
        request = testing.DummyRequest()
        views = self._make_one(request)
        tmpl_vars = views.populaire_list()
        self.assertEqual(tmpl_vars['active_tab'], 'populaires')
        self.assertEqual(tmpl_vars['admin_email'], 'tom@example.com')

    def test_populaire_page_registration_open(self):
        """populaire_page view has expected tmpl_vars when registration is open
        """
        from ..models import Populaire
        from ..views.site import populaire as pop_module
        self.config.registry.settings['timezone'] = 'Canada/Pacific'
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
        request.matchdict['short_name'] = 'VicPop'
        views = self._make_one(request)
        with patch.object(pop_module, 'datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = datetime(2011, 3, 22, 23, 18)
            mock_datetime.today.return_value = datetime(2011, 3, 22, 23, 18)
            tmpl_vars = views.populaire_page()
        self.assertEqual(tmpl_vars['active_tab'], 'populaires')
        self.assertEqual(tmpl_vars['populaire'], populaire)
        self.assertFalse(tmpl_vars['registration_closed'])

    def test_populaire_page_registration_closed(self):
        """populaire_page view has expected tmpl_vars when registration closed
        """
        from ..models import Populaire
        from ..views.site import populaire as pop_module
        self.config.registry.settings['timezone'] = 'Canada/Pacific'
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
        request.matchdict['short_name'] = 'VicPop'
        views = self._make_one(request)
        with patch.object(pop_module, 'datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = datetime(2011, 3, 25, 23, 24)
            mock_datetime.today.return_value = datetime(2011, 3, 25, 23, 24)
            tmpl_vars = views.populaire_page()
        self.assertTrue(tmpl_vars['registration_closed'])

    def test_populaire_page_event_started(self):
        """populaire_page view has expected tmpl_vars when event has started
        """
        from ..models import Populaire
        from ..views.site import populaire as pop_module
        self.config.registry.settings['timezone'] = 'Canada/Pacific'
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
        request.matchdict['short_name'] = 'VicPop'
        views = self._make_one(request)
        with patch.object(pop_module, 'datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = datetime(2011, 3, 27, 17, 1)
            mock_datetime.today.return_value = datetime(2011, 3, 27, 17, 1)
            tmpl_vars = views.populaire_page()
        self.assertTrue(tmpl_vars['event_started'])

    def test_populaire_page_event_not_started(self):
        """populaire_page view has exp tmpl_vars when event has yet to start
        """
        from ..models import Populaire
        from ..views.site import populaire as pop_module
        self.config.registry.settings['timezone'] = 'Canada/Pacific'
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
        request.matchdict['short_name'] = 'VicPop'
        views = self._make_one(request)
        with patch.object(pop_module, 'datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = datetime(2011, 3, 27, 16, 59)
            mock_datetime.today.return_value = datetime(2011, 3, 27, 16, 59)
            tmpl_vars = views.populaire_page()
        self.assertFalse(tmpl_vars['event_started'])

    def test_populaire_page_past_event(self):
        """populaire_page view calls _moved_on_page for event >7 days ago
        """
        from ..models import (
            Link,
            Populaire,
            )
        from ..views.site import populaire as pop_module
        self.config.registry.settings['timezone'] = 'Canada/Pacific'
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
        results_link = Link(
            key='results_link',
            url='http://randonneurs.bc.ca/results/{year}_times/{year}_times.html',
            )
        DBSession.add_all((populaire, results_link))
        request = testing.DummyRequest()
        request.matchdict['short_name'] = 'VicPop'
        views = self._make_one(request)
        views._moved_on_page = MagicMock('_moved_on', return_value='moved-on body')
        with patch.object(pop_module, 'datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2011, 4, 7, 15, 52)
            resp = views.populaire_page()
        self.assertEqual(resp.body, b'moved-on body')

    def test_populaire_moved_on_page(self):
        """_moved_on_page calls render with expected args
        """
        from ..models import (
            Link,
            Populaire,
            )
        from ..views.site import populaire as pop_module
        self.config.registry.settings['timezone'] = 'Canada/Pacific'
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
        results_link = Link(
            key='results_link',
            url='http://randonneurs.bc.ca/results/{year}_times/{year}_times.html',
            )
        DBSession.add_all((populaire, results_link))
        request = testing.DummyRequest()
        request.matchdict['short_name'] = 'VicPop'
        views = self._make_one(request)
        render_patch = patch.object(pop_module, 'render')
        with render_patch as mock_render:
            views._moved_on_page()
        tmpl_name = mock_render.call_args[0][0]
        tmpl_vars = mock_render.call_args[0][1]
        kwargs = mock_render.call_args[1]
        self.assertEqual(tmpl_name, 'moved-on.mako')
        self.assertIn('brevets', tmpl_vars)
        self.assertIn('populaires', tmpl_vars)
        self.assertEqual(tmpl_vars['active_tab'], 'populaires')
        self.assertEqual(tmpl_vars['event'], 'VicPop 27-Mar-2011')
        self.assertEqual(
            tmpl_vars['results_link'],
            'http://randonneurs.bc.ca/results/11_times/11_times.html')
        self.assertEqual(kwargs['request'], request)


class TestPopulaireEntry(unittest.TestCase):
    """Unit tests for populaire pre-registration form handler & views.

    *TODO*: Add integrations tests:

      * Distance radio buttons only rendered for multi-distance events
      * Valid pre-registration renders confirmation message
      * Duplicate pre-registration renders error message
    """
    def _get_target_class(self):
        from ..views.site.populaire import PopulaireEntry
        return PopulaireEntry

    def _make_one(self, *args, **kwargs):
        return self._get_target_class()(*args, **kwargs)

    def setUp(self):
        from ..models import EmailAddress
        self.config = testing.setUp(
            settings={
                'mako.directories': 'randopony:templates',
                'google_drive.username': 'randopony',
                'google_drive.password': 'sEcReT',
            })
        self.config.include('pyramid_mailer.testing')
        self.config.add_route('populaire', '/populaires/{short_name}')
        self.config.add_route(
            'populaire.rider_emails',
            '/populaire/{short_name}/rider_emails/{uuid}')
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

    def test_redirect_url(self):
        """_redirect_url returns expected populaire page URL
        """
        request = testing.DummyRequest()
        entry = self._make_one(request)
        url = entry._redirect_url('VicPop')
        self.assertEqual(url, 'http://example.com/populaires/VicPop')

    def test_get_bind_data(self):
        """get_bind_data returns expected data dict for multi-distance event
        """
        from ..models import Populaire
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
        request.matchdict['short_name'] = 'VicPop'
        entry = self._make_one(request)
        data = entry.get_bind_data()
        self.assertEqual(data['distances'], [(50, '50 km'), (100, '100 km')])
        self.assertTrue(data['include_distance'])

    def test_get_bind_data_exclude_distance(self):
        """get_bind_data returns expected data dict for single distance event
        """
        from ..models import Populaire
        populaire = Populaire(
            event_name="New Year's Populaire",
            short_name='NewYearsPop',
            distance='60 km',
            date_time=datetime(2013, 1, 1, 10, 0),
            start_locn='Kelseys Family Restaurant, 325 Burnside Rd W, Victoria',
            organizer_email='mcroy@example.com',
            registration_end=datetime(2012, 12, 31, 17, 0),
            entry_form_url='http://www.randonneurs.bc.ca/organize/eventform.pdf',
            )
        DBSession.add(populaire)
        request = testing.DummyRequest()
        request.matchdict['short_name'] = 'NewYearsPop'
        entry = self._make_one(request)
        data = entry.get_bind_data()
        self.assertEqual(data['distances'], [(60, '60 km')])
        self.assertFalse(data['include_distance'])

    def test_show(self):
        """show returns expected template variables
        """
        from ..models import Populaire
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
        populare_id = str(populaire)
        DBSession.add(populaire)
        request = testing.DummyRequest()
        request.matchdict['short_name'] = 'VicPop'
        entry = self._make_one(request)
        tmpl_vars = entry.show(MagicMock(name='form'))
        self.assertEqual(tmpl_vars['active_tab'], 'populaires')
        self.assertIn('brevets', tmpl_vars)
        self.assertIn('populaires', tmpl_vars)
        self.assertEqual(str(tmpl_vars['populaire']), populare_id)
        self.assertEqual(
            tmpl_vars['cancel_url'], 'http://example.com/populaires/VicPop')

    def test_register_success_duplicate_rider(self):
        """valid entry w/ duplicate rider name & email sets expected flash msgs
        """
        from ..models import (
            Populaire,
            PopulaireRider,
            )
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
        rider = PopulaireRider(
            email='tom@example.com',
            first_name='Tom',
            last_name='Dickson',
            distance=100,
            comment='',
            )
        populaire.riders.append(rider)
        DBSession.add(populaire)
        DBSession.add(rider)
        request = testing.DummyRequest()
        request.matchdict['short_name'] = 'VicPop'
        entry = self._make_one(request)
        url = entry.register_success({
            'email': 'tom@example.com',
            'first_name': 'Tom',
            'last_name': 'Dickson',
            'populaire': populaire.id,
            })
        self.assertEqual(url.location, 'http://example.com/populaires/VicPop')
        self.assertEqual(
            request.session.pop_flash(),
            ['duplicate', 'Tom Dickson', 'tom@example.com'])

    def test_register_success_new_rider(self):
        """valid entry for new rider adds rider to db & sets exp flash msgs
        """
        from ..models import (
            Populaire,
            PopulaireRider,
            )
        from ..views.site import populaire as pop_module
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
            google_doc_id='spreadsheet:'
                '0AtBTJntkFrPQdFJDN3lvRmVOQW5RXzRZbzRTRFJLYnc',
            )
        DBSession.add(populaire)
        request = testing.DummyRequest()
        request.matchdict['short_name'] = 'VicPop'
        entry = self._make_one(request)
        with patch.object(pop_module, 'update_google_spreadsheet'):
            url = entry.register_success({
                'email': 'fred@example.com',
                'first_name': 'Fred',
                'last_name': 'Dickson',
                'comment': 'Sunshine Man',
                'distance': 100,
                'populaire': populaire.id,
                })
        rider = DBSession.query(PopulaireRider).first()
        self.assertEqual(rider.email, 'fred@example.com')
        self.assertEqual(rider.full_name, 'Fred "Sunshine Man" Dickson')
        self.assertEqual(rider.lowercase_last_name, 'dickson')
        self.assertEqual(rider.distance, 100)
        self.assertEqual(url.location, 'http://example.com/populaires/VicPop')
        self.assertEqual(
            request.session.pop_flash(), ['success', 'fred@example.com'])

    def test_register_success_single_distance(self):
        """valid entry for single dstance populaire sets distance correctly
        """
        from ..models import (
            Populaire,
            PopulaireRider,
            )
        from ..views.site import populaire as pop_module
        populaire = Populaire(
            event_name="New Year's Populaire",
            short_name='NewYearsPop',
            distance='60 km',
            date_time=datetime(2013, 1, 1, 10, 0),
            start_locn='Kelseys Family Restaurant, 325 Burnside Rd W, Victoria',
            organizer_email='mcroy@example.com',
            registration_end=datetime(2012, 12, 31, 17, 0),
            entry_form_url='http://www.randonneurs.bc.ca/organize/eventform.pdf',
            google_doc_id='spreadsheet:'
                '0AtBTJntkFrPQdFJDN3lvRmVOQW5RXzRZbzRTRFJLYnc',
            )
        DBSession.add(populaire)
        request = testing.DummyRequest()
        request.matchdict['short_name'] = 'NewYearsPop'
        entry = self._make_one(request)
        with patch.object(pop_module, 'update_google_spreadsheet'):
            entry.register_success({
                'email': 'fred@example.com',
                'first_name': 'Fred',
                'last_name': 'Dickson',
                'comment': 'Sunshine Man',
                'populaire': populaire.id,
                })
        rider = DBSession.query(PopulaireRider).first()
        self.assertEqual(rider.distance, '60')

    def test_register_success_sends_2_emails(self):
        """successful entry sends emails to rider and organizer
        """
        from ..models import Populaire
        from ..views.site import populaire as pop_module
        populaire = Populaire(
            event_name="New Year's Populaire",
            short_name='NewYearsPop',
            distance='60 km',
            date_time=datetime(2013, 1, 1, 10, 0),
            start_locn='Kelseys Family Restaurant, 325 Burnside Rd W, Victoria',
            organizer_email='mcroy@example.com',
            registration_end=datetime(2012, 12, 31, 17, 0),
            entry_form_url='http://www.randonneurs.bc.ca/organize/eventform.pdf',
            google_doc_id='spreadsheet:'
                '0AtBTJntkFrPQdFJDN3lvRmVOQW5RXzRZbzRTRFJLYnc',
            )
        DBSession.add(populaire)
        request = testing.DummyRequest()
        request.matchdict['short_name'] = 'NewYearsPop'
        mailer = get_mailer(request)
        entry = self._make_one(request)
        with patch.object(pop_module, 'update_google_spreadsheet'):
            entry.register_success({
                'email': 'fred@example.com',
                'first_name': 'Fred',
                'last_name': 'Dickson',
                'comment': 'Sunshine Man',
                })
        self.assertEqual(len(mailer.outbox), 2)

    def test_rider_email_message(self):
        """registration confirmation email to rider has expected content
        """
        from ..models import (
            EmailAddress,
            Populaire,
            PopulaireRider,
            )
        populaire = Populaire(
            event_name="New Year's Populaire",
            short_name='NewYearsPop',
            distance='60 km',
            date_time=datetime(2013, 1, 1, 10, 0),
            start_locn='Kelseys Family Restaurant, 325 Burnside Rd W, Victoria',
            organizer_email='mcroy@example.com',
            registration_end=datetime(2012, 12, 31, 17, 0),
            entry_form_url='http://www.randonneurs.bc.ca/organize/eventform.pdf',
            google_doc_id='spreadsheet:'
                '0AtBTJntkFrPQdFJDN3lvRmVOQW5RXzRZbzRTRFJLYnc',
            )
        rider = PopulaireRider(
            email='fred@example.com',
            first_name='Fred',
            last_name='Dickson',
            distance=60,
            comment='',
            )
        request = testing.DummyRequest()
        request.matchdict['short_name'] = 'NewYearsPop'
        entry = self._make_one(request)
        DBSession.add(populaire)
        msg = entry._rider_message(populaire, rider)
        self.assertEqual(
            msg.subject, 'Pre-registration Confirmation for NewYearsPop')
        from_randopony = (
            DBSession.query(EmailAddress)
            .filter_by(key='from_randopony').first().email)
        self.assertEqual(msg.sender, from_randopony)
        self.assertEqual(msg.recipients, ['fred@example.com'])
        self.assertEqual(msg.extra_headers['Sender'], from_randopony)
        self.assertEqual(
            msg.extra_headers['Reply-To'], populaire.organizer_email)
        self.assertIn('NewYearsPop on Tue 01-Jan-2013', msg.body)
        self.assertIn(
            'list at <http://example.com/populaires/NewYearsPop>', msg.body)
        self.assertIn(
            'web site <http://www.randonneurs.bc.ca/organize/eventform.pdf>, '
            'read it', msg.body)

    def test_organizer_email_message_single_distance(self):
        """reg notify email to org for single dist event has expected content
        """
        from ..models import (
            EmailAddress,
            Populaire,
            PopulaireRider,
            )
        populaire = Populaire(
            event_name="New Year's Populaire",
            short_name='NewYearsPop',
            distance='60 km',
            date_time=datetime(2013, 1, 1, 10, 0),
            start_locn='Kelseys Family Restaurant, 325 Burnside Rd W, Victoria',
            organizer_email='mcroy@example.com',
            registration_end=datetime(2012, 12, 31, 17, 0),
            entry_form_url='http://www.randonneurs.bc.ca/organize/eventform.pdf',
            google_doc_id='spreadsheet:'
                '0AtBTJntkFrPQdFJDN3lvRmVOQW5RXzRZbzRTRFJLYnc',
            )
        rider = PopulaireRider(
            email='fred@example.com',
            first_name='Fred',
            last_name='Dickson',
            distance=60,
            comment='Sunshine Man',
            )
        request = testing.DummyRequest()
        request.matchdict['short_name'] = 'NewYearsPop'
        entry = self._make_one(request)
        DBSession.add(populaire)
        msg = entry._organizer_message(populaire, rider)
        self.assertEqual(
            msg.subject, 'Fred Dickson has Pre-registered for the NewYearsPop')
        from_randopony = (
            DBSession.query(EmailAddress)
            .filter_by(key='from_randopony').first().email)
        self.assertEqual(msg.sender, from_randopony)
        self.assertEqual(msg.recipients, [populaire.organizer_email])
        self.assertIn(
            'Fred "Sunshine Man" Dickson <fred@example.com> '
            'has pre-registered for the NewYearsPop.',
            msg.body)
        self.assertIn(
            'list at <http://example.com/populaires/NewYearsPop>', msg.body)
        self.assertIn(
            'spreadsheet at <https://spreadsheets.google.com/ccc?'
            'key=0AtBTJntkFrPQdFJDN3lvRmVOQW5RXzRZbzRTRFJLYnc>,',
            msg.body)
        self.assertIn('email address list at '
            '<http://example.com/populaire/NewYearsPop/rider_emails/'
            '524abf1c-0f42-545e-974f-91fba9b34f8d>.',
            msg.body)
        self.assertNotIn('Fred Dickson has indicated', msg.body)
        self.assertIn('please send email to <djl@douglatornell.ca>.', msg.body)

    def test_organizer_email_message_multi_distance(self):
        """reg notify email to org for multi-dist event has expected content
        """
        from ..models import (
            Populaire,
            PopulaireRider,
            )
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
            google_doc_id='spreadsheet:'
                '0AtBTJntkFrPQdFJDN3lvRmVOQW5RXzRZbzRTRFJLYnc',
            )
        rider = PopulaireRider(
            email='fred@example.com',
            first_name='Fred',
            last_name='Dickson',
            distance=100,
            comment='Sunshine Man',
            )
        request = testing.DummyRequest()
        request.matchdict['short_name'] = 'NewYearsPop'
        entry = self._make_one(request)
        DBSession.add(populaire)
        msg = entry._organizer_message(populaire, rider)
        self.assertIn(
            'Fred Dickson has indicated that zhe is planning to ride the 100 km',
             msg.body)

    def test_organizer_email_message_multi_organizer(self):
        """reg notify email to orgs for multi-org event has expected content
        """
        from ..models import (
            Populaire,
            PopulaireRider,
            )
        populaire = Populaire(
            event_name='Victoria Populaire',
            short_name='VicPop',
            distance='50 km, 100 km',
            date_time=datetime(2011, 3, 27, 10, 0),
            start_locn='University of Victoria, Parking Lot #2 '
                       'Gabriola Road, near McKinnon Gym)',
            organizer_email='mjansson@example.com, mcroy@example.com',
            registration_end=datetime(2011, 3, 24, 12, 0),
            entry_form_url='http://www.randonneurs.bc.ca/VicPop/'
                           'VicPop11_registration.pdf',
            google_doc_id='spreadsheet:'
                '0AtBTJntkFrPQdFJDN3lvRmVOQW5RXzRZbzRTRFJLYnc',
            )
        rider = PopulaireRider(
            email='fred@example.com',
            first_name='Fred',
            last_name='Dickson',
            distance=100,
            comment='Sunshine Man',
            )
        request = testing.DummyRequest()
        request.matchdict['short_name'] = 'NewYearsPop'
        entry = self._make_one(request)
        DBSession.add(populaire)
        msg = entry._organizer_message(populaire, rider)
        self.assertEqual(
            msg.recipients, ['mjansson@example.com', 'mcroy@example.com'])

    def test_register_success_queues_update_google_spreadsheet_task(self):
        """successful registration queues task to update rider list spreadsheet
        """
        from ..models import Populaire
        from ..views.site import populaire as pop_module
        populaire = Populaire(
            event_name="New Year's Populaire",
            short_name='NewYearsPop',
            distance='60 km',
            date_time=datetime(2013, 1, 1, 10, 0),
            start_locn='Kelseys Family Restaurant, 325 Burnside Rd W, Victoria',
            organizer_email='mcroy@example.com',
            registration_end=datetime(2012, 12, 31, 17, 0),
            entry_form_url='http://www.randonneurs.bc.ca/organize/eventform.pdf',
            google_doc_id='spreadsheet:'
                '0AtBTJntkFrPQdFJDN3lvRmVOQW5RXzRZbzRTRFJLYnc',
            )
        DBSession.add(populaire)
        request = testing.DummyRequest()
        request.matchdict['short_name'] = 'NewYearsPop'
        get_mailer(request)
        entry = self._make_one(request)
        with patch.object(pop_module, 'update_google_spreadsheet') as mock_task:
            entry.register_success({
                'email': 'fred@example.com',
                'first_name': 'Fred',
                'last_name': 'Dickson',
                'comment': 'Sunshine Man',
                })
        mock_task.delay.assert_called_once()

    def test_failure(self):
        """populaire entry form validation failure returns expected tmpl_vars
        """
        self.config.add_route('populaire', '/populaires/{short_name}')
        from ..models import Populaire
        self.config.add_route('populaire', '/populaires/{short_name}')
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
        populare_id = str(populaire)
        DBSession.add(populaire)
        request = testing.DummyRequest()
        request.matchdict['short_name'] = 'VicPop'
        entry = self._make_one(request)
        tmpl_vars = entry.failure(MagicMock(name='ValidationError'))
        self.assertEqual(tmpl_vars['active_tab'], 'populaires')
        self.assertIn('brevets', tmpl_vars)
        self.assertIn('populaires', tmpl_vars)
        self.assertEqual(str(tmpl_vars['populaire']), populare_id)
        self.assertEqual(
            tmpl_vars['cancel_url'], 'http://example.com/populaires/VicPop')
