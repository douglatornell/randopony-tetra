# -*- coding: utf-8 -*-
"""RandoPony base site views.
"""
from pyramid.view import view_config
from .. models import (
    DBSession,
    EmailAddress,
    )


@view_config(route_name='home', renderer='home.mako')
def home(request):
    return {}


@view_config(route_name='organizer-info', renderer='organizer-info.mako')
def organizer_info(request):
    admin_email = (DBSession.query(EmailAddress)
        .filter_by(key='admin_email')
        .one())
    return {
        'admin_email': admin_email.email,
    }


@view_config(route_name='about', renderer='about-pony.mako')
def about(request):
    return {}
