# -*- coding: utf-8 -*-
"""RandoPony base site views.
"""
import logging
from deform import Button
from pyramid_deform import FormView
from pyramid.httpexceptions import HTTPFound
from pyramid.view import (
    notfound_view_config,
    view_config,
    )
import transaction
from ..models import (
    Brevet,
    EmailAddress,
    Populaire,
    PopulaireEntrySchema,
    PopulaireRider,
    )
from ..models.meta import DBSession


log = logging.getLogger(__name__)


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

    @notfound_view_config(renderer='404.mako')
    def notfound(self):
        self.request.response.status = '404 Not Found'
        self.tmpl_vars.update({
            'active_tab': None,
        })
        return self.tmpl_vars

    @view_config(route_name='region.list', renderer='region-list.mako')
    @view_config(route_name='register', renderer='region-list.mako')
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

    @view_config(route_name='brevet.list', renderer='brevet-list.mako')
    @view_config(route_name='register.region', renderer='brevet-list.mako')
    def brevet_list(self):
        region = self.request.matchdict['region']
        region_brevets = (self.tmpl_vars['brevets']
            .filter_by(region=region)
            )
        images = {
            'LM': {
                'file': 'LowerMainlandQuartet.jpg',
                'alt': 'Harrison Hotsprings Road',
                'credit': 'Nobo Yonemitsu',
                },
            'SI': {
                'file': 'SouthIntLivestock.jpg',
                'alt': 'Southern Interior Peloton',
                'credit': 'Bud MacRae',
            },
            'VI': {
                'file': 'VanIsDuo.jpg',
                'alt': 'Van Isle Duo',
                'credit': 'Raymond Parker'},
        }
        self.tmpl_vars.update({
            'active_tab': 'brevets',
            'region': region,
            'regions': Brevet.REGIONS,
            'region_brevets': region_brevets,
            'image': images[region],
        })
        return self.tmpl_vars

    @view_config(route_name='populaire.list', renderer='populaire-list.mako')
    def populaire_list(self):
        admin_email = (DBSession.query(EmailAddress)
            .filter_by(key='admin_email')
            .one())
        self.tmpl_vars.update({
            'active_tab': 'populaires',
            'admin_email': admin_email.email,
        })
        return self.tmpl_vars

    @view_config(route_name='populaire', renderer='populaire.mako')
    def populaire_page(self):
        populaire = get_populaire(self.request.matchdict['short_name'])
        self.tmpl_vars.update({
            'active_tab': 'populaires',
            'populaire': populaire,
        })
        return self.tmpl_vars


def get_populaire(short_name):
    populaire = (DBSession.query(Populaire)
        .filter_by(short_name=short_name)
        .first()
        )
    return populaire


@view_config(
    route_name='populaire.entry',
    renderer='populaire-entry.mako',
    )
class PopulaireEntry(FormView):
    schema = PopulaireEntrySchema()
    buttons = (
        Button(name='register', css_class='btn btn-primary'),
        Button(name='cancel', css_class='btn', type='reset'),
        )

    def _redirect_url(self, short_name):
        return self.request.route_url('populaire', short_name=short_name)

    def show(self, form):
        tmpl_vars = super(PopulaireEntry, self).show(form)
        populaire = get_populaire(self.request.matchdict['short_name'])
        tmpl_vars.update({
            'active_tab': 'populaires',
            'brevets': Brevet.get_current(),
            'populaires': Populaire.get_current(),
            'populaire': populaire,
            'cancel_url': self._redirect_url(
                self.request.matchdict['short_name']),
            })
        return tmpl_vars

    def register_success(self, appstruct):
        pop_short_name = self.request.matchdict['short_name']
        with transaction.manager:
            populaire = get_populaire(pop_short_name)
            rider = PopulaireRider(
                email=appstruct['email'],
                first_name=appstruct['first_name'],
                last_name=appstruct['last_name'],
                distance=60,
                comment=appstruct['comment'],
                )
            populaire.riders.append(rider)
            DBSession.add(rider)
        return HTTPFound(self._redirect_url(pop_short_name))

    def failure(self, e):
        tmpl_vars = super(PopulaireEntry, self).failure(e)
        populaire = get_populaire(self.request.matchdict['short_name'])
        tmpl_vars.update({
            'active_tab': 'populaires',
            'brevets': Brevet.get_current(),
            'populaires': Populaire.get_current(),
            'populaire': populaire,
            'cancel_url': self._redirect_url(
                self.request.matchdict['short_name']),
            })
        return tmpl_vars
