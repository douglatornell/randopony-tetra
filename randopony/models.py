# -*- coding: utf-8 -*-
"""RandoPony data model.
"""
from sqlalchemy import (
    Column,
    Integer,
    Text,
    )
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )
from zope.sqlalchemy import ZopeTransactionExtension


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class MyModel(Base):
    __tablename__ = 'models'
    id = Column(Integer, primary_key=True)
    name = Column(Text, unique=True)
    value = Column(Integer)

    def __init__(self, name, value):
        self.name = name
        self.value = value


class Administrator(Base):
    __tablename__ = 'admins'
    id = Column(Integer, primary_key=True)
    persona_email = Column(Text, unique=True)

    def __init__(self, persona_email):
        self.persona_email = persona_email

    def __str__(self):
        return self.persona_email
