# -*- coding: utf-8 -*-
"""RandoPony base site views.
"""
from pyramid.view import view_config


@view_config(route_name='home', renderer='home.mako')
def home(request):
    return {}


@view_config(route_name='organizer-info', renderer='organizer-info.mako')
def organizer_info(request):
    return {
        'admin_email': 'djl@douglatornell.ca',
    }


@view_config(route_name='about', renderer='about-pony.mako')
def about(request):
    return {}
