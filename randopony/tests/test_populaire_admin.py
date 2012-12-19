# -*- coding: utf-8 -*-
"""Tests for RandoPony populaire admin views and functionality.
"""
from datetime import datetime
import unittest
try:
    from unittest.mock import MagicMock
except ImportError:
    from mock import MagicMock
from pyramid import testing
from sqlalchemy import create_engine
import transaction
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
        with transaction.manager:
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
            populaire_id = str(populaire)
            DBSession.add(populaire)
        request = testing.DummyRequest()
        request.matchdict['item'] = populaire_id
        tmpl_vars = populaire_details(request)
        self.assertTrue(tmpl_vars['logout_btn'])
        self.assertEqual(str(tmpl_vars['populaire']), populaire_id)


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
        with transaction.manager:
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
        with transaction.manager:
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
        with transaction.manager:
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
