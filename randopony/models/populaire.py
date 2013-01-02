# -*- coding: utf-8 -*-
"""RandoPony populaire data model.
"""
import colander
from deform.widget import (
    DateTimeInputWidget,
    HiddenWidget,
    RadioChoiceWidget,
    TextInputWidget,
    )
from pyramid_deform import CSRFSchema
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Text,
    )
from sqlalchemy.orm import relationship
from .core import (
    EventMixin,
    Link,
    )
from .meta import (
    Base,
    DBSession,
    )


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
    riders = relationship(
        'PopulaireRider',
        order_by='PopulaireRider.lowercase_last_name',
        )

    def __init__(self, event_name, short_name, distance, date_time,
        start_locn, organizer_email, registration_end, entry_form_url=None):
        self.event_name = event_name
        self.short_name = short_name
        self.distance = distance
        self.date_time = date_time
        self.start_locn = start_locn
        self.organizer_email = organizer_email
        self.registration_end = registration_end
        self.entry_form_url = (
            entry_form_url
            or DBSession.query(Link)
            .filter_by(key='entry_form')
            .one().url)
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


class PopulaireRider(Base):
    """Populaire rider.
    """
    __tablename__ = 'populaire_riders'

    id = Column(Integer, primary_key=True)
    email = Column(Text)
    first_name = Column(Text)
    last_name = Column(Text)
    lowercase_last_name = Column(Text, index=True)
    comment = Column(Text)
    distance = Column(Integer)
    populaire = Column(Integer, ForeignKey('populaires.id'))

    def __init__(self, first_name, last_name, email, distance, comment):
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.lowercase_last_name = self.last_name.lower()
        self.distance = distance
        self.comment = comment

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


class PopulaireEntrySchema(CSRFSchema):
    """Form schema for populaire rider pre-regisration.
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

    @colander.deferred
    def deferred_distance_widget(node, kw):
        distances = kw.get('distances')
        return RadioChoiceWidget(
            values=distances,
            css_class='radio inline',
            )

    distance = colander.SchemaNode(
        colander.Integer(),
        title='Distance (choose one)',
        widget=deferred_distance_widget,
        )
