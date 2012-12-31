# -*- coding: utf-8 -*-
"""Tests for RandoPony public site core views and functionality.
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
from sqlalchemy import create_engine
import transaction
from ..models.meta import (
    Base,
    DBSession,
    )


class TestSiteViews(unittest.TestCase):
    """Unit tests for public site views.
    """
    def _get_target_class(self):
        from ..views.site.core import SiteViews
        return SiteViews

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

    def test_init(self):
        """SiteViews constructor sets request & tmpl_vars attrs
        """
        request = testing.DummyRequest()
        views = self._make_one(request)
        self.assertEqual(views.request, request)
        self.assertIn('brevets', views.tmpl_vars)
        self.assertIn('populaires', views.tmpl_vars)

    def test_home(self):
        """home view has home tab set as active tab
        """
        request = testing.DummyRequest()
        views = self._make_one(request)
        tmpl_vars = views.home()
        self.assertEqual(tmpl_vars['active_tab'], 'home')

    def test_organizer_info(self):
        """organizer_info view has expected tmpl_vars
        """
        from ..models import EmailAddress
        email = EmailAddress(key='admin_email', email='tom@example.com')
        with transaction.manager:
            DBSession.add(email)
        request = testing.DummyRequest()
        views = self._make_one(request)
        tmpl_vars = views.organizer_info()
        self.assertEqual(tmpl_vars['active_tab'], 'organizer-info')
        self.assertEqual(tmpl_vars['admin_email'], 'tom@example.com')

    def test_about(self):
        """about view has about tab set as active tab
        """
        request = testing.DummyRequest()
        views = self._make_one(request)
        tmpl_vars = views.about()
        self.assertEqual(tmpl_vars['active_tab'], 'about')

    def test_notfound(self):
        """notfound view has no active tab and 404 status
        """
        request = testing.DummyRequest()
        views = self._make_one(request)
        tmpl_vars = views.notfound()
        self.assertIsNone(tmpl_vars['active_tab'])
        self.assertEqual(request.response.status, '404 Not Found')

    def test_region_list(self):
        """region_list view has expected tmpl_vars
        """
        from ..models import (
            Brevet,
            EmailAddress,
            )
        email = EmailAddress(key='admin_email', email='tom@example.com')
        with transaction.manager:
            DBSession.add(email)
        request = testing.DummyRequest()
        views = self._make_one(request)
        tmpl_vars = views.region_list()
        self.assertEqual(tmpl_vars['active_tab'], 'brevets')
        self.assertEqual(tmpl_vars['regions'], Brevet.REGIONS)
        self.assertEqual(
            tmpl_vars['region_brevets'].keys(), Brevet.REGIONS.keys())
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
        with transaction.manager:
            DBSession.add(brevet)
            DBSession.add(email)
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
        with transaction.manager:
            DBSession.add(brevet)
            DBSession.add(email)
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


class TestPopulaireViews(unittest.TestCase):
    """Unit tests for public site populaire views.
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
        email = EmailAddress(key='admin_email', email='tom@example.com')
        with transaction.manager:
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
        populare_id = str(populaire)
        with transaction.manager:
            DBSession.add(populaire)
        request = testing.DummyRequest()
        request.matchdict['short_name'] = 'VicPop'
        views = self._make_one(request)
        with patch.object(pop_module, 'datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = datetime(2011, 3, 22, 23, 18)
            tmpl_vars = views.populaire_page()
        self.assertEqual(tmpl_vars['active_tab'], 'populaires')
        self.assertEqual(str(tmpl_vars['populaire']), populare_id)
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
        with transaction.manager:
            DBSession.add(populaire)
        request = testing.DummyRequest()
        request.matchdict['short_name'] = 'VicPop'
        views = self._make_one(request)
        with patch.object(pop_module, 'datetime') as mock_datetime:
            mock_datetime.utcnow.return_value = datetime(2011, 3, 25, 23, 24)
            tmpl_vars = views.populaire_page()
        self.assertTrue(tmpl_vars['registration_closed'])


class TestPopulaireEntry(unittest.TestCase):
    """Unit tests for populaire pre-registration form handler & views.
    """
    def _get_target_class(self):
        from ..views.site.populaire import PopulaireEntry
        return PopulaireEntry

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

    def test_redirect_url(self):
        """_redirect_url returns expected populaire page URL
        """
        self.config.add_route('populaire', '/populaires/{short_name}')
        request = testing.DummyRequest()
        entry = self._make_one(request)
        url = entry._redirect_url('VicPop')
        self.assertEqual(url, 'http://example.com/populaires/VicPop')

    def test_get_bind_data(self):
        """get_bind_data returns expected data dict for multi-distance event
        """
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
        with transaction.manager:
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
        self.config.add_route('populaire', '/populaires/{short_name}')
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
        with transaction.manager:
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
        with transaction.manager:
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
        rider = PopulaireRider(
            email='tom@example.com',
            first_name='Tom',
            last_name='Dickson',
            distance=100,
            comment='',
            )
        populaire.riders.append(rider)
        with transaction.manager:
            DBSession.add(populaire)
            DBSession.add(rider)
            populaire_id = populaire.id
        request = testing.DummyRequest()
        request.matchdict['short_name'] = 'VicPop'
        entry = self._make_one(request)
        url = entry.register_success({
            'email': 'tom@example.com',
            'first_name': 'Tom',
            'last_name': 'Dickson',
            'populaire': populaire_id,
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
        with transaction.manager:
            DBSession.add(populaire)
            populaire_id = populaire.id
        request = testing.DummyRequest()
        request.matchdict['short_name'] = 'VicPop'
        entry = self._make_one(request)
        url = entry.register_success({
            'email': 'fred@example.com',
            'first_name': 'Fred',
            'last_name': 'Dickson',
            'comment': 'Sunshine Man',
            'distance': 100,
            'populaire': populaire_id,
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
        self.config.add_route('populaire', '/populaires/{short_name}')
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
        with transaction.manager:
            DBSession.add(populaire)
            populaire_id = populaire.id
        request = testing.DummyRequest()
        request.matchdict['short_name'] = 'NewYearsPop'
        entry = self._make_one(request)
        entry.register_success({
            'email': 'fred@example.com',
            'first_name': 'Fred',
            'last_name': 'Dickson',
            'comment': 'Sunshine Man',
            'populaire': populaire_id,
            })
        rider = DBSession.query(PopulaireRider).first()
        self.assertEqual(rider.distance, 60)

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
        with transaction.manager:
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
