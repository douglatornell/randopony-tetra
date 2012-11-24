# -*- coding: utf-8 -*-
"""Unit tests for RandoPony data model.
"""
from datetime import datetime
import unittest
from unittest.mock import patch
from pyramid import testing
from sqlalchemy import create_engine
import transaction
from ..models import (
    Base,
    DBSession,
    )


class TestAdministrator(unittest.TestCase):
    """Unit tests for Administrator data model.
    """
    def _get_target_class(self):
        from ..models import Administrator
        return Administrator

    def _make_one(self, *args, **kwargs):
        return self._get_target_class()(*args, **kwargs)

    def test_str(self):
        """Administrator model string rep is persona email address
        """
        admin = self._make_one('tom@example.com')
        self.assertEqual(str(admin), 'tom@example.com')

    def test_repr(self):
        """Administrator model string rep is persona email address
        """
        admin = self._make_one('tom@example.com')
        self.assertEqual(repr(admin), '<Administrator(tom@example.com)>')


class TestBrevet(unittest.TestCase):
    """Unit tests for Brevet data model."""
    def _get_target_class(self):
        from ..models import Brevet
        return Brevet

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

    def test_str(self):
        """Brevet model string rep is like 'LM200 11Nov2012'."""
        brevet = self._make_one(region='LM', distance=200,
            date_time=datetime(2012, 11, 11, 7, 0, 0), route_name='11th Hour',
            start_locn='Bean Around the World Coffee, Lonsdale Quay, '
                       '123 Carrie Cates Ct, North Vancouver',
            organizer_email='tracy@example.com')
        self.assertEqual(str(brevet), 'LM200 11Nov2012')

    def test_epr(self):
        """Brevet model string rep is like 'LM200 11Nov2012'."""
        brevet = self._make_one(region='LM', distance=200,
            date_time=datetime(2012, 11, 11, 7, 0, 0), route_name='11th Hour',
            start_locn='Bean Around the World Coffee, Lonsdale Quay, '
                       '123 Carrie Cates Ct, North Vancouver',
            organizer_email='tracy@example.com')
        self.assertEqual(repr(brevet), '<Brevet(LM200 11Nov2012)>')

    def test_default_registration_end(self):
        """Brevet end of registration default to noon before event
        """
        brevet = self._make_one(
            region='LM',
            distance=200,
            date_time=datetime(2012, 11, 11, 7, 0, 0), route_name='11th Hour',
            start_locn='Bean Around the World Coffee, Lonsdale Quay, '
                       '123 Carrie Cates Ct, North Vancouver',
            organizer_email='tracy@example.com',
            )
        self.assertEqual(
            brevet.registration_end, datetime(2012, 11, 10, 12, 0, 0))

    def test_default_start_map_url(self):
        """Brevet start locn map URL defaults based on start_locn value
        """
        brevet = self._make_one(
            region='LM',
            distance=200,
            date_time=datetime(2012, 11, 11, 7, 0, 0), route_name='11th Hour',
            start_locn='Bean Around the World Coffee, Lonsdale Quay, '
                       '123 Carrie Cates Ct, North Vancouver',
            organizer_email='tracy@example.com',
            )
        self.assertEqual(
            brevet.start_map_url,
            'https://maps.google.com/maps'
            '?q=Bean+Around+the+World+Coffee,+Lonsdale+Quay,'
            '+123+Carrie+Cates+Ct,+North+Vancouver')

    def test_get_current_future_brevet(self):
        """get_current class method returns brevet in future
        """
        from .. import models
        brevet = self._make_one(
            region='LM',
            distance=200,
            date_time=datetime(2012, 11, 11, 7, 0, 0), route_name='11th Hour',
            start_locn='Bean Around the World Coffee, Lonsdale Quay, '
                       '123 Carrie Cates Ct, North Vancouver',
            organizer_email='tracy@example.com',
            )
        with transaction.manager:
            DBSession.add(brevet)
        Brev = self._get_target_class()
        with patch.object(models, 'datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2012, 11, 1, 7, 36, 42)
            brevets = Brev.get_current()
        self.assertEqual(
            brevets.first().date_time, datetime(2012, 11, 11, 7, 0, 0))

    def test_get_current_recent_brevet(self):
        """get_current class method returns brevet in within last 7 days
        """
        from .. import models
        brevet = self._make_one(
            region='LM',
            distance=200,
            date_time=datetime(2012, 11, 11, 7, 0, 0), route_name='11th Hour',
            start_locn='Bean Around the World Coffee, Lonsdale Quay, '
                       '123 Carrie Cates Ct, North Vancouver',
            organizer_email='tracy@example.com',
            )
        with transaction.manager:
            DBSession.add(brevet)
        Brev = self._get_target_class()
        with patch.object(models, 'datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2012, 11, 12, 8, 33, 42)
            brevets = Brev.get_current()
        self.assertEqual(
            brevets.first().date_time, datetime(2012, 11, 11, 7, 0, 0))

    def test_get_current_exclude_old_brevet(self):
        """get_current class method excludes brevet longer ago than 7 days
        """
        from .. import models
        brevet = self._make_one(
            region='LM',
            distance=200,
            date_time=datetime(2012, 11, 11, 7, 0, 0), route_name='11th Hour',
            start_locn='Bean Around the World Coffee, Lonsdale Quay, '
                       '123 Carrie Cates Ct, North Vancouver',
            organizer_email='tracy@example.com',
            )
        with transaction.manager:
            DBSession.add(brevet)
        Brev = self._get_target_class()
        with patch.object(models, 'datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2012, 11, 19, 8, 45, 42)
            brevets = Brev.get_current()
        self.assertEqual(brevets.all(), [])
