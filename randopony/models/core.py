# -*- coding: utf-8 -*-
"""RandoPony data model core components.
"""
from sqlalchemy import (
    Column,
    Integer,
    Text,
    )
from .meta import Base


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
        return '<EmailAddress({.email})>'.format(self)


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

    def __init__(self, key, email):
        self.key = key
        self.email = email

    def __repr__(self):
        return '<Link({.email})>'.format(self)
