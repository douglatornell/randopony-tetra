# -*- coding: utf-8 -*-
"""Tests for RandoPony admin views and functionality.
"""
from datetime import datetime
import unittest
try:
    from unittest.mock import patch
except ImportError:                  # pragma: no cover
    from mock import patch
from pyramid import testing
from pyramid_mailer import get_mailer
from sqlalchemy import create_engine
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

    def test_home(self):
        """admin home view has expected template variables
        """
        from .. import __pkg_metadata__ as version
        request = testing.DummyRequest()
        admin = self._make_one(request)
        tmpl_vars = admin.home()
        self.assertEqual(
            tmpl_vars, {'version': version.number + version.release})

    def test_wranglers_list(self):
        """admin wranglers view has expected template variables
        """
        from .. import __pkg_metadata__ as version
        request = testing.DummyRequest()
        request.matchdict['list'] = 'wranglers'
        admin = self._make_one(request)
        tmpl_vars = admin.items_list()
        self.assertEqual(
            tmpl_vars['version'], version.number + version.release)
        self.assertEqual(tmpl_vars['list'], 'wranglers')
        self.assertEqual(tmpl_vars['list_title'], 'Pony Wranglers')
        self.assertEqual(tmpl_vars['action'], 'edit')

    def test_wranglers_list_order(self):
        """admin wranglers list is alpha ordered by persona email
        """
        from ..models import Administrator
        admin1 = Administrator(persona_email='tom@example.com')
        admin2 = Administrator(persona_email='harry@example.com')
        DBSession.add_all((admin1, admin2))
        request = testing.DummyRequest()
        request.matchdict['list'] = 'wranglers'
        admin = self._make_one(request)
        tmpl_vars = admin.items_list()
        admins = [a.persona_email for a in tmpl_vars['items'].all()]
        self.assertEqual(
            admins, 'harry@example.com tom@example.com'.split())

    def test_delete_cancel(self):
        """admin delete cancel leaves item in database
        """
        from ..models import Administrator
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
        from .. import __pkg_metadata__ as version
        self.config.add_route('admin.list', '/admin/{list}/')
        request = testing.DummyRequest()
        request.matchdict['list'] = 'wranglers'
        request.matchdict['item'] = 'tom@example.com'
        admin = self._make_one(request)
        tmpl_vars = admin.delete()
        self.assertEqual(
            tmpl_vars,
            {
                'version': version.number + version.release,
                'list': 'wranglers',
                'item': 'tom@example.com',
                'item_type': 'administrator',
            })

    def test_delete_wrangler(self):
        """admin delete for wrangler deletes item from database
        """
        from sqlalchemy.orm.exc import NoResultFound
        from ..models import Administrator
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
        self.config.add_route('admin.list', '/admin/{list}/')
        request = testing.DummyRequest(post={'delete': 'delete'})
        request.matchdict['list'] = 'brevets'
        request.matchdict['item'] = str(brevet)
        with patch.object(core, 'datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2012, 11, 1, 12, 55, 42)
            admin = self._make_one(request)
        admin.delete()
        with self.assertRaises(NoResultFound):
            Brevet.get_current().one()


class TestEmailToOrganizer(unittest.TestCase):
    """Unit tests for email_to_organizer admin function re: event URLs.
    """
    def _call_email_to_organizer(self, *args, **kwargs):
        from ..views.admin.core import email_to_organizer
        return email_to_organizer(*args, **kwargs)

    def setUp(self):
        from ..models import EmailAddress
        self.config = testing.setUp(
            settings={
                'mako.directories': 'randopony:templates',
            })
        self.config.include('pyramid_mailer.testing')
        self.config.include('pyramid_mako')
        self.config.add_route(
            'admin.populaires.view', '/admin/brevet/{item}')
        self.config.add_route(
            'brevet', '/brevets/{region}/{distance}/{date}')
        self.config.add_route(
            'brevet.rider_emails',
            '/brevets/{region}/{distance}/{date}/rider_emails/{uuid}')
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

    def test_email_to_organizer_catches_missing_google_doc_id(self):
        """email_to_organizer return error flash if google_doc_id not set
        """
        from ..models import Brevet
        brevet = Brevet(
            region='VI',
            distance=200,
            date_time=datetime(2013, 3, 3, 7, 0),
            route_name='Chilly 200',
            start_locn='Chez Croy, 3131 Millgrove St, Victoria',
            organizer_email='mcroy@example.com',
            registration_end=datetime(2013, 3, 2, 12, 0),
        )
        DBSession.add(brevet)
        request = testing.DummyRequest()
        request.matchdict.update({
            'region': 'VI',
            'distance': '200',
            'date': '03Mar2013',
        })
        date = '03Mar2013'
        event_page_url = request.route_url(
            'brevet', region=brevet.region, distance=brevet.distance,
            date=date)
        rider_emails_url = request.route_url(
            'brevet.rider_emails', region=brevet.region,
            distance=brevet.distance, date=date, uuid=brevet.uuid)
        flash = self._call_email_to_organizer(
            request, brevet, event_page_url, rider_emails_url)
        self.assertEqual(
            flash, [
                'error',
                'Google Drive rider list must be created before email to '
                'organizer(s) can be sent'
            ])

    def test_email_to_organizer_sends_email(self):
        """email_to_organizer sends message & sets expected flash message
        """
        from ..models import Brevet
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
        request.matchdict.update({
            'region': 'VI',
            'distance': '200',
            'date': '03Mar2013',
        })
        date = '03Mar2013'
        event_page_url = request.route_url(
            'brevet', region=brevet.region, distance=brevet.distance,
            date=date)
        rider_emails_url = request.route_url(
            'brevet.rider_emails', region=brevet.region,
            distance=brevet.distance, date=date, uuid=brevet.uuid)
        mailer = get_mailer(request)
        flash = self._call_email_to_organizer(
            request, brevet, event_page_url, rider_emails_url)
        self.assertEqual(len(mailer.outbox), 1)
        self.assertEqual(
            flash,
            ['success', 'Email sent to VI200 03Mar2013 organizer(s)'])

    def test_email_to_organizer_message(self):
        """email_to_organizer message has expected content
        """
        from ..models import (
            EmailAddress,
            Brevet,
        )
        brevet = Brevet(
            region='VI',
            distance=200,
            date_time=datetime(2013, 3, 3, 7, 0),
            route_name='Chilly 200',
            start_locn='Chez Croy, 3131 Millgrove St, Victoria',
            organizer_email='mcroy@example.com',
            registration_end=datetime(2013, 3, 2, 12, 0),
            google_doc_id='spreadsheet:123'
        )
        DBSession.add(brevet)
        request = testing.DummyRequest()
        request.matchdict.update({
            'region': 'VI',
            'distance': '200',
            'date': '03Mar2013',
        })
        date = '03Mar2013'
        event_page_url = request.route_url(
            'brevet', region=brevet.region, distance=brevet.distance,
            date=date)
        rider_emails_url = request.route_url(
            'brevet.rider_emails', region=brevet.region,
            distance=brevet.distance, date=date, uuid=brevet.uuid)
        mailer = get_mailer(request)
        self._call_email_to_organizer(
            request, brevet, event_page_url, rider_emails_url)
        msg = mailer.outbox[0]
        self.assertEqual(msg.subject, 'RandoPony URLs for VI200 03Mar2013')
        from_randopony = (
            DBSession.query(EmailAddress)
            .filter_by(key='from_randopony').first().email)
        self.assertEqual(msg.sender, from_randopony)
        self.assertEqual(msg.recipients, ['mcroy@example.com'])
        self.assertIn(
            'The URL is <http://example.com/brevets/VI/200/03Mar2013>.',
            msg.body)
        self.assertIn(
            'rider list URL is <https://spreadsheets.google.com/ccc?key=123>.',
            msg.body)
        self.assertIn(
            'email address list URL is <http://example.com/brevets/'
            'VI/200/03Mar2013/rider_emails/'
            'ba8e8e00-dd42-5c6c-9b30-b65ce9c8df26>.',
            msg.body)
        self.assertIn(
            'Pre-registration on the pony closes at 12:00 on 2013-03-02',
            msg.body)
        self.assertIn('send email to <djl@douglatornell.ca>.', msg.body)

    def test_email_to_organizer_multi_organizer(self):
        """email to organizer has expected to list for multi-organizer event
        """
        from ..models import Brevet
        brevet = Brevet(
            region='VI',
            distance=200,
            date_time=datetime(2013, 3, 3, 7, 0),
            route_name='Chilly 200',
            start_locn='Chez Croy, 3131 Millgrove St, Victoria',
            organizer_email='mjansson@example.com, mcroy@example.com',
            registration_end=datetime(2013, 3, 2, 12, 0),
            google_doc_id='spreadsheet:1234'
        )
        DBSession.add(brevet)
        request = testing.DummyRequest()
        request.matchdict.update({
            'region': 'VI',
            'distance': '200',
            'date': '03Mar2013',
        })
        date = '03Mar2013'
        event_page_url = request.route_url(
            'brevet', region=brevet.region, distance=brevet.distance,
            date=date)
        rider_emails_url = request.route_url(
            'brevet.rider_emails', region=brevet.region,
            distance=brevet.distance, date=date, uuid=brevet.uuid)
        mailer = get_mailer(request)
        self._call_email_to_organizer(
            request, brevet, event_page_url, rider_emails_url)
        msg = mailer.outbox[0]
        self.assertEqual(
            msg.recipients, ['mjansson@example.com', 'mcroy@example.com'])


class TestEmailToWebmaster(unittest.TestCase):
    """Unit tests for email_to_webmaster admin function re: event page URL.
    """
    def _call_email_to_webmaster(self, *args, **kwargs):
        from ..views.admin.core import email_to_webmaster
        return email_to_webmaster(*args, **kwargs)

    def setUp(self):
        from ..models import EmailAddress
        self.config = testing.setUp(
            settings={
                'mako.directories': 'randopony:templates',
            })
        self.config.include('pyramid_mailer.testing')
        self.config.include('pyramid_mako')
        self.config.add_route(
            'admin.populaires.view', '/admin/populaire/{item}')
        self.config.add_route(
            'populaire', '/populaires/{short_name}')
        engine = create_engine('sqlite://')
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)
        from_randopony = EmailAddress(
            key='from_randopony',
            email='randopony@randonneurs.bc.ca',
        )
        club_webmaster = EmailAddress(
            key='club_webmaster',
            email='webmaster@randonneurs.bc.ca',
        )
        admin_email = EmailAddress(
            key='admin_email',
            email='djl@douglatornell.ca',
        )
        DBSession.add_all((from_randopony, club_webmaster, admin_email))

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_email_to_webmaster_sends_email(self):
        """email_to_webmaster sends message & sets expected flash message
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
            google_doc_id='spreadsheet:1234'
        )
        DBSession.add(populaire)
        request = testing.DummyRequest()
        request.matchdict['item'] = 'VicPop'
        event_page_url = request.route_url(
            'populaire', short_name=populaire.short_name)
        mailer = get_mailer(request)
        flash = self._call_email_to_webmaster(
            request, populaire, event_page_url)
        self.assertEqual(len(mailer.outbox), 1)
        self.assertEqual(
            flash,
            ['success', 'Email with VicPop page URL sent to webmaster'])

    def test_email_to_webmaster_message(self):
        """email_to_webmaster message has expected content
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
            google_doc_id='spreadsheet:1234'
        )
        DBSession.add(populaire)
        request = testing.DummyRequest()
        request.matchdict['item'] = 'VicPop'
        event_page_url = request.route_url(
            'populaire', short_name=populaire.short_name)
        mailer = get_mailer(request)
        self._call_email_to_webmaster(request, populaire, event_page_url)
        msg = mailer.outbox[0]
        self.assertEqual(
            msg.subject, 'RandoPony Pre-registration page for VicPop')
        self.assertEqual(msg.sender, 'randopony@randonneurs.bc.ca')
        self.assertEqual(msg.recipients, ['webmaster@randonneurs.bc.ca'])
        self.assertIn('page for the VicPop event has been added', msg.body)
        self.assertIn(
            'The URL is <http://example.com/populaires/VicPop>.', msg.body)
        self.assertIn('send email to <djl@douglatornell.ca>.', msg.body)


class TestFinalizeFlashMsg(unittest.TestCase):
    """Unit tests for finalize_flash_msg function.
    """
    def _call_finalize_flash_msg(self, *args, **kwargs):
        from ..views.admin.core import finalize_flash_msg
        return finalize_flash_msg(*args, **kwargs)

    def test_finalize_flash_msg_error(self):
        """flash 1st element is error when error present in flash list
        """
        request = testing.DummyRequest()
        self._call_finalize_flash_msg(request, 'success foo error bar'.split())
        flash = request.session.pop_flash()
        self.assertEqual(flash[0], 'error')

    def test_finalize_flash_msg_success(self):
        """flash 1st element is success when error not present in flash list
        """
        request = testing.DummyRequest()
        self._call_finalize_flash_msg(
            request, 'success foo sucess bar'.split())
        flash = request.session.pop_flash()
        self.assertEqual(flash[0], 'success')

    def test_finalize_flash_msg_content(self):
        """flash[1:] are msgs w/o error or success elements of flash list
        """
        request = testing.DummyRequest()
        self._call_finalize_flash_msg(request, 'success foo error bar'.split())
        flash = request.session.pop_flash()
        self.assertEqual(flash[1:], 'foo bar'.split())
