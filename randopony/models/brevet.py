# -*- coding: utf-8 -*-
"""RandoPony brevet data model.
"""
from datetime import timedelta
from operator import itemgetter
import uuid
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
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Text,
)
from sqlalchemy.orm import relationship
from .core import EventMixin
from .meta import Base


class Brevet(EventMixin, Base):
    """Brevet event.
    """
    REGIONS = {
        '6K': 'Kamloops 6-Pack',
        'HW': 'Eau de Hell Week',
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
    riders = relationship(
        'BrevetRider',
        order_by='BrevetRider.lowercase_last_name',
    )

    def __init__(
        self, region, distance, date_time, route_name, start_locn,
        organizer_email, info_question=None, alt_date_time=None,
        registration_end=None, google_doc_id=None,
    ):
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
        self.google_doc_id = google_doc_id

    def __str__(self):
        return '{0.region}{0.distance} {0.date_time:%d%b%Y}'.format(self)

    def __repr__(self):
        return '<Brevet({})>'.format(self)

    @property
    def uuid(self):
        return uuid.uuid5(
            uuid.NAMESPACE_URL,
            '/randopony/{0.region}/{0.distance}/{0.date_time:%d%b%Y}'
            .format(self))


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
        colander.DateTime(default_tzinfo=None),
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
        colander.DateTime(default_tzinfo=None),
        title='Registration Closes',
        widget=DateTimeInputWidget(options=datetimeinputwidget_options),
    )


class BrevetRider(Base):
    """Brevet rider.
    """
    BIKE_TYPES = (
        ('fixie', 'Fixie'),
        ('quad', 'Quad'),
        ('recumbent', 'Recumbent'),
        ('recumbent tandem', 'Recumbent Tandem'),
        ('single', 'Single'),
        ('single-speed', 'Single-Speed'),
        ('tandem', 'Tandem'),
        ('triplet', 'Triplet'),
        ('velomobile', 'Velomobile'),
        ('other', 'Other... Seriously?!'),
    )

    __tablename__ = 'brevet_riders'

    id = Column(Integer, primary_key=True)
    email = Column(Text)
    first_name = Column(Text)
    last_name = Column(Text)
    lowercase_last_name = Column(Text, index=True)
    comment = Column(Text)
    member_status = Column(Boolean, nullable=True)
    bike_type = Column(Text)
    info_answer = Column(Text)
    brevet = Column(Integer, ForeignKey('brevets.id'))

    def __init__(self, first_name, last_name, email, comment,
                 bike_type='single', member_status=None, info_answer=None):
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.lowercase_last_name = self.last_name.lower()
        self.comment = comment
        self.bike_type = bike_type
        self.member_status = member_status
        self.info_answer = info_answer

    def __str__(self):
        return ' '.join((self.first_name, self.last_name))

    def __repr__(self):
        return '<Rider({})>'.format(self)

    @property
    def full_name(self):
        return (
            '{0.first_name} "{0.comment}" {0.last_name}'.format(self)
            if self.comment
            else str(self))


class BrevetEntrySchema(CSRFSchema):
    """Form schema for brevet rider pre-registration.
    """
    email = colander.SchemaNode(
        colander.String(),
        title='Email Address',
        widget=TextInputWidget(
            template='emailinput',
            autofocus=True,
            placeholder='you@example.com',
        ),
        validator=colander.Email(),
    )
    first_name = colander.SchemaNode(
        colander.String(),
    )
    last_name = colander.SchemaNode(
        colander.String(),
    )
    comment = colander.SchemaNode(
        colander.String(),
        widget=TextInputWidget(
            template='textinput',
            placeholder='wit, wisdom, ...',
            help_block=(
                'Your comment will appear with your name like: '
                'Tom "fueled by coffee" Dickson. It is optional. '
                'Please be sensible and respectful. This is the Internet. '
                'What is written once can never be unwritten.'),
        ),
        missing=None,
    )
    bike_type = colander.SchemaNode(
        colander.String(),
        default='single',
        widget=SelectWidget(values=BrevetRider.BIKE_TYPES),
    )
