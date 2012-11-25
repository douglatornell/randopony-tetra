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
        self.tmpl_vars = {
            'brevets': Brevet.get_current(),
        }

    @view_config(route_name='home', renderer='home.mako')
    def home(self):
        self.tmpl_vars.update({
            'active_tab': 'home',
        })
        return self.tmpl_vars

    @view_config(route_name='organizer-info', renderer='organizer-info.mako')
    def organizer_info(self):
        admin_email = (DBSession.query(EmailAddress)
            .filter_by(key='admin_email')
            .one())
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

    @view_config(route_name='region.list', renderer='region-list.mako')
    def region_list(self):
        region_brevets = {
            region: self.tmpl_vars['brevets']
                .filter_by(region=region)
                for region in Brevet.REGIONS.keys()}
        admin_email = (DBSession.query(EmailAddress)
            .filter_by(key='admin_email')
            .one()
            )
        self.tmpl_vars.update({
            'active_tab': 'brevets',
            'regions': Brevet.REGIONS,
            'region_brevets': region_brevets,
            'admin_email': admin_email.email,
        })
        return self.tmpl_vars
