# -*- coding: utf-8 -*-
"""RandoPony populaire data model.
"""
from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    Text,
    )
from .core import EventMixin
from .meta import Base


class Populaire(EventMixin, Base):
    """Populaire event.
    """
    __tablename__ = 'populaires'
    event_name = Column(Text)
    short_name = Column(Text)
    distance = Column(Text)
    start_locn = Column(Text)
    start_map_url = Column(Text)
    entry_form_url = Column(Text)
    entry_form_url_label = Column(Text)

    def __init__(self, event_name, short_name, distance, date_time,
        start_locn, organizer_email, registration_end, entry_form_url,
        entry_form_url_label):
        self.event_name = event_name
        self.short_name = short_name
        self.distance = distance
        self.date_time = date_time
        self.start_locn = start_locn
        self.organizer_email = organizer_email
        self.registration_end = registration_end
        self.entry_form_url = entry_form_url
        self.entry_form_url_label = entry_form_url_label
        self.start_map_url = (
            'https://maps.google.com/maps?q={}'
            .format('+'.join(self.start_locn.split())))

    def __str__(self):
        return '{0.short_name} {0.date_time:%d%b%Y}'.format(self)

    def __repr__(self):
        return '<Populaire({})>'.format(self)
