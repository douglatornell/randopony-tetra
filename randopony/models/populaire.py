# -*- coding: utf-8 -*-
"""RandoPony populaire data model.
"""
import colander
from deform.widget import (
    DateTimeInputWidget,
    HiddenWidget,
    TextInputWidget,
    )
from pyramid_deform import CSRFSchema
from sqlalchemy import (
    Column,
    Text,
    )
from .core import EventMixin
from .meta import Base


class Populaire(EventMixin, Base):
    """Populaire event.
    """
    __tablename__ = 'populaires'

    event_name = Column(Text)
    short_name = Column(Text, index=True)
    distance = Column(Text)
    start_locn = Column(Text)
    start_map_url = Column(Text)
    entry_form_url = Column(Text)

    def __init__(self, event_name, short_name, distance, date_time,
        start_locn, organizer_email, registration_end, entry_form_url):
        self.event_name = event_name
        self.short_name = short_name
        self.distance = distance
        self.date_time = date_time
        self.start_locn = start_locn
        self.organizer_email = organizer_email
        self.registration_end = registration_end
        self.entry_form_url = entry_form_url
        self.start_map_url = (
            'https://maps.google.com/maps?q={}'
            .format('+'.join(self.start_locn.split())))

    def __str__(self):
        return '{.short_name}'.format(self)

    def __repr__(self):
        return '<Populaire({})>'.format(self)


class PopulaireSchema(CSRFSchema):
    """Form schema for admin interface for Populaire model.
    """
    id = colander.SchemaNode(
        colander.Integer(),
        widget=HiddenWidget(),
        )
    event_name = colander.SchemaNode(
        colander.String(),
        )
    short_name = colander.SchemaNode(
        colander.String(),
        widget=TextInputWidget(
            placeholder='e.g. VicPop',
            )
        )
    distance = colander.SchemaNode(
        colander.String(),
        widget=TextInputWidget(
            placeholder='e.g. 50 km, 100 km',
            )
        )
    datetimeinputwidget_options = {
        'dateFormat': 'yy-mm-dd',
        'separator': ' ',
        'timeFormat': 'HH:mm:ss',
        'hourGrid': 6,
        'minuteGrid': 15,
    }
    date_time = colander.SchemaNode(
        colander.DateTime(),
        title='Date and Start Time',
        widget=DateTimeInputWidget(options=datetimeinputwidget_options),
        )
    start_locn = colander.SchemaNode(
        colander.String(),
        title='Start Location',
        widget=TextInputWidget(
            css_class='input-xxlarge',
            placeholder='Venue, Address, City',
            ),
        )
    start_map_url = colander.SchemaNode(
        colander.String(),
        title='Map URL for Start',
        widget=TextInputWidget(
            template='locationinput',
            css_class='input-xxlarge',
            ),
        )
    organizer_email = colander.SchemaNode(
        colander.String(),
        title='Organizer Email(s)',
        widget=TextInputWidget(
            template='emailinput',
            placeholder='tom@example.com, harry@example.com',
            css_class='input-xlarge',
            ),
        validator=colander.Email(),
        )
    registration_end = colander.SchemaNode(
        colander.DateTime(),
        title='Registration Closes',
        widget=DateTimeInputWidget(options=datetimeinputwidget_options),
        )
    entry_form_url = colander.SchemaNode(
        colander.String(),
        title='Entry Form URL',
        widget=TextInputWidget(
            css_class='input-xxlarge',
            placeholder='http://randonneurs.bc.ca/...',
            ),
        missing=None,
        )
