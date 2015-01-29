# -*- coding: utf-8 -*-
"""Tests for RandoPony public site brevet views and functionality.
"""
from datetime import datetime
import unittest
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
from ..views.site import brevet as brevet_module


class TestBrevetViews(unittest.TestCase):
    """Unit tests for public site brevet views.

    *TODO*: Add integrations tests:

      * Registration closed & no register button rendered after registration_end
      * Past event template is rendered for events more than 7 days in the past
    """
    def _get_target_class(self):
        from ..views.site.brevet import BrevetViews
        return BrevetViews

    def _make_one(self, *args, **kwargs):
        from ..views.site import core
        with patch.object(core, 'get_membership_link'):
            return self._get_target_class()(*args, **kwargs)

    def setUp(self):
        self.config = testing.setUp()
        self.config.registry.settings['timezone'] = 'Canada/Pacific'
        engine = create_engine('sqlite://')
        DBSession.configure(bind=engine)
        Base.metadata.create_all(engine)

    def tearDown(self):
        DBSession.remove()
        testing.tearDown()

    def test_region_list(self):
        """region_list view has expected tmpl_vars
        """
        from ..models import (
            Brevet,
            EmailAddress,
        )
        email = EmailAddress(key='admin_email', email='tom@example.com')
        DBSession.add(email)
        request = testing.DummyRequest()
        views = self._make_one(request)
        tmpl_vars = views.region_list()
        self.assertEqual(tmpl_vars['active_tab'], 'brevets')
        self.assertEqual(tmpl_vars['regions'], Brevet.REGIONS)
        self.assertEqual(
            set(tmpl_vars['region_brevets'].keys()), set(Brevet.REGIONS.keys()))
        self.assertEqual(tmpl_vars['admin_email'], 'tom@example.com')

    def test_region_list_brevet(self):
        """region_list view has expected tmpl_vars
        """
        from ..models import core
        from ..models import (
            Brevet,
            EmailAddress,
        )
        brevet = Brevet(
            region='LM',
            distance=200,
            date_time=datetime(2012, 11, 11, 7, 0, 0), route_name='11th Hour',
            start_locn='Bean Around the World Coffee, Lonsdale Quay, '
                       '123 Carrie Cates Ct, North Vancouver',
            organizer_email='tracy@example.com',
        )
        brevet_id = str(brevet)
        email = EmailAddress(key='admin_email', email='tom@example.com')
        DBSession.add_all((brevet, email))
        request = testing.DummyRequest()
        with patch.object(core, 'datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2012, 11, 1, 12, 55, 42)
            views = self._make_one(request)
            tmpl_vars = views.region_list()
        self.assertEqual(
            str(tmpl_vars['region_brevets']['LM'].one()), brevet_id)

    def test_brevet_list(self):
        """brevet_list view has expected tmpl_vars
        """
        from ..models import core
        from ..models import (
            Brevet,
            EmailAddress,
        )
        brevet = Brevet(
            region='LM',
            distance=200,
            date_time=datetime(2012, 11, 11, 7, 0, 0), route_name='11th Hour',
            start_locn='Bean Around the World Coffee, Lonsdale Quay, '
                       '123 Carrie Cates Ct, North Vancouver',
            organizer_email='tracy@example.com',
        )
        brevet_id = str(brevet)
        email = EmailAddress(key='admin_email', email='tom@example.com')
        DBSession.add_all((brevet, email))
        request = testing.DummyRequest()
        request.matchdict['region'] = 'LM'
        with patch.object(core, 'datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2012, 11, 1, 12, 55, 42)
            views = self._make_one(request)
            tmpl_vars = views.brevet_list()
        self.assertEqual(tmpl_vars['active_tab'], 'brevets')
        self.assertEqual(tmpl_vars['region'], 'LM')
        self.assertEqual(tmpl_vars['regions'], Brevet.REGIONS)
        self.assertEqual(
            str(tmpl_vars['region_brevets'].one()), brevet_id)
        self.assertEqual(
            tmpl_vars['image'], {
                'file': 'LowerMainlandQuartet.jpg',
                'alt': 'Harrison Hotsprings Road',
                'credit': 'Nobo Yonemitsu',
            })

    def test_brevet_coming_soon_before_nov(self):
        """brevet this yr not in db redirects to coming soon for Jan-Oct
        """
        from ..views.site import brevet as brevet_module
        request = testing.DummyRequest()
        request.matchdict.update({
            'region': 'VI',
            'distance': '200',
            'date': '03Mar2013',
        })
        views = self._make_one(request)
        views._coming_soon_page = MagicMock(
            '_coming_soon', return_value='coming-soon body')
        datetime_patch = patch.object(brevet_module, 'datetime')
        with datetime_patch as mock_datetime:
            mock_datetime.today.return_value = datetime(2013, 2, 1, 18, 35)
            mock_datetime.strptime = datetime.strptime
            resp = views.brevet_page()
        self.assertEqual(resp.body, b'coming-soon body')

    def test_brevet_coming_soon_after_oct(self):
        """brevet this yr or next not in db redirects to coming soon for Nov-Dec
        """
        from ..views.site import brevet as brevet_module
        request = testing.DummyRequest()
        request.matchdict.update({
            'region': 'VI',
            'distance': '200',
            'date': '03Mar2013',
        })
        views = self._make_one(request)
        views._coming_soon_page = MagicMock(
            '_coming_soon', return_value='coming-soon body')
        datetime_patch = patch.object(brevet_module, 'datetime')
        with datetime_patch as mock_datetime:
            mock_datetime.today.return_value = datetime(2012, 11, 1, 18, 1)
            mock_datetime.strptime = datetime.strptime
            resp = views.brevet_page()
        self.assertEqual(resp.body, b'coming-soon body')

    def test_brevet_coming_soon_page(self):
        """_coming_soon_page calls render with expected args
        """
        from ..views.site import brevet as brevet_module
        request = testing.DummyRequest()
        request.matchdict.update({
            'region': 'VI',
            'distance': '200',
            'date': '03Mar2013',
        })
        views = self._make_one(request)
        render_patch = patch.object(brevet_module, 'render')
        with render_patch as mock_render:
            views._coming_soon_page()
        tmpl_name = mock_render.call_args[0][0]
        tmpl_vars = mock_render.call_args[0][1]
        kwargs = mock_render.call_args[1]
        self.assertEqual(tmpl_name, 'coming-soon.mako')
        self.assertIn('brevets', tmpl_vars)
        self.assertIn('populaires', tmpl_vars)
        self.assertEqual(tmpl_vars['active_tab'], 'brevets')
        self.assertEqual(tmpl_vars['maybe_brevet'], 'VI200 03Mar2013')
        self.assertEqual(kwargs['request'], request)

    def test_brevet_not_in_db_and_not_coming_soon(self):
        """brevet date not in db & outside coming soon range raises 404
        """
        from pyramid.httpexceptions import HTTPNotFound
        from ..views.site import brevet as brevet_module
        request = testing.DummyRequest()
        request.matchdict.update({
            'region': 'VI',
            'distance': '200',
            'date': '03Mar2014',
        })
        views = self._make_one(request)
        datetime_patch = patch.object(brevet_module, 'datetime')
        with datetime_patch as mock_datetime:
            mock_datetime.today.return_value = datetime(2013, 2, 13, 18, 43)
            mock_datetime.strptime = datetime.strptime
            with self.assertRaises(HTTPNotFound):
                views.brevet_page()

    def test_brevet_page_registration_open(self):
        """brevet_page view has expected tmpl_vars when registration is open
        """
        from ..models import (
            Brevet,
            Link,
        )
        from ..views.site import brevet as brevet_module
        brevet = Brevet(
            region='VI',
            distance=200,
            date_time=datetime(2013, 3, 3, 7, 0),
            route_name='Chilly 200',
            start_locn='Chez Croy, 3131 Millgrove St, Victoria',
            organizer_email='mcroy@example.com',
            registration_end=datetime(2013, 3, 2, 12, 0),
        )
        entry_form_link = Link(
            key='entry_form',
            url='http://www.randonneurs.bc.ca/organize/eventform.pdf',
        )
        DBSession.add_all((brevet, entry_form_link))
        request = testing.DummyRequest()
        request.matchdict.update({
            'region': 'VI',
            'distance': '200',
            'date': '03Mar2013',
        })
        views = self._make_one(request)
        with patch.object(brevet_module, 'datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = datetime(2011, 3, 22, 23, 18)
            mock_datetime.today.return_value = datetime(2011, 3, 22, 23, 18)
            tmpl_vars = views.brevet_page()
        self.assertEqual(tmpl_vars['active_tab'], 'brevets')
        self.assertEqual(tmpl_vars['brevet'], brevet)
        self.assertFalse(tmpl_vars['registration_closed'])

    def test_brevet_page_registration_closed(self):
        """brevet_page view has expected tmpl_vars when registration closed
        """
        from ..models import (
            Brevet,
            Link,
        )
        from ..views.site import brevet as brevet_module
        brevet = Brevet(
            region='VI',
            distance=200,
            date_time=datetime(2013, 3, 3, 7, 0),
            route_name='Chilly 200',
            start_locn='Chez Croy, 3131 Millgrove St, Victoria',
            organizer_email='mcroy@example.com',
            registration_end=datetime(2013, 3, 2, 12, 0),
        )
        entry_form_link = Link(
            key='entry_form',
            url='http://www.randonneurs.bc.ca/organize/eventform.pdf',
        )
        DBSession.add_all((brevet, entry_form_link))
        request = testing.DummyRequest()
        request.matchdict.update({
            'region': 'VI',
            'distance': '200',
            'date': '03Mar2013',
        })
        views = self._make_one(request)
        with patch.object(brevet_module, 'datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = datetime(2013, 3, 2, 23, 24)
            mock_datetime.today.return_value = datetime(2013, 3, 2, 23, 24)
            tmpl_vars = views.brevet_page()
        self.assertTrue(tmpl_vars['registration_closed'])

    def test_brevet_page_event_started(self):
        """brevet_page view has expected tmpl_vars when event has started
        """
        from ..models import (
            Brevet,
            Link,
        )
        from ..views.site import brevet as brevet_module
        brevet = Brevet(
            region='VI',
            distance=200,
            date_time=datetime(2013, 3, 3, 7, 0),
            route_name='Chilly 200',
            start_locn='Chez Croy, 3131 Millgrove St, Victoria',
            organizer_email='mcroy@example.com',
            registration_end=datetime(2013, 3, 2, 12, 0),
        )
        entry_form_link = Link(
            key='entry_form',
            url='http://www.randonneurs.bc.ca/organize/eventform.pdf',
        )
        DBSession.add_all((brevet, entry_form_link))
        request = testing.DummyRequest()
        request.matchdict.update({
            'region': 'VI',
            'distance': '200',
            'date': '03Mar2013',
        })
        views = self._make_one(request)
        with patch.object(brevet_module, 'datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = datetime(2013, 3, 3, 15, 1)
            mock_datetime.today.return_value = datetime(2013, 3, 3, 15, 1)
            tmpl_vars = views.brevet_page()
        self.assertTrue(tmpl_vars['event_started'])

    def test_brevet_page_event_not_started(self):
        """brevet_page view has exp tmpl_vars up to 1 hr after event start
        """
        from ..models import (
            Brevet,
            Link,
        )
        from ..views.site import brevet as brevet_module
        brevet = Brevet(
            region='VI',
            distance=200,
            date_time=datetime(2013, 3, 3, 7, 0),
            route_name='Chilly 200',
            start_locn='Chez Croy, 3131 Millgrove St, Victoria',
            organizer_email='mcroy@example.com',
            registration_end=datetime(2013, 3, 2, 12, 0),
        )
        entry_form_link = Link(
            key='entry_form',
            url='http://www.randonneurs.bc.ca/organize/eventform.pdf',
        )
        DBSession.add_all((brevet, entry_form_link))
        request = testing.DummyRequest()
        request.matchdict.update({
            'region': 'VI',
            'distance': '200',
            'date': '03Mar2013',
        })
        views = self._make_one(request)
        with patch.object(brevet_module, 'datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = datetime(2013, 3, 3, 14, 59)
            mock_datetime.today.return_value = datetime(2013, 3, 3, 14, 59)
            tmpl_vars = views.brevet_page()
        self.assertFalse(tmpl_vars['event_started'])

    def test_brevet_page_past_event(self):
        """brevet_page view calls _moved_on_page for event >7 days ago
        """
        from ..models import (
            Link,
            Brevet,
        )
        from ..views.site import brevet as brevet_module
        brevet = Brevet(
            region='VI',
            distance=200,
            date_time=datetime(2013, 3, 3, 7, 0),
            route_name='Chilly 200',
            start_locn='Chez Croy, 3131 Millgrove St, Victoria',
            organizer_email='mcroy@example.com',
            registration_end=datetime(2013, 3, 2, 12, 0),
        )
        results_link = Link(
            key='results_link',
            url='https://database.randonneurs.bc.ca/browse/randonnees',
        )
        DBSession.add_all((brevet, results_link))
        request = testing.DummyRequest()
        request.matchdict.update({
            'region': 'VI',
            'distance': '200',
            'date': '03Mar2013',
        })
        views = self._make_one(request)
        views._moved_on_page = MagicMock(
            '_moved_on', return_value='moved-on body')
        with patch.object(brevet_module, 'datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2013, 3, 11, 18, 47)
            resp = views.brevet_page()
        self.assertEqual(resp.body, b'moved-on body')

    def test_brevet_moved_on_page(self):
        """_moved_on_page calls render with expected args
        """
        from ..models import (
            Brevet,
            Link,
        )
        from ..views.site import brevet as brevet_module
        brevet = Brevet(
            region='VI',
            distance=200,
            date_time=datetime(2013, 3, 3, 7, 0),
            route_name='Chilly 200',
            start_locn='Chez Croy, 3131 Millgrove St, Victoria',
            organizer_email='mcroy@example.com',
            registration_end=datetime(2013, 3, 2, 12, 0),
        )
        results_link = Link(
            key='results_link',
            url='https://database.randonneurs.bc.ca/browse/randonnees',
        )
        DBSession.add_all((brevet, results_link))
        request = testing.DummyRequest()
        request.matchdict.update({
            'region': 'VI',
            'distance': '200',
            'date': '03Mar2013',
        })
        views = self._make_one(request)
        render_patch = patch.object(brevet_module, 'render')
        with render_patch as mock_render:
            views._moved_on_page()
        tmpl_name = mock_render.call_args[0][0]
        tmpl_vars = mock_render.call_args[0][1]
        kwargs = mock_render.call_args[1]
        self.assertEqual(tmpl_name, 'moved-on.mako')
        self.assertIn('brevets', tmpl_vars)
        self.assertIn('populaires', tmpl_vars)
        self.assertEqual(tmpl_vars['active_tab'], 'brevets')
        self.assertEqual(str(tmpl_vars['event']), 'VI200 03Mar2013')
        self.assertEqual(
            tmpl_vars['results_link'],
            'https://database.randonneurs.bc.ca/browse/randonnees')
        self.assertEqual(kwargs['request'], request)

    @patch.object(brevet_module, 'get_brevet')
    def test_rider_emails_invalid_uuid(self, mock_get_brevet):
        """rider_emails raises 404 when request uuid doesn't match database
        """
        from pyramid.httpexceptions import HTTPNotFound
        mock_get_brevet.return_value = MagicMock(name='brevet', uuid='bar')
        request = testing.DummyRequest()
        request.matchdict.update({
            'region': 'VI',
            'distance': '200',
            'date': '03Mar2013',
            'uuid': 'foo',
        })
        views = self._make_one(request)
        with self.assertRaises(HTTPNotFound):
            views.rider_emails()

    @patch.object(brevet_module, 'get_brevet')
    def test_rider_emails_past_event(self, mock_get_brevet):
        """rider_emails raises 404 when event is beyond in_past horizon
        """
        from pyramid.httpexceptions import HTTPNotFound
        mock_get_brevet.return_value = MagicMock(name='brevet', uuid='foo')
        request = testing.DummyRequest()
        request.matchdict.update({
            'region': 'VI',
            'distance': '200',
            'date': '03Mar2013',
            'uuid': 'foo',
        })
        views = self._make_one(request)
        views._in_past = MagicMock(return_value=True)
        with self.assertRaises(HTTPNotFound):
            views.rider_emails()

    @patch.object(brevet_module, 'get_brevet')
    def test_rider_emails_no_riders_registered(self, mock_get_brevet):
        """rider_emails returns expected message when no riders are registered
        """
        mock_get_brevet.return_value = MagicMock(name='brevet', uuid='foo')
        request = testing.DummyRequest()
        request.matchdict.update({
            'region': 'VI',
            'distance': '200',
            'date': '03Mar2013',
            'uuid': 'foo',
        })
        views = self._make_one(request)
        views._in_past = MagicMock(return_value=False)
        resp = views.rider_emails()
        self.assertEqual(resp, 'No riders have registered yet!')

    @patch.object(brevet_module, 'get_brevet')
    def test_rider_emails_list_of_addresses(self, mock_get_brevet):
        """rider_emails returns expected list of registered rider's addresses
        """
        mock_riders = [
            MagicMock(name='rider_tom', email='tom@example.com'),
            MagicMock(name='rider_dick', email='dick@example.com'),
        ]
        mock_get_brevet.return_value = MagicMock(
            name='brevet', uuid='foo', riders=mock_riders)
        request = testing.DummyRequest()
        request.matchdict.update({
            'region': 'VI',
            'distance': '200',
            'date': '03Mar2013',
            'uuid': 'foo',
        })
        views = self._make_one(request)
        views._in_past = MagicMock(return_value=False)
        resp = views.rider_emails()
        self.assertEqual(resp, 'tom@example.com, dick@example.com')


class TestBrevetEntry(unittest.TestCase):
    """Unit tests for brevet pre-registration form handler & views.

    *TODO*: Add integrations tests:

      * Valid pre-registration renders confirmation message
      * Duplicate pre-registration renders error message
    """
    def _get_target_class(self):
        from ..views.site.brevet import BrevetEntry
        return BrevetEntry

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
        self.config.add_route('brevet', '/brevets/{region}/{distance}/{date}')
        self.config.add_route(
            'brevet.rider_emails',
            '/brevet/{region}/{distance}/{date}/rider_emails/{uuid}')
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
        """_redirect_url returns expected brevet page URL
        """
        request = testing.DummyRequest()
        entry = self._make_one(request)
        url = entry._redirect_url('VI', 200, '03Mar2013')
        self.assertEqual(url, 'http://example.com/brevets/VI/200/03Mar2013')

    def test_show(self):
        """show returns expected template variables
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
        entry = self._make_one(request)
        tmpl_vars = entry.show(MagicMock(name='form'))
        self.assertEqual(tmpl_vars['active_tab'], 'brevets')
        self.assertIn('brevets', tmpl_vars)
        self.assertIn('populaires', tmpl_vars)
        self.assertEqual(tmpl_vars['brevet'], brevet)
        self.assertEqual(
            tmpl_vars['cancel_url'],
            'http://example.com/brevets/VI/200/03Mar2013')


class TestMakeSpreadsheetRowDict(unittest.TestCase):
    """Unit tests for _make_spreadsheet_row_dict function.
    """
    def _call_make_spreadsheet_row_dict(self, *args, **kwargs):
        from ..views.site.brevet import _make_spreadsheet_row_dict
        return _make_spreadsheet_row_dict(*args, **kwargs)

    @patch.object(brevet_module, '_get_member_status_by_name')
    def test_member_status_unknown(self, mock_gmsbn):
        """clubmember value set to "Unknown" when member_status in None
        """
        mock_rider = MagicMock(name='mock_rider', member_status=None)
        mock_gmsbn.return_value = None
        row_data = self._call_make_spreadsheet_row_dict(
            1, mock_rider, 'is_current_member_url')
        self.assertEqual(row_data['clubmember'], 'Unknown')

    def test_member_status_true(self):
        """clubmember value set to "Yes" when member_status in True
        """
        mock_rider = MagicMock(name='mock_rider', member_status=True)
        row_data = self._call_make_spreadsheet_row_dict(
            1, mock_rider, 'is_current_member_url')
        self.assertEqual(row_data['clubmember'], 'Yes')

    @patch.object(brevet_module, '_get_member_status_by_name')
    def test_member_status_false(self, mock_gmsbn):
        """clubmember value set to "No" when member_status in False
        """
        mock_rider = MagicMock(name='mock_rider', member_status=False)
        mock_gmsbn.return_value = False
        row_data = self._call_make_spreadsheet_row_dict(
            1, mock_rider, 'is_current_member_url')
        self.assertEqual(row_data['clubmember'], 'No')

    @patch.object(brevet_module, '_get_member_status_by_name')
    def test_member_status_not_updated_if_true(self, mock_gmsbn):
        """don't update member status from club database if it is True
        """
        mock_rider = MagicMock(name='mock_rider', member_status=True)
        self._call_make_spreadsheet_row_dict(
            1, mock_rider, 'is_current_member_url')
        self.assertFalse(mock_gmsbn.called)

    @patch.object(brevet_module, '_get_member_status_by_name')
    def test_update_member_status_if_none(self, mock_gmsbn):
        """update member status from club database if it is none
        """
        mock_rider = MagicMock(
            name='mock_rider',
            first_name='Tom',
            last_name='Jones',
            member_status=None,
        )
        self._call_make_spreadsheet_row_dict(
            1, mock_rider, 'is_current_member_url')
        mock_gmsbn.assert_called_once_with(
            'Tom', 'Jones', 'is_current_member_url')

    @patch.object(brevet_module, '_get_member_status_by_name')
    def test_update_member_status_if_false(self, mock_gmsbn):
        """update member status from club database if it is False
        """
        mock_rider = MagicMock(
            name='mock_rider',
            first_name='Tom',
            last_name='Jones',
            member_status=False,
        )
        self._call_make_spreadsheet_row_dict(
            1, mock_rider, 'is_current_member_url')
        mock_gmsbn.assert_called_once_with(
            'Tom', 'Jones', 'is_current_member_url')
