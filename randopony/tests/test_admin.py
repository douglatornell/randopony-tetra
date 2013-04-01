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
        from .. import __version__ as version
        request = testing.DummyRequest()
        admin = self._make_one(request)
        tmpl_vars = admin.home()
        self.assertEqual(
            tmpl_vars,
            {
                'version': version.number + version.release,
                'logout_btn': True,
            })

    def test_wranglers_list(self):
        """admin wranglers view has expected template variables
        """
        from .. import __version__ as version
        request = testing.DummyRequest()
        request.matchdict['list'] = 'wranglers'
        admin = self._make_one(request)
        tmpl_vars = admin.items_list()
        self.assertEqual(
            tmpl_vars['version'], version.number + version.release)
        self.assertTrue(tmpl_vars['logout_btn'])
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
        from .. import __version__ as version
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
    """Unit tests for email_to_organizer function.
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
            google_doc_id='spreadsheet:'
                '0AtBTJntkFrPQdFJDN3lvRmVOQW5RXzRZbzRTRFJLYnc',
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
            google_doc_id='spreadsheet:'
                '0AtBTJntkFrPQdFJDN3lvRmVOQW5RXzRZbzRTRFJLYnc',
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
            'The URL is <http://example.com/brevets/VI/200/03Mar2013>.', msg.body)
        self.assertIn(
            'rider list URL is <https://spreadsheets.google.com/ccc?key='
            '0AtBTJntkFrPQdFJDN3lvRmVOQW5RXzRZbzRTRFJLYnc>.',
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
            google_doc_id='spreadsheet:'
                '0AtBTJntkFrPQdFJDN3lvRmVOQW5RXzRZbzRTRFJLYnc',
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
