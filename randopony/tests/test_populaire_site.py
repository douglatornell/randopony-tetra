# -*- coding: utf-8 -*-
"""Tests for RandoPony public site populaire views and functionality.
"""
from datetime import datetime
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
from pyramid.threadlocal import get_current_request
from pyramid_mailer import get_mailer
import pytest

from ..models.meta import DBSession


@pytest.fixture(scope='module')
def views_module():
    from ..views.site import populaire
    return populaire


@pytest.fixture(scope='module')
def views_class():
    from ..views.site.populaire import PopulaireViews
    return PopulaireViews


@pytest.fixture(scope='function')
def entry(pyramid_config):
    from ..views.site.populaire import PopulaireEntry
    return PopulaireEntry(get_current_request())


@pytest.mark.usefixtures(
    'views_class', 'email_address_model', 'pop_model',
    'views_core_module', 'views_module', 'db_session',
    'pyramid_config',
)
class TestPopulaireViews(object):
    """Unit tests for public site populaire views.

    *TODO*: Add integrations tests:

      * Registration closed & no register button rendered after registration_end
      * Past event template is rendered for events more than 7 days in the past
    """
    def test_populaire_list(
        self, views_class, email_address_model, views_core_module, db_session,
    ):
        """populaire_list view has expected tmpl_vars
        """
        email = email_address_model(key='admin_email', email='tom@example.com')
        db_session.add(email)
        with patch.object(views_core_module, 'get_membership_link'):
            views = views_class(get_current_request())
            tmpl_vars = views.populaire_list()
        assert tmpl_vars['active_tab'] == 'populaires'
        assert tmpl_vars['admin_email'] == 'tom@example.com'

    def test_populaire_page_registration_open(
        self, views_class, pop_model, views_module, views_core_module,
    ):
        """populaire_page view has expected tmpl_vars when registration is open
        """
        populaire = pop_model(
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
        request = get_current_request()
        request.matchdict['short_name'] = 'VicPop'
        gml_patch = patch.object(views_core_module, 'get_membership_link')
        gp_patch = patch.object(
            views_module, 'get_populaire', return_value=populaire)
        with gml_patch, gp_patch:
            with patch.object(views_module, 'datetime') as m_dt:
                m_dt.utcnow.return_value = datetime(2011, 3, 22, 23, 18)
                m_dt.today.return_value = datetime(2011, 3, 22, 23, 18)
                views = views_class(request)
                tmpl_vars = views.populaire_page()
        assert tmpl_vars['active_tab'] == 'populaires'
        assert tmpl_vars['populaire'] == populaire
        assert not tmpl_vars['registration_closed']

    def test_populaire_page_registration_closed(
            self, views_class, pop_model, views_module, views_core_module,
    ):
        """populaire_page view has expected tmpl_vars when registration closed
        """
        populaire = pop_model(
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
        request = get_current_request()
        request.matchdict['short_name'] = 'VicPop'
        gml_patch = patch.object(views_core_module, 'get_membership_link')
        gp_patch = patch.object(
            views_module, 'get_populaire', return_value=populaire)
        with gml_patch, gp_patch:
            with patch.object(views_module, 'datetime') as m_dt:
                m_dt.utcnow.return_value = datetime(2011, 3, 25, 23, 24)
                m_dt.today.return_value = datetime(2011, 3, 25, 23, 24)
                views = views_class(request)
                tmpl_vars = views.populaire_page()
        assert tmpl_vars['registration_closed']

    def test_populaire_page_event_started(
        self, views_class, pop_model, views_module, views_core_module,
    ):
        """populaire_page view has expected tmpl_vars when event has started
        """
        populaire = pop_model(
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
        request = get_current_request()
        request.matchdict['short_name'] = 'VicPop'
        gml_patch = patch.object(views_core_module, 'get_membership_link')
        gp_patch = patch.object(
            views_module, 'get_populaire', return_value=populaire)
        with gml_patch, gp_patch:
            with patch.object(views_module, 'datetime') as m_dt:
                m_dt.utcnow.return_value = datetime(2011, 3, 27, 17, 1)
                m_dt.today.return_value = datetime(2011, 3, 27, 17, 1)
                views = views_class(request)
                tmpl_vars = views.populaire_page()
        assert tmpl_vars['event_started']

    def test_populaire_page_event_not_started(
        self, views_class, pop_model, views_module, views_core_module,
    ):
        """populaire_page view has exp tmpl_vars when event has yet to start
        """
        populaire = pop_model(
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
        request = get_current_request()
        request.matchdict['short_name'] = 'VicPop'
        gml_patch = patch.object(views_core_module, 'get_membership_link')
        gp_patch = patch.object(
            views_module, 'get_populaire', return_value=populaire)
        with gml_patch, gp_patch:
            with patch.object(views_module, 'datetime') as m_dt:
                m_dt.utcnow.return_value = datetime(2011, 3, 27, 16, 59)
                m_dt.today.return_value = datetime(2011, 3, 27, 16, 59)
                views = views_class(request)
                tmpl_vars = views.populaire_page()
        assert not tmpl_vars['event_started']

    def test_populaire_page_past_event(
        self, views_class, pop_model, views_module, views_core_module,
    ):
        """populaire_page view calls _moved_on_page for event >7 days ago
        """
        populaire = pop_model(
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
        request = get_current_request()
        request.matchdict['short_name'] = 'VicPop'
        gml_patch = patch.object(views_core_module, 'get_membership_link')
        gp_patch = patch.object(
            views_module, 'get_populaire', return_value=populaire)
        with gml_patch, gp_patch:
            with patch.object(views_module, 'datetime') as m_dt:
                m_dt.today.return_value = datetime(2011, 4, 7, 15, 52)
                views = views_class(request)
                views._moved_on_page = MagicMock(
                    '_moved_on', return_value='moved-on body')
                resp = views.populaire_page()
        assert resp.body == b'moved-on body'

    def test_populaire_moved_on_page(
        self, views_class, pop_model, views_module, views_core_module,
    ):
        """_moved_on_page calls render with expected args
        """
        populaire = pop_model(
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
        request = get_current_request()
        request.matchdict['short_name'] = 'VicPop'
        gml_patch = patch.object(views_core_module, 'get_membership_link')
        gml_pv_patch = patch.object(
            views_module, 'get_membership_link',
            return_value='https://example.com/membership_link')
        gp_patch = patch.object(
            views_module, 'get_populaire', return_value=populaire)
        grl_patch = patch.object(
            views_module, 'get_results_link',
            return_value='https://example.com/browse/randonnees')
        with gml_patch, gml_pv_patch, gp_patch, grl_patch:
            with patch.object(views_module, 'render') as m_render:
                views = views_class(request)
                views._moved_on_page()
        tmpl_name = m_render.call_args[0][0]
        tmpl_vars = m_render.call_args[0][1]
        kwargs = m_render.call_args[1]
        assert tmpl_name == 'moved-on.mako'
        assert tmpl_vars['active_tab'] == 'populaires'
        assert 'populaires' in tmpl_vars
        assert 'populaires' in tmpl_vars
        assert tmpl_vars['event'] == 'VicPop 27-Mar-2011'
        expected = 'https://example.com/browse/randonnees'
        assert tmpl_vars['results_link'] == expected
        assert kwargs['request'] == request


@pytest.mark.usefixtures(
    'entry', 'pop_model', 'pop_rider_model', 'views_module', 'db_session',
    'pyramid_config',
)
class TestPopulaireEntry(object):
    """Unit tests for populaire pre-registration form handler & views.

    *TODO*: Add integrations tests:

      * Distance radio buttons only rendered for multi-distance events
      * Valid pre-registration renders confirmation message
      * Duplicate pre-registration renders error message
    """
    def test_redirect_url(self, entry, pyramid_config):
        """_redirect_url returns expected populaire page URL
        """
        pyramid_config.add_route('populaire', '/populaires/{short_name}')
        url = entry._redirect_url('VicPop')
        assert url == 'http://example.com/populaires/VicPop'

    def test_get_bind_data(self, pop_model, views_module, entry):
        """get_bind_data returns expected data dict for multi-distance event
        """
        populaire = pop_model(
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
        request = get_current_request()
        request.matchdict['short_name'] = 'VicPop'
        gp_patch = patch.object(
            views_module, 'get_populaire', return_value=populaire)
        with gp_patch:
            data = entry.get_bind_data()
        assert data['distances'] == [(50, '50 km'), (100, '100 km')]
        assert data['include_distance']

    def test_get_bind_data_exclude_distance(
        self, entry, pop_model, views_module,
    ):
        """get_bind_data returns expected data dict for single distance event
        """
        populaire = pop_model(
            event_name="New Year's Populaire",
            short_name='NewYearsPop',
            distance='60 km',
            date_time=datetime(2013, 1, 1, 10, 0),
            start_locn='Kelseys Family Restaurant, 325 Burnside Rd W, Victoria',
            organizer_email='mcroy@example.com',
            registration_end=datetime(2012, 12, 31, 17, 0),
            entry_form_url='http://www.randonneurs.bc.ca/organize/eventform.pdf',
        )
        request = get_current_request()
        request.matchdict['short_name'] = 'VicPop'
        gp_patch = patch.object(
            views_module, 'get_populaire', return_value=populaire)
        with gp_patch:
            data = entry.get_bind_data()
        assert data['distances'] == [(60, '60 km')]
        assert not data['include_distance']

    def test_show(
        self, entry, pop_model, views_module, db_session, pyramid_config,
    ):
        """show returns expected template variables
        """
        pyramid_config.add_route('populaire', '/populaires/{short_name}')
        populaire = pop_model(
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
        db_session.add(populaire)
        request = get_current_request()
        request.matchdict['short_name'] = 'VicPop'
        gml_patch = patch.object(
            views_module, 'get_membership_link',
            return_value='https://example.com/membership_link')
        with gml_patch:
            tmpl_vars = entry.show(MagicMock(name='form'))
        assert tmpl_vars['active_tab'] == 'populaires'
        assert 'brevets' in tmpl_vars
        assert 'populaires' in tmpl_vars
        assert tmpl_vars['populaire'] == populaire
        expected = 'https://example.com/membership_link'
        assert tmpl_vars['membership_link'] == expected
        expected = 'http://example.com/populaires/VicPop'
        assert tmpl_vars['cancel_url'] == expected

    @pytest.mark.parametrize("first_name, last_name", [
        ('Tom', 'Disckson'),  # ASCII
        (u'Étienne', u'«küßî»'),  # 1-byte Unicode
        (u'Étienne', u'“ЌύБЇ”'),  # 2-byte Unicode
    ])
    def test_register_success_duplicate_rider(
        self, first_name, last_name, entry, pop_model, pop_rider_model,
        db_session, pyramid_config,
    ):
        """valid entry w/ duplicate rider name & email sets expected flash msgs
        """
        pyramid_config.add_route('populaire', '/populaires/{short_name}')
        populaire = pop_model(
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
        rider = pop_rider_model(
            email='tom@example.com',
            first_name=first_name,
            last_name=last_name,
            distance=100,
            comment='',
        )
        populaire.riders.append(rider)
        db_session.add_all((populaire, rider))
        request = get_current_request()
        request.matchdict['short_name'] = 'VicPop'
        url = entry.register_success({
            'email': 'tom@example.com',
            'first_name': first_name,
            'last_name': last_name,
            'populaire': populaire.id,
        })
        assert url.location == 'http://example.com/populaires/VicPop'
        expected = [
            'duplicate', ' '.join((first_name, last_name)), 'tom@example.com']
        assert request.session.pop_flash() == expected

    @pytest.mark.xfail(reason='google spreadsheet disabled')
    @pytest.mark.parametrize("first_name, last_name", [
        ('Tom', 'Disckson'),  # ASCII
        (u'Étienne', u'«küßî»'),  # 1-byte Unicode
        (u'Étienne', u'“ЌύБЇ”'),  # 2-byte Unicode
    ])
    def test_register_success_new_rider(
        self, first_name, last_name, entry, pop_model, pop_rider_model,
        email_address_model, views_module, db_session, pyramid_config,
    ):
        """valid entry for new rider adds rider to db & sets exp flash msgs
        """
        pyramid_config.add_route('populaire', '/populaires/{short_name}')
        from_randopony = email_address_model(
            key='from_randopony', email='randopony@example.com')
        populaire = pop_model(
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
        db_session.add_all((from_randopony, populaire))
        request = get_current_request()
        request.matchdict['short_name'] = 'VicPop'
        gm_patch = patch.object(views_module, 'get_mailer')
        ugs_patch = patch.object(views_module, 'update_google_spreadsheet')
        r_msg_patch = patch.object(entry, '_rider_message')
        o_msg_patch = patch.object(entry, '_organizer_message')
        with gm_patch, ugs_patch, r_msg_patch, o_msg_patch:
            url = entry.register_success({
                'email': 'fred@example.com',
                'first_name': first_name,
                'last_name': last_name,
                'comment': 'Sunshine Man',
                'distance': 100,
                'populaire': populaire.id,
            })
        rider = db_session.query(pop_rider_model).first()
        assert rider.email == 'fred@example.com'
        expected = u'{} "Sunshine Man" {}'.format(first_name, last_name)
        assert rider.full_name == expected
        assert rider.lowercase_last_name == last_name.lower()
        assert rider.distance == 100
        assert url.location == 'http://example.com/populaires/VicPop'
        assert request.session.pop_flash() == ['success', 'fred@example.com']

    @pytest.mark.xfail(reason='google spreadsheet disabled')
    def test_register_success_single_distance(
        self, entry, pop_model, pop_rider_model, email_address_model,
        views_module, db_session, pyramid_config,
    ):
        """valid entry for single dstance populaire sets distance correctly
        """
        pyramid_config.add_route('populaire', '/populaires/{short_name}')
        from_randopony = email_address_model(
            key='from_randopony', email='randopony@example.com')
        populaire = pop_model(
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
        db_session.add_all((from_randopony, populaire))
        request = get_current_request()
        request.matchdict['short_name'] = 'NewYearsPop'
        gm_patch = patch.object(views_module, 'get_mailer')
        ugs_patch = patch.object(views_module, 'update_google_spreadsheet')
        r_msg_patch = patch.object(entry, '_rider_message')
        o_msg_patch = patch.object(entry, '_organizer_message')
        with gm_patch, ugs_patch, r_msg_patch, o_msg_patch:
            entry.register_success({
                'email': 'fred@example.com',
                'first_name': 'Fred',
                'last_name': 'Dickson',
                'comment': 'Sunshine Man',
                'populaire': populaire.id,
            })
        rider = db_session.query(pop_rider_model).first()
        assert rider.distance == '60'

    @pytest.mark.xfail(reason='google spreadsheet disabled')
    def test_register_success_sends_2_emails(
        self, entry, pop_model, pop_rider_model, email_address_model,
        views_module, db_session, pyramid_config,
    ):
        """successful entry sends emails to rider and organizer
        """
        pyramid_config.add_route('populaire', '/populaires/{short_name}')
        from_randopony = email_address_model(
            key='from_randopony', email='randopony@example.com')
        populaire = pop_model(
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
        db_session.add_all((from_randopony, populaire))
        request = get_current_request()
        request.matchdict['short_name'] = 'NewYearsPop'
        ugs_patch = patch.object(views_module, 'update_google_spreadsheet')
        r_msg_patch = patch.object(entry, '_rider_message')
        o_msg_patch = patch.object(entry, '_organizer_message')
        with ugs_patch, r_msg_patch, o_msg_patch:
            m_mailer = MagicMock(name='mailer')
            gm_patch = patch.object(
                views_module, 'get_mailer', return_value=m_mailer)
            with gm_patch:
                entry.register_success({
                    'email': 'fred@example.com',
                    'first_name': 'Fred',
                    'last_name': 'Dickson',
                    'comment': 'Sunshine Man',
                })
        assert m_mailer.send.call_count == 2

    def test_rider_email_message(
        self, entry, pop_model, pop_rider_model, email_address_model,
        db_session, pyramid_config,
    ):
        """registration confirmation email to rider has expected content
        """
        pyramid_config.add_route('populaire', '/populaires/{short_name}')
        from_randopony = email_address_model(
            key='from_randopony', email='randopony@example.com')
        populaire = pop_model(
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
        rider = pop_rider_model(
            email='fred@example.com',
            first_name='Fred',
            last_name='Dickson',
            distance=60,
            comment='',
        )
        db_session.add_all((from_randopony, populaire))
        request = get_current_request()
        request.matchdict['short_name'] = 'NewYearsPop'
        msg = entry._rider_message(populaire, rider)
        assert msg.subject == 'Pre-registration Confirmation for NewYearsPop'
        assert msg.sender == from_randopony.email
        assert msg.recipients == ['fred@example.com']
        assert msg.extra_headers['Sender'] == from_randopony.email
        assert msg.extra_headers['Reply-To'] == populaire.organizer_email
        assert 'NewYearsPop on Tue 01-Jan-2013' in msg.body
        assert 'list at <http://example.com/populaires/NewYearsPop>' in msg.body
        assert 'web site <http://www.randonneurs.bc.ca/organize/eventform.pdf>, read it' in msg.body

    @pytest.mark.parametrize("first_name, last_name", [
        ('Jerry', 'Harrison'),  # ASCII
        (u'Étienne', u'«küßî»'),  # 1-byte Unicode
        (u'Étienne', u'“ЌύБЇ”'),  # 2-byte Unicode
    ])
    def test_organizer_email_message_single_distance(
        self, first_name, last_name, entry, pop_model, pop_rider_model,
        email_address_model, views_module, db_session, pyramid_config,
    ):
        """reg notify email to org for single dist event has expected content
        """
        pyramid_config.add_route('populaire', '/populaires/{short_name}')
        pyramid_config.add_route(
            'populaire.rider_emails',
            '/populaires/{short_name}/rider_emails/{uuid}')
        from_randopony = email_address_model(
            key='from_randopony', email='randopony@example.com')
        admin_email = email_address_model(
            key='admin_email', email='tom@example.com')
        populaire = pop_model(
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
        rider = pop_rider_model(
            email='fred@example.com',
            first_name=first_name,
            last_name=last_name,
            distance=60,
            comment='Sunshine Man',
        )
        db_session.add_all((from_randopony, admin_email, populaire))
        request = get_current_request()
        request.matchdict['short_name'] = 'NewYearsPop'
        with patch.object(views_module, 'render') as m_render:
            msg = entry._organizer_message(populaire, rider)
        expected = (
            u'{} {} has Pre-registered for the NewYearsPop'
            .format(first_name, last_name))
        assert msg.subject == expected
        assert msg.sender == from_randopony.email
        assert msg.recipients == [populaire.organizer_email]
        assert msg.body == m_render()

    def test_organizer_email_message_multi_organizer(
        self, entry, pop_model, pop_rider_model, email_address_model,
        views_module, db_session, pyramid_config,
    ):
        """reg notify email to orgs for multi-org event has expected content
        """
        pyramid_config.add_route('populaire', '/populaires/{short_name}')
        pyramid_config.add_route(
            'populaire.rider_emails',
            '/populaires/{short_name}/rider_emails/{uuid}')
        from_randopony = email_address_model(
            key='from_randopony', email='randopony@example.com')
        admin_email = email_address_model(
            key='admin_email', email='tom@example.com')
        populaire = pop_model(
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
        rider = pop_rider_model(
            email='fred@example.com',
            first_name='Fred',
            last_name='Dickson',
            distance=100,
            comment='Sunshine Man',
        )
        db_session.add_all((from_randopony, admin_email, populaire))
        request = get_current_request()
        request.matchdict['short_name'] = 'NewYearsPop'
        with patch.object(views_module, 'render') as m_render:
            msg = entry._organizer_message(populaire, rider)
        assert msg.recipients == ['mjansson@example.com', 'mcroy@example.com']

    @pytest.mark.xfail(reason='google spreadsheet disabled')
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
        assert mock_task.delay.called

    def test_failure(
        self, entry, pop_model, email_address_model,
        views_module, db_session, pyramid_config,
    ):
        """populaire entry form validation failure returns expected tmpl_vars
        """
        pyramid_config.add_route('populaire', '/populaires/{short_name}')
        populaire = pop_model(
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
        db_session.add(populaire)
        populare_id = str(populaire)
        request = get_current_request()
        request.matchdict['short_name'] = 'VicPop'
        tmpl_vars = entry.failure(MagicMock(name='ValidationError'))
        assert tmpl_vars['active_tab'] == 'populaires'
        assert 'brevets' in tmpl_vars
        assert 'populaires' in tmpl_vars
        assert str(tmpl_vars['populaire']) == populare_id
        assert tmpl_vars['cancel_url'] == 'http://example.com/populaires/VicPop'
