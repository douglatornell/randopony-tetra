# -*- coding: utf-8 -*-
"""RandoPony base site views.
"""
from pyramid.view import view_config
from .. models import (
    Brevet,
    DBSession,
    EmailAddress,
    )


class SiteViews(object):
    """Views for the RandoPony public site.
    """
    def __init__(self, request):
        self.request = request

    @view_config(route_name='home', renderer='home.mako')
    def home(self):
        tmpl_vars = {
            'active_tab': 'home',
            'brevets': Brevet.get_current(),
        }
        return tmpl_vars

    @view_config(route_name='organizer-info', renderer='organizer-info.mako')
    def organizer_info(self):
        admin_email = (DBSession.query(EmailAddress)
            .filter_by(key='admin_email')
            .one())
        tmpl_vars = {
            'active_tab': 'organizer-info',
            'admin_email': admin_email.email,
            'brevets': Brevet.get_current(),
        }
        return tmpl_vars

    @view_config(route_name='about', renderer='about-pony.mako')
    def about(self):
        tmpl_vars = {
            'active_tab': 'about',
            'brevets': Brevet.get_current(),
        }
        return tmpl_vars
