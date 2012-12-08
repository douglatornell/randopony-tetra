# -*- coding: utf-8 -*-
"""RandoPony administrator (aka wrangler) data model.
"""
import colander
from deform.widget import (
    HiddenWidget,
    TextInputWidget,
    )
from pyramid_deform import CSRFSchema
from sqlalchemy import (
    Column,
    Integer,
    Text,
    )
from .meta import Base


class Administrator(Base):
    """App administrator (aka Pony Wrangler).

    Authentication is via Mozilla Persona, so all we store is the admin's
    Persona email address.
    """
    __tablename__ = 'admins'
    id = Column(Integer, primary_key=True)
    persona_email = Column(Text, index=True, unique=True)

    def __init__(self, persona_email):
        self.persona_email = persona_email

    def __str__(self):
        return self.persona_email

    def __repr__(self):
        return '<Administrator({})>'.format(self)


class AdministratorSchema(CSRFSchema):
    """Form schema for admin interface for Administrator model.
    """
    id = colander.SchemaNode(
        colander.Integer(),
        widget=HiddenWidget(),
        )
    persona_email = colander.SchemaNode(
        colander.String(),
        widget=TextInputWidget(
            template='emailinput',
            autofocus=True,
            placeholder='tom@example.com',
            ),
        validator=colander.Email(),
        )
