# -*- coding: utf-8 -*-
"""RandoPony public site populaire views.
"""
from datetime import datetime
from deform import Button
from pyramid_deform import FormView
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
import pytz
import transaction
from .core import SiteViews
from ...models import (
    Brevet,
    EmailAddress,
    Populaire,
    PopulaireEntrySchema,
    PopulaireRider,
    )
from ...models.meta import DBSession


def get_populaire(short_name):
    populaire = (DBSession.query(Populaire)
        .filter_by(short_name=short_name)
        .first()
        )
    return populaire


class PopulaireViews(SiteViews):
    """Views for populaires section of RandoPony public site
    """
    def __init__(self, request):
        super(PopulaireViews, self).__init__(request)

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
        registration_closed = self._registration_closed(
            populaire.registration_end)
        self.tmpl_vars.update({
            'active_tab': 'populaires',
            'populaire': populaire,
            'registration_closed': registration_closed,
        })
        return self.tmpl_vars

    def _registration_closed(self, registration_end):
        tz = pytz.timezone(self.request.registry.settings['timezone'])
        utc_registration_end = (
            tz.localize(registration_end).astimezone(pytz.utc))
        utc_now = pytz.utc.localize(datetime.utcnow())
        return utc_now > utc_registration_end


@view_config(
    route_name='populaire.entry',
    renderer='populaire-entry.mako',
    )
class PopulaireEntry(FormView):
    def maybe_include_distance(node, kw):
        if not kw.get('include_distance'):
            del node['distance']

    schema = PopulaireEntrySchema(after_bind=maybe_include_distance)
    buttons = (
        Button(name='register', css_class='btn btn-primary'),
        Button(name='cancel', css_class='btn', type='reset'),
        )

    def _redirect_url(self, short_name):
        return self.request.route_url('populaire', short_name=short_name)

    def get_bind_data(self):
        data = super(PopulaireEntry, self).get_bind_data()
        populaire = get_populaire(self.request.matchdict['short_name'])
        distances = [
            (int(d.split()[0]), d.strip())
            for d in populaire.distance.split(',')
            ]
        data.update({
            'distances': distances,
            'include_distance': len(distances) > 1,
            })
        return data

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
        populaire = get_populaire(pop_short_name)
        # Check for rider already registered
        rider = (DBSession.query(PopulaireRider)
            .filter_by(
                email=appstruct['email'],
                first_name=appstruct['first_name'],
                last_name=appstruct['last_name'],
                populaire=populaire.id,
                )
            .first())
        if rider is not None:
            # Rider with same name and email already registered
            self.request.session.flash('duplicate')
            self.request.session.flash(
                ' '.join((appstruct['first_name'], appstruct['last_name'])))
            self.request.session.flash(appstruct['email'])
        else:
            # New rider registration
            with transaction.manager:
                populaire = get_populaire(pop_short_name)
                try:
                    distance = appstruct['distance']
                except KeyError:
                    distance = populaire.distance.split()[0]
                rider = PopulaireRider(
                    email=appstruct['email'],
                    first_name=appstruct['first_name'],
                    last_name=appstruct['last_name'],
                    distance=distance,
                    comment=appstruct['comment'],
                    )
                populaire.riders.append(rider)
                DBSession.add(rider)
                self.request.session.flash('success')
                self.request.session.flash(rider.email)
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
