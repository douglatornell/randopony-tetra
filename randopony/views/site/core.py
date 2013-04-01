# -*- coding: utf-8 -*-
"""RandoPony public site core views.
"""
from pyramid.view import (
    notfound_view_config,
    view_config,
)
from ...models import (
    Brevet,
    EmailAddress,
    Populaire,
)
from ...models.meta import DBSession


class SiteViews(object):
    """Views for the RandoPony public site.
    """
    def __init__(self, request):
        self.request = request
        self.tmpl_vars = {
            'brevets': Brevet.get_current(),
            'populaires': Populaire.get_current(),
        }

    @view_config(route_name='home', renderer='home.mako')
    def home(self):
        self.tmpl_vars.update({
            'active_tab': 'home',
        })
        return self.tmpl_vars

    @view_config(route_name='organizer-info', renderer='organizer-info.mako')
    def organizer_info(self):
        admin_email = (
            DBSession.query(EmailAddress)
            .filter_by(key='admin_email')
            .one()
        )
        self.tmpl_vars.update({
            'active_tab': 'organizer-info',
            'admin_email': admin_email.email,
        })
        return self.tmpl_vars

    @view_config(route_name='about', renderer='about-pony.mako')
    def about(self):
        self.tmpl_vars.update({
            'active_tab': 'about',
        })
        return self.tmpl_vars

    @notfound_view_config(renderer='404.mako')
    def notfound(self):
        self.request.response.status = '404 Not Found'
        self.tmpl_vars.update({
            'active_tab': None,
        })
        return self.tmpl_vars
