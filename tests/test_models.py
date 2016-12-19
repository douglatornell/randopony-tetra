"""Unit tests for RandoPony data model.
"""
from datetime import datetime
import unittest
from unittest.mock import patch

from pyramid import testing
import pytest
from sqlalchemy import create_engine

from randopony.models.meta import (
    Base,
    DBSession,
)


class TestAdministrator(unittest.TestCase):
    """Unit tests for Administrator data model.
    """
    def _get_target_class(self):
        from randopony.models import Administrator
        return Administrator

    def _make_one(self, *args, **kwargs):
        return self._get_target_class()(*args, **kwargs)

    def test_str(self):
        """Administrator model string rep is persona email address
        """
        admin = self._make_one('tom@example.com')
        self.assertEqual(str(admin), 'tom@example.com')

    def test_repr(self):
        admin = self._make_one('tom@example.com')
        self.assertEqual(repr(admin), '<Administrator(tom@example.com)>')


class TestEmailAddress(unittest.TestCase):
    """Unit tests for EmailAddress data model.
    """
    def _get_target_class(self):
        from randopony.models import EmailAddress
        return EmailAddress

    def _make_one(self, *args, **kwargs):
        return self._get_target_class()(*args, **kwargs)

    def test_repr(self):
        email = self._make_one(key='webmaster', email='tom@example.com')
        self.assertEqual(
            repr(email), '<EmailAddress(webmaster=tom@example.com)>')


class TestLink(unittest.TestCase):
    """Unit tests for Link data model.
    """
    def _get_target_class(self):
        from randopony.models import Link
        return Link

    def _make_one(self, *args, **kwargs):
        return self._get_target_class()(*args, **kwargs)

    def test_repr(self):
        email = self._make_one(
            key='club_site', url='http://randonneurs.bc.ca')
        self.assertEqual(
            repr(email), '<Link(club_site=http://randonneurs.bc.ca)>')


class TestBrevet(unittest.TestCase):
    """Unit tests for Brevet data model.
    """
    def _get_target_class(self):
        from randopony.models import Brevet
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
        brevet = self._make_one(
            region='LM',
            distance=200,
            date_time=datetime(2012, 11, 11, 7, 0, 0),
            route_name='11th Hour',
            start_locn='Bean Around the World Coffee, Lonsdale Quay, '
                       '123 Carrie Cates Ct, North Vancouver',
            organizer_email='tracy@example.com')
        self.assertEqual(str(brevet), 'LM200 11Nov2012')

    def test_repr(self):
        """Brevet model repr is like '<Brevet(LM200 11Nov2012)>'.
        """
        brevet = self._make_one(
            region='LM',
            distance=200,
            date_time=datetime(2012, 11, 11, 7, 0, 0),
            route_name='11th Hour',
            start_locn='Bean Around the World Coffee, Lonsdale Quay, '
                       '123 Carrie Cates Ct, North Vancouver',
            organizer_email='tracy@example.com')
        self.assertEqual(repr(brevet), '<Brevet(LM200 11Nov2012)>')

    def test_registration_end(self):
        """Brevet end of registration specified
        """
        brevet = self._make_one(
            region='LM',
            distance=200,
            date_time=datetime(2012, 11, 11, 7, 0, 0),
            route_name='11th Hour',
            start_locn='Bean Around the World Coffee, Lonsdale Quay, '
                       '123 Carrie Cates Ct, North Vancouver',
            organizer_email='tracy@example.com',
            registration_end=datetime(2012, 11, 11, 7, 0, 0),
        )
        self.assertEqual(
            brevet.registration_end, datetime(2012, 11, 11, 7, 0, 0))

    def test_default_registration_end(self):
        """Brevet end of registration defaults to noon before event
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
        from randopony.models import core
        brevet = self._make_one(
            region='LM',
            distance=200,
            date_time=datetime(2012, 11, 11, 7, 0, 0), route_name='11th Hour',
            start_locn='Bean Around the World Coffee, Lonsdale Quay, '
                       '123 Carrie Cates Ct, North Vancouver',
            organizer_email='tracy@example.com',
        )
        DBSession.add(brevet)
        Brev = self._get_target_class()
        with patch.object(core, 'datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2012, 11, 1, 7, 36, 42)
            brevets = Brev.get_current()
        self.assertEqual(
            brevets.first().date_time, datetime(2012, 11, 11, 7, 0, 0))

    def test_get_current_recent_brevet(self):
        """get_current class method returns brevet in within last 7 days
        """
        from randopony.models import core
        brevet = self._make_one(
            region='LM',
            distance=200,
            date_time=datetime(2012, 11, 11, 7, 0, 0), route_name='11th Hour',
            start_locn='Bean Around the World Coffee, Lonsdale Quay, '
                       '123 Carrie Cates Ct, North Vancouver',
            organizer_email='tracy@example.com',
        )
        DBSession.add(brevet)
        Brev = self._get_target_class()
        with patch.object(core, 'datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2012, 11, 12, 8, 33, 42)
            brevets = Brev.get_current()
        self.assertEqual(
            brevets.first().date_time, datetime(2012, 11, 11, 7, 0, 0))

    def test_get_current_exclude_old_brevet(self):
        """get_current class method excludes brevet longer ago than 7 days
        """
        from randopony.models import core
        brevet = self._make_one(
            region='LM',
            distance=200,
            date_time=datetime(2012, 11, 11, 7, 0, 0), route_name='11th Hour',
            start_locn='Bean Around the World Coffee, Lonsdale Quay, '
                       '123 Carrie Cates Ct, North Vancouver',
            organizer_email='tracy@example.com',
        )
        DBSession.add(brevet)
        Brev = self._get_target_class()
        with patch.object(core, 'datetime') as mock_datetime:
            mock_datetime.today.return_value = datetime(2012, 11, 19, 8, 45, 42)
            brevets = Brev.get_current()
        self.assertEqual(brevets.all(), [])


class TestBrevetRider(object):
    """Unit tests for BrevetRider data model.
    """
    @pytest.mark.parametrize("first_name, last_name", [
        ('Tom', 'Dickson'),  # ASCII
        (u'Étienne', u'«küßî»'),  # 1-byte Unicode
        (u'Étienne', u'“ЌύБЇ”'),  # 2-byte Unicode
    ])
    def test_str(self, first_name, last_name, brevet_rider_model):
        """BrevetRider model string rep is first_name last_name
        """
        rider = brevet_rider_model(
            email='tom@example.com',
            first_name=first_name,
            last_name=last_name,
            comment='',
        )
        expected = '{} {}'.format(first_name, last_name)
        assert str(rider) == expected

    @pytest.mark.parametrize("first_name, last_name", [
        ('Tom', 'Dickson'),  # ASCII
        (u'Étienne', u'«küßî»'),  # 1-byte Unicode
        (u'Étienne', u'“ЌύБЇ”'),  # 2-byte Unicode
    ])
    def test_repr(self, last_name, first_name, brevet_rider_model):
        """BrevetRider model repr is <Rider(first_name last_name)>
        """
        rider = brevet_rider_model(
            email='tom@example.com',
            first_name=first_name,
            last_name=last_name,
            comment='',
        )
        expected = '<Rider({} {})>'.format(first_name, last_name)
        assert repr(rider) == expected

    @pytest.mark.parametrize("first_name, last_name", [
        ('Tom', 'Dickson'),  # ASCII
        (u'Étienne', u'«küßî»'),  # 1-byte Unicode
        (u'Étienne', u'“ЌύБЇ”'),  # 2-byte Unicode
    ])
    def test_full_name_wo_comment(
        self, first_name, last_name, brevet_rider_model,
    ):
        """BrevetRider full_name w/o comment is first_name last_name
        """
        rider = brevet_rider_model(
            email='tom@example.com',
            first_name=first_name,
            last_name=last_name,
            comment='',
        )
        expected = u'{} {}'.format(first_name, last_name)
        assert rider.full_name == expected

    @pytest.mark.parametrize("first_name, last_name", [
        ('Tom', 'Dickson'),  # ASCII
        (u'Étienne', u'«küßî»'),  # 1-byte Unicode
        (u'Étienne', u'“ЌύБЇ”'),  # 2-byte Unicode
    ])
    def test_full_name_w_comment(
        self, first_name, last_name, brevet_rider_model,
    ):
        """BrevetRider full_name w comment is first_name "comment" last_name
        """
        rider = brevet_rider_model(
            email='tom@example.com',
            first_name=first_name,
            last_name=last_name,
            comment='hoping for sun',
        )
        expected = u'{} "hoping for sun" {}'.format(first_name, last_name)
        assert rider.full_name == expected


class TestPopulaire(unittest.TestCase):
    """Unit tests for Populaire data model.
    """
    def _get_target_class(self):
        from randopony.models import Populaire
        return Populaire

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
        """Populaire model string repr is like 'VicPop 24Mar2011'.
        """
        populaire = self._make_one(
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
        self.assertEqual(str(populaire), 'VicPop')

    def test_repr(self):
        """Populaire model repr is like '<Populaire(VicPop 27Mar2011)>'.
        """
        populaire = self._make_one(
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
        self.assertEqual(repr(populaire), '<Populaire(VicPop)>')

    def test_entry_form_url(self):
        """Populaire entry form URL specified
        """
        populaire = self._make_one(
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
        self.assertEqual(
            populaire.entry_form_url,
            'http://www.randonneurs.bc.ca/VicPop/VicPop11_registration.pdf')

    def test_default_entry_form_url(self):
        """Populaire entry form URL defaults to standard club form
        """
        from randopony.models import Link
        entry_form_link = Link(
            key='entry_form',
            url='http://www.randonneurs.bc.ca/organize/eventform.pdf',
        )
        DBSession.add(entry_form_link)
        populaire = self._make_one(
            event_name='Victoria Populaire',
            short_name='VicPop',
            distance='50 km, 100 km',
            date_time=datetime(2011, 3, 27, 10, 0),
            start_locn='University of Victoria, Parking Lot #2 '
                       '(Gabriola Road, near McKinnon Gym)',
            organizer_email='mjansson@example.com',
            registration_end=datetime(2011, 3, 24, 12, 0),
        )
        self.assertEqual(
            populaire.entry_form_url,
            'http://www.randonneurs.bc.ca/organize/eventform.pdf')


class TestPopulaireRider(object):
    """Unit tests for PopulaireRider data model.
    """
    @pytest.mark.parametrize("first_name, last_name", [
        ('Tom', 'Dickson'),  # ASCII
        (u'Étienne', u'«küßî»'),  # 1-byte Unicode
        (u'Étienne', u'“ЌύБЇ”'),  # 2-byte Unicode
    ])
    def test_str(self, first_name, last_name, pop_rider_model):
        """PopulaireRider model string rep is first_name last_name
        """
        rider = pop_rider_model(
            email='tom@example.com',
            first_name=first_name,
            last_name=last_name,
            distance='60',
            comment='',
        )
        expected = '{} {}'.format(first_name, last_name)
        assert str(rider) == expected

    @pytest.mark.parametrize("first_name, last_name", [
        ('Tom', 'Dickson'),  # ASCII
        (u'Étienne', u'«küßî»'),  # 1-byte Unicode
        (u'Étienne', u'“ЌύБЇ”'),  # 2-byte Unicode
    ])
    def test_repr(self, first_name, last_name, pop_rider_model):
        """PopulaireRider model repr is <Rider(first_name last_name)>
        """
        rider = pop_rider_model(
            email='tom@example.com',
            first_name=first_name,
            last_name=last_name,
            distance='60',
            comment='',
        )
        expected = '<Rider({} {})>'.format(first_name, last_name)
        assert repr(rider) == expected

    @pytest.mark.parametrize("first_name, last_name", [
    ('Tom', 'Dickson'),  # ASCII
    (u'Étienne', u'«küßî»'),  # 1-byte Unicode
    (u'Étienne', u'“ЌύБЇ”'),  # 2-byte Unicode
    ])
    def test_full_name_wo_comment(
        self, first_name, last_name, pop_rider_model,
    ):
        """PopulaireRider full_name w/o comment is first_name last_name
        """
        rider = pop_rider_model(
            email='tom@example.com',
            first_name=first_name,
            last_name=last_name,
            distance='60',
            comment='',
        )
        expected = u'{} {}'.format(first_name, last_name)
        assert rider.full_name == expected


    @pytest.mark.parametrize("first_name, last_name", [
    ('Tom', 'Dickson'),  # ASCII
    (u'Étienne', u'«küßî»'),  # 1-byte Unicode
    (u'Étienne', u'“ЌύБЇ”'),  # 2-byte Unicode
    ])
    def test_full_name_w_comment(
        self, first_name, last_name, pop_rider_model,
    ):
        """PopulaireRider full_name w comment is first_name "comment" last_name
        """
        rider = pop_rider_model(
            email='tom@example.com',
            first_name=first_name,
            last_name=last_name,
            distance='60',
            comment='hoping for sun',
        )
        expected = u'{} "hoping for sun" {}'.format(first_name, last_name)
        assert rider.full_name == expected
