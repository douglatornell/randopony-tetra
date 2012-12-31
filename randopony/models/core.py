# -*- coding: utf-8 -*-
"""RandoPony data model core components.
"""
from datetime import (
    datetime,
    timedelta,
    )
from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    Text,
    )
from .meta import (
    Base,
    DBSession,
    )


class EmailAddress(Base):
    """Email address.

    Storage for "static" email addresses used in views;
    e.g. site administrator(s), club web master, etc.

    .. note::

       There is presently no admin interface for this model.
       Use `pshell` to manage instances.
    """
    __tablename__ = 'email_addresses'
    id = Column(Integer, primary_key=True)
    key = Column(Text, unique=True, index=True)
    email = Column(Text)

    def __init__(self, key, email):
        self.key = key
        self.email = email

    def __repr__(self):
        return '<EmailAddress({0.key}={0.email})>'.format(self)


class Link(Base):
    """Off-site link.

    Storage for URLs for content outside the RandoPony app;
    e.g. event waiver on club site.

    .. note::

       There is presently no admin interface for this model.
       Use `pshell` to manage instances.
    """
    __tablename__ = 'links'
    id = Column(Integer, primary_key=True)
    key = Column(Text, unique=True, index=True)
    url = Column(Text)

    def __init__(self, key, url):
        self.key = key
        self.url = url

    def __repr__(self):
        return '<Link({0.key}={0.url})>'.format(self)


class EventMixin(object):
    """Common database columns and properties for all event data models.
    """
    id = Column(Integer, primary_key=True)
    date_time = Column(DateTime, index=True)
    organizer_email = Column(Text)
    registration_end = Column(DateTime)
    google_doc_id = Column(Text)

    @classmethod
    def get_current(cls, recent_days=7):
        """Return query object for current events.
        """
        today = datetime.today()
        today = today.replace(hour=0, minute=0, second=0, microsecond=0)
        days_ago = today - timedelta(days=recent_days)
        events = (DBSession.query(cls)
            .filter(cls.date_time >= days_ago)
            .order_by(cls.date_time)
            )
        return events
