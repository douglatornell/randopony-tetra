# -*- coding: utf-8 -*-
"""Tests for RandoPony public site brevet views and functionality.
"""
from datetime import datetime
import unittest

from mock import (
    MagicMock,
    Mock,
    patch,
)
from pyramid.threadlocal import get_current_request
import pytest

from ..views.site import brevet as brevet_module


@pytest.fixture(scope='module')
def views_core_module():
    from ..views.site import core
    return core


@pytest.fixture(scope='module')
def brevet_views_module():
    from ..views.site import brevet
    return brevet


@pytest.fixture(scope='module')
def views_class():
    from ..views.site.brevet import BrevetViews
    return BrevetViews


@pytest.fixture(scope='function')
def views(views_core_module, pyramid_config):
    """BrevetViews instance with mocked get_membership_link() function
    """
    from ..views.site.brevet import BrevetViews
    with patch.object(views_core_module, 'get_membership_link'):
        return BrevetViews(get_current_request())


@pytest.fixture(scope='function')
def entry(pyramid_config):
    from ..views.site.brevet import BrevetEntry
    return BrevetEntry(get_current_request())


@pytest.mark.usefixtures(
    'views_class', 'email_address_model', 'brevet_model', 'views_core_module',
    'brevet_views_module', 'db_session', 'pyramid_config',
)
class TestBrevetViews(object):
    """Unit tests for public site brevet views.

    *TODO*: Add integrations tests:

      * Registration closed & no register button rendered after registration_end
      * Past event template is rendered for events more than 7 days in the past
    """
    def test_region_list(
        self, views_class, email_address_model, brevet_model,
        views_core_module, db_session,
    ):
        """region_list view has expected tmpl_vars
        """
        email = email_address_model(
            key='admin_email', email='tom@example.com')
        db_session.add(email)
        with patch.object(views_core_module, 'get_membership_link'):
            views = views_class(get_current_request())
            tmpl_vars = views.region_list()
        assert tmpl_vars['active_tab'] == 'brevets'
        assert tmpl_vars['regions'] == brevet_model.REGIONS
        expected = set(brevet_model.REGIONS.keys())
        assert set(tmpl_vars['region_brevets'].keys()) == expected
        assert tmpl_vars['admin_email'] == 'tom@example.com'

    def test_region_list_brevet(
        self, views_class, email_address_model, brevet_model, core_model,
        views_core_module, db_session,
    ):
        """region_list view has expected tmpl_vars
        """
        brevet = brevet_model(
            region='LM',
            distance=200,
            date_time=datetime(2012, 11, 11, 7, 0, 0),
            route_name='11th Hour',
            start_locn='Bean Around the World Coffee, Lonsdale Quay, '
                       '123 Carrie Cates Ct, North Vancouver',
            organizer_email='tracy@example.com',
        )
        brevet_id = str(brevet)
        email = email_address_model(key='admin_email', email='tom@example.com')
        db_session.add_all((brevet, email))
        with patch.object(views_core_module, 'get_membership_link'):
            with patch.object(core_model, 'datetime') as m_datetime:
                m_datetime.today.return_value = datetime(
                    2012, 11, 1, 12, 55, 42)
                views = views_class(get_current_request())
                tmpl_vars = views.region_list()
        assert str(tmpl_vars['region_brevets']['LM'].one()) == brevet_id

    def test_brevet_list(
        self, views_class, email_address_model, brevet_model, core_model,
        views_core_module, db_session,
    ):
        """brevet_list view has expected tmpl_vars
        """
        brevet = brevet_model(
            region='LM',
            distance=200,
            date_time=datetime(2012, 11, 11, 7, 0, 0),
            route_name='11th Hour',
            start_locn='Bean Around the World Coffee, Lonsdale Quay, '
                       '123 Carrie Cates Ct, North Vancouver',
            organizer_email='tracy@example.com',
        )
        brevet_id = str(brevet)
        email = email_address_model(key='admin_email', email='tom@example.com')
        db_session.add_all((brevet, email))
        request = get_current_request()
        request.matchdict['region'] = 'LM'
        with patch.object(views_core_module, 'get_membership_link'):
            with patch.object(core_model, 'datetime') as m_datetime:
                m_datetime.today.return_value = datetime(
                    2012, 11, 1, 12, 55, 42)
                views = views_class(get_current_request())
                tmpl_vars = views.brevet_list()
        assert tmpl_vars['active_tab'] == 'brevets'
        assert tmpl_vars['region'] == 'LM'
        assert tmpl_vars['regions'] == brevet_model.REGIONS
        assert str(tmpl_vars['region_brevets'].one()) == brevet_id
        expected = {
            'file': 'LowerMainlandQuartet.jpg',
            'alt': 'Harrison Hotsprings Road',
            'credit': 'Nobo Yonemitsu',
        }
        assert tmpl_vars['image'] == expected

    def test_brevet_coming_soon_before_nov(self, views, brevet_views_module):
        """brevet this yr not in db redirects to coming soon for Jan-Oct
        """
        request = get_current_request()
        request.matchdict.update({
            'region': 'VI',
            'distance': '200',
            'date': '03Mar2013',
        })
        views._coming_soon_page = Mock(
            '_coming_soon', return_value='coming-soon body')
        with patch.object(brevet_views_module, 'datetime') as m_datetime:
            m_datetime.today.return_value = datetime(2013, 2, 1, 18, 35)
            m_datetime.strptime = datetime.strptime
            resp = views.brevet_page()
        assert resp.body == b'coming-soon body'

    def test_brevet_coming_soon_after_oct(self, views, brevet_views_module):
        """brevet this yr or next not in db redirects to coming soon for Nov-Dec
        """
        request = get_current_request()
        request.matchdict.update({
            'region': 'VI',
            'distance': '200',
            'date': '03Mar2013',
        })
        views._coming_soon_page = Mock(
            '_coming_soon', return_value='coming-soon body')
        with patch.object(brevet_views_module, 'datetime') as m_datetime:
            m_datetime.today.return_value = datetime(2012, 11, 1, 18, 1)
            m_datetime.strptime = datetime.strptime
            resp = views.brevet_page()
        assert resp.body == b'coming-soon body'

    def test_brevet_coming_soon_page(self, views, brevet_views_module):
        """_coming_soon_page calls render with expected args
        """
        request = get_current_request()
        request.matchdict.update({
            'region': 'VI',
            'distance': '200',
            'date': '03Mar2013',
        })
        with patch.object(brevet_views_module, 'get_membership_link'):
            with patch.object(brevet_views_module, 'render') as m_render:
                views._coming_soon_page()
        tmpl_name = m_render.call_args[0][0]
        tmpl_vars = m_render.call_args[0][1]
        kwargs = m_render.call_args[1]
        assert tmpl_name == 'coming-soon.mako'
        assert 'brevets' in tmpl_vars
        assert 'populaires' in tmpl_vars
        assert tmpl_vars['active_tab'] == 'brevets'
        assert tmpl_vars['maybe_brevet'] == 'VI200 03Mar2013'
        assert kwargs['request'] == request

    def test_brevet_not_in_db_and_not_coming_soon(
        self, views, brevet_views_module,
    ):
        """brevet date not in db & outside coming soon range raises 404
        """
        from pyramid.httpexceptions import HTTPNotFound
        request = get_current_request()
        request.matchdict.update({
            'region': 'VI',
            'distance': '200',
            'date': '03Mar2014',
        })
        with patch.object(brevet_views_module, 'datetime') as m_datetime:
            m_datetime.today.return_value = datetime(2013, 2, 13, 18, 43)
            m_datetime.strptime = datetime.strptime
            with pytest.raises(HTTPNotFound):
                views.brevet_page()

    def test_brevet_page_registration_open(
        self, views_class, brevet_model, brevet_views_module,
        views_core_module,
    ):
        """brevet_page view has expected tmpl_vars when registration is open
        """
        brevet = brevet_model(
            region='VI',
            distance=200,
            date_time=datetime(2013, 3, 3, 7, 0),
            route_name='Chilly 200',
            start_locn='Chez Croy, 3131 Millgrove St, Victoria',
            organizer_email='mcroy@example.com',
            registration_end=datetime(2013, 3, 2, 12, 0),
        )
        request = get_current_request()
        request.matchdict.update({
            'region': 'VI',
            'distance': '200',
            'date': '03Mar2013',
        })
        gml_patch = patch.object(
            views_core_module, 'get_membership_link')
        gefu_patch = patch.object(
            brevet_views_module, 'get_entry_form_url')
        gb_patch = patch.object(
            brevet_views_module, 'get_brevet', return_value=brevet)
        with gml_patch, gefu_patch, gb_patch:
            with patch.object(brevet_views_module, 'datetime') as m_dt:
                m_dt.utcnow.return_value = datetime(2013, 2, 22, 23, 18)
                m_dt.today.return_value = datetime(2013, 2, 22, 23, 18)
                views = views_class(get_current_request())
                tmpl_vars = views.brevet_page()
        assert tmpl_vars['active_tab'] == 'brevets'
        assert tmpl_vars['brevet'] == brevet
        assert not tmpl_vars['registration_closed']

    def test_brevet_page_registration_closed(
        self, views_class, brevet_model, brevet_views_module,
        views_core_module,
    ):
        """brevet_page view has expected tmpl_vars when registration closed
        """
        brevet = brevet_model(
            region='VI',
            distance=200,
            date_time=datetime(2013, 3, 3, 7, 0),
            route_name='Chilly 200',
            start_locn='Chez Croy, 3131 Millgrove St, Victoria',
            organizer_email='mcroy@example.com',
            registration_end=datetime(2013, 3, 2, 12, 0),
        )
        request = get_current_request()
        request.matchdict.update({
            'region': 'VI',
            'distance': '200',
            'date': '03Mar2013',
        })
        gml_patch = patch.object(
            views_core_module, 'get_membership_link')
        gefu_patch = patch.object(
            brevet_views_module, 'get_entry_form_url')
        gb_patch = patch.object(
            brevet_views_module, 'get_brevet', return_value=brevet)
        with gml_patch, gefu_patch, gb_patch:
            with patch.object(brevet_views_module, 'datetime') as m_dt:
                m_dt.utcnow.return_value = datetime(2013, 3, 2, 23, 24)
                m_dt.today.return_value = datetime(2013, 2, 2, 23, 24)
                views = views_class(get_current_request())
                tmpl_vars = views.brevet_page()
        assert tmpl_vars['registration_closed']

    def test_brevet_page_event_started(
        self, views_class, brevet_model, brevet_views_module,
        views_core_module,
    ):
        """brevet_page view has expected tmpl_vars when event has started
        """
        brevet = brevet_model(
            region='VI',
            distance=200,
            date_time=datetime(2013, 3, 3, 7, 0),
            route_name='Chilly 200',
            start_locn='Chez Croy, 3131 Millgrove St, Victoria',
            organizer_email='mcroy@example.com',
            registration_end=datetime(2013, 3, 2, 12, 0),
        )
        request = get_current_request()
        request.matchdict.update({
            'region': 'VI',
            'distance': '200',
            'date': '03Mar2013',
        })
        gml_patch = patch.object(
            views_core_module, 'get_membership_link')
        gefu_patch = patch.object(
            brevet_views_module, 'get_entry_form_url')
        gb_patch = patch.object(
            brevet_views_module, 'get_brevet', return_value=brevet)
        with gml_patch, gefu_patch, gb_patch:
            with patch.object(brevet_views_module, 'datetime') as m_dt:
                m_dt.utcnow.return_value = datetime(2013, 3, 3, 15, 1)
                m_dt.today.return_value = datetime(2013, 3, 3, 15, 1)
                views = views_class(get_current_request())
                tmpl_vars = views.brevet_page()
        assert tmpl_vars['event_started']

    def test_brevet_page_event_not_started(
        self, views_class, brevet_model, brevet_views_module,
        views_core_module,
    ):
        """brevet_page view has exp tmpl_vars up to 1 hr after event start
        """
        brevet = brevet_model(
            region='VI',
            distance=200,
            date_time=datetime(2013, 3, 3, 7, 0),
            route_name='Chilly 200',
            start_locn='Chez Croy, 3131 Millgrove St, Victoria',
            organizer_email='mcroy@example.com',
            registration_end=datetime(2013, 3, 2, 12, 0),
        )
        request = get_current_request()
        request.matchdict.update({
            'region': 'VI',
            'distance': '200',
            'date': '03Mar2013',
        })
        gml_patch = patch.object(
            views_core_module, 'get_membership_link')
        gefu_patch = patch.object(
            brevet_views_module, 'get_entry_form_url')
        gb_patch = patch.object(
            brevet_views_module, 'get_brevet', return_value=brevet)
        with gml_patch, gefu_patch, gb_patch:
            with patch.object(brevet_views_module, 'datetime') as m_dt:
                m_dt.utcnow.return_value = datetime(2013, 3, 3, 14, 59)
                m_dt.today.return_value = datetime(2013, 3, 3, 14, 59)
                views = views_class(get_current_request())
                tmpl_vars = views.brevet_page()
        assert not tmpl_vars['event_started']

    def test_brevet_page_past_event(
        self, views_class, brevet_model, brevet_views_module,
        views_core_module,
    ):
        """brevet_page view calls _moved_on_page for event >7 days ago
        """
        brevet = brevet_model(
            region='VI',
            distance=200,
            date_time=datetime(2013, 3, 3, 7, 0),
            route_name='Chilly 200',
            start_locn='Chez Croy, 3131 Millgrove St, Victoria',
            organizer_email='mcroy@example.com',
            registration_end=datetime(2013, 3, 2, 12, 0),
        )
        request = get_current_request()
        request.matchdict.update({
            'region': 'VI',
            'distance': '200',
            'date': '03Mar2013',
        })
        gml_patch = patch.object(
            views_core_module, 'get_membership_link')
        gefu_patch = patch.object(
            brevet_views_module, 'get_entry_form_url')
        gb_patch = patch.object(
            brevet_views_module, 'get_brevet', return_value=brevet)
        with gml_patch, gefu_patch, gb_patch:
            with patch.object(brevet_views_module, 'datetime') as m_dt:
                m_dt.today.return_value = datetime(2013, 3, 11, 18, 47)
                views = views_class(get_current_request())
                views._moved_on_page = Mock(
                    '_moved_on', return_value='moved-on body')
                resp = views.brevet_page()
        assert resp.body == b'moved-on body'

    def test_brevet_moved_on_page(
        self, views_class, brevet_model, brevet_views_module,
        views_core_module,
    ):
        """_moved_on_page calls render with expected args
        """
        brevet = brevet_model(
            region='VI',
            distance=200,
            date_time=datetime(2013, 3, 3, 7, 0),
            route_name='Chilly 200',
            start_locn='Chez Croy, 3131 Millgrove St, Victoria',
            organizer_email='mcroy@example.com',
            registration_end=datetime(2013, 3, 2, 12, 0),
        )
        request = get_current_request()
        request.matchdict.update({
            'region': 'VI',
            'distance': '200',
            'date': '03Mar2013',
        })
        gml_patch = patch.object(
            views_core_module, 'get_membership_link')
        gml_bv_patch = patch.object(
            brevet_views_module, 'get_membership_link',
            return_value='https://example.com/membership_link')
        gb_patch = patch.object(
            brevet_views_module, 'get_brevet', return_value=brevet)
        grl_patch = patch.object(
            brevet_views_module, 'get_results_link',
            return_value='https://example.com/browse/randonnees')
        with gml_patch, gml_bv_patch, gb_patch, grl_patch:
            with patch.object(brevet_views_module, 'render') as m_render:
                views = views_class(get_current_request())
                views._moved_on_page()
        tmpl_name = m_render.call_args[0][0]
        tmpl_vars = m_render.call_args[0][1]
        kwargs = m_render.call_args[1]
        assert tmpl_name == 'moved-on.mako'
        assert tmpl_vars['active_tab'] == 'brevets'
        assert 'brevets' in tmpl_vars
        assert 'populaires' in tmpl_vars
        assert str(tmpl_vars['event']) == 'VI200 03Mar2013'
        expected = 'https://example.com/browse/randonnees'
        assert tmpl_vars['results_link'] == expected
        expected = 'https://example.com/membership_link'
        assert tmpl_vars['membership_link'] == expected
        assert kwargs['request'] == request

    def test_rider_emails_invalid_uuid(
        self, views_class, brevet_views_module, views_core_module,
    ):
        """rider_emails raises 404 when request uuid doesn't match database
        """
        from pyramid.httpexceptions import HTTPNotFound
        request = get_current_request()
        request.matchdict.update({
            'region': 'VI',
            'distance': '200',
            'date': '03Mar2013',
            'uuid': 'foo',
        })
        gml_patch = patch.object(
            views_core_module, 'get_membership_link')
        gb_patch = patch.object(
            brevet_views_module, 'get_brevet',
            return_value=Mock(name='brevet', uuid='bar'))
        with gml_patch, gb_patch:
            views = views_class(get_current_request())
            with pytest.raises(HTTPNotFound):
                views.rider_emails()

    def test_rider_emails_past_event(
        self, views_class, brevet_views_module, views_core_module,
    ):
        """rider_emails raises 404 when event is beyond in_past horizon
        """
        from pyramid.httpexceptions import HTTPNotFound
        request = get_current_request()
        request.matchdict.update({
            'region': 'VI',
            'distance': '200',
            'date': '03Mar2013',
            'uuid': 'foo',
        })
        gml_patch = patch.object(
            views_core_module, 'get_membership_link')
        gb_patch = patch.object(
            brevet_views_module, 'get_brevet',
            return_value=Mock(name='brevet', uuid='foo'))
        with gml_patch, gb_patch:
            views = views_class(get_current_request())
            views._in_past = Mock(return_value=True)
            with pytest.raises(HTTPNotFound):
                views.rider_emails()

    def test_rider_emails_no_riders_registered(
        self, views_class, brevet_views_module, views_core_module,
    ):
        """rider_emails returns expected message when no riders are registered
        """
        request = get_current_request()
        request.matchdict.update({
            'region': 'VI',
            'distance': '200',
            'date': '03Mar2013',
            'uuid': 'foo',
        })
        gml_patch = patch.object(
            views_core_module, 'get_membership_link')
        gb_patch = patch.object(
            brevet_views_module, 'get_brevet',
            return_value=Mock(name='brevet', uuid='foo', riders=[]))
        with gml_patch, gb_patch:
            views = views_class(get_current_request())
            views._in_past = Mock(return_value=False)
            resp = views.rider_emails()
        assert resp == 'No riders have registered yet!'

    def test_rider_emails_list_of_addresses(
        self, views_class, brevet_views_module, views_core_module,
    ):
        """rider_emails returns expected list of registered rider's addresses
        """
        request = get_current_request()
        request.matchdict.update({
            'region': 'VI',
            'distance': '200',
            'date': '03Mar2013',
            'uuid': 'foo',
        })
        gml_patch = patch.object(
            views_core_module, 'get_membership_link')
        gb_patch = patch.object(
            brevet_views_module, 'get_brevet',
            return_value=Mock(
                name='brevet', uuid='foo',
                riders=[
                    Mock(name='rider_tom', email='tom@example.com'),
                    Mock(name='rider_dick', email='dick@example.com'),
                ]))
        with gml_patch, gb_patch:
            views = views_class(get_current_request())
            views._in_past = Mock(return_value=False)
            resp = views.rider_emails()
        assert resp == 'tom@example.com, dick@example.com'


@pytest.mark.usefixtures(
    'entry', 'brevet_model', 'db_session', 'pyramid_config',
)
class TestBrevetEntry(object):
    """Unit tests for brevet pre-registration form handler & views.

    *TODO*: Add integrations tests:

      * Valid pre-registration renders confirmation message
      * Duplicate pre-registration renders error message
    """
    def test_redirect_url(self, entry, pyramid_config):
        pyramid_config.add_route(
            'brevet', '/brevets/{region}/{distance}/{date}')
        url = entry._redirect_url('VI', 200, '03Mar2013')
        assert url == 'http://example.com/brevets/VI/200/03Mar2013'

    def test_show(self, entry, brevet_model, db_session, pyramid_config):
        pyramid_config.add_route(
            'brevet', '/brevets/{region}/{distance}/{date}')
        brevet = brevet_model(
            region='VI',
            distance=200,
            date_time=datetime(2013, 3, 3, 7, 0),
            route_name='Chilly 200',
            start_locn='Chez Croy, 3131 Millgrove St, Victoria',
            organizer_email='mcroy@example.com',
            registration_end=datetime(2013, 3, 2, 12, 0),
        )
        db_session.add(brevet)
        get_current_request().matchdict.update({
            'region': 'VI',
            'distance': '200',
            'date': '03Mar2013',
        })
        tmpl_vars = entry.show(Mock(name='form'))
        assert tmpl_vars['active_tab'] == 'brevets'
        assert 'brevets' in tmpl_vars
        assert 'populaires' in tmpl_vars
        assert tmpl_vars['brevet'] == brevet
        expected = 'http://example.com/brevets/VI/200/03Mar2013'
        assert tmpl_vars['cancel_url'] == expected


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
