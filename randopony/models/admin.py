"""RandoPony administrator (aka wrangler) data model.
"""
import colander
from deform.widget import (
    HiddenWidget,
    PasswordWidget,
    TextInputWidget,
)
from pyramid_deform import CSRFSchema
from sqlalchemy import (
    Column,
    Integer,
    Text,
)
from sqlalchemy.orm.exc import NoResultFound

from randopony.models.meta import (
    Base,
    DBSession,
)


class Administrator(Base):
    """App administrator (aka Pony Wrangler).
    """
    __tablename__ = 'admins'
    id = Column(Integer, primary_key=True)
    email = Column(Text, index=True, unique=True)
    password_hash = Column(Text, nullable=False)

    def __init__(self, email, password_hash):
        self.email = email
        self.password_hash = password_hash

    def __str__(self):
        return self.email

    def __repr__(self):
        return '<Administrator({})>'.format(self)

    @classmethod
    def get(cls, email):
        try:
            return (
                DBSession.query(cls)
                .filter(cls.email == email)
                .one()
            )
        except NoResultFound:
            raise NoResultFound('no User with email: {}'.format(email))


class AdministratorSchema(CSRFSchema):
    """Form schema for admin interface for Administrator model.
    """
    id = colander.SchemaNode(
        colander.Integer(),
        widget=HiddenWidget(),
    )
    email = colander.SchemaNode(
        colander.String(),
        widget=TextInputWidget(
            template='emailinput',
            autofocus=True,
            placeholder='tom@example.com',
        ),
        validator=colander.Email(),
    )
    password = colander.SchemaNode(
        colander.String(),
        widget=PasswordWidget(),
    )
