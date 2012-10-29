# -*- coding: utf-8 -*-
"""RandoPony data model.
"""
import colander
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
    """App administrator (aka Pony Wrangler).

    Authentication is via Mozilla Persona, so all we store is the admin'
    Persona email address.
    """
    __tablename__ = 'admins'
    id = Column(Integer, primary_key=True)
    persona_email = Column(Text, index=True, unique=True)

    def __init__(self, persona_email):
        self.persona_email = persona_email

    def __str__(self):
        return self.persona_email


class AdministratorSchema(colander.MappingSchema):
    """Form schema for admin interface for Administrator model.
    """
    persona_email = colander.SchemaNode(
        colander.String(), validator=colander.Email())
