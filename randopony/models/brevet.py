# -*- coding: utf-8 -*-
"""RandoPony brevet data model.
"""
from datetime import timedelta
from operator import itemgetter
import colander
from deform.widget import (
    DateTimeInputWidget,
    HiddenWidget,
    RadioChoiceWidget,
    SelectWidget,
    TextInputWidget,
    )
from pyramid_deform import CSRFSchema
from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    Text,
    )
from .core import EventMixin
from .meta import Base


class Brevet(EventMixin, Base):
    """Brevet event.
    """
    REGIONS = {
        'LM': 'Lower Mainland',
        'PR': 'Peace Region',
        'SI': 'Southern Interior',
        'VI': 'Vancouver Island',
    }
    DISTANCES = {
        200: '200 km',
        300: '300 km',
        400: '400 km',
        600: '600 km',
        1000: '1000 km',
    }

    __tablename__ = 'brevets'

    region = Column(Text, index=True)
    distance = Column(Integer)
    alt_date_time = Column(DateTime)
    route_name = Column(Text)
    start_locn = Column(Text)
    start_map_url = Column(Text)
    info_question = Column(Text)

    def __init__(self, region, distance, date_time, route_name, start_locn,
        organizer_email, info_question=None, alt_date_time=None,
        registration_end=None):
        self.region = region
        self.distance = distance
        self.date_time = date_time
        self.alt_date_time = alt_date_time
        self.route_name = route_name
        self.start_locn = start_locn
        self.organizer_email = organizer_email
        self.info_question = info_question
        if registration_end is None:
            self.registration_end = (
                self.date_time - timedelta(days=1)).\
                replace(hour=12, minute=0, second=0)
        else:
            self.registration_end = registration_end
        self.start_map_url = (
            'https://maps.google.com/maps?q={}'
            .format('+'.join(self.start_locn.split())))

    def __str__(self):
        return '{0.region}{0.distance} {0.date_time:%d%b%Y}'.format(self)

    def __repr__(self):
        return '<Brevet({})>'.format(self)


class BrevetSchema(CSRFSchema):
    """Form schema for admin interface for Brevet model.
    """
    id = colander.SchemaNode(
        colander.Integer(),
        widget=HiddenWidget(),
        )
    region = colander.SchemaNode(
        colander.String(),
        widget=SelectWidget(
            values=[(k, v) for k, v
                    in sorted(Brevet.REGIONS.items(), key=itemgetter(0))],
            autofocus=True,
            placeholder='Please choose...',
            ),
        validator=colander.OneOf(Brevet.REGIONS.keys()),
        )
    distance = colander.SchemaNode(
        colander.Integer(),
        widget=RadioChoiceWidget(
            values=[(k, v) for k, v
                    in sorted(Brevet.DISTANCES.items(), key=itemgetter(0))],
            css_class='radio inline'),
        validator=colander.OneOf(Brevet.DISTANCES.keys()),
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
    route_name = colander.SchemaNode(
        colander.String()
        )
    start_locn = colander.SchemaNode(
        colander.String(),
        title='Start Location',
        widget=TextInputWidget(
            css_class='input-xxlarge',
            placeholder='Venue, Address, City',
            )
        )
    start_map_url = colander.SchemaNode(
        colander.String(),
        title='Map URL for Start',
        widget=TextInputWidget(
            template='locationinput',
            css_class='input-xxlarge',
            )
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
