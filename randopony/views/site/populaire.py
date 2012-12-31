# -*- coding: utf-8 -*-
"""RandoPony public site populaire views.
"""
from deform import Button
from pyramid_deform import FormView
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from sqlalchemy.orm.exc import NoResultFound
import transaction
from .core import SiteViews
from ...models import (
    Brevet,
    EmailAddress,
    Link,
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
        entry_form_url = (
            populaire.entry_form_url
            or DBSession.query(Link)
                .filter_by(key='entry_form')
                .one().url)
        self.tmpl_vars.update({
            'active_tab': 'populaires',
            'populaire': populaire,
            'entry_form_url': entry_form_url,
        })
        return self.tmpl_vars


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
            rider = PopulaireRider(
                email=appstruct['email'],
                first_name=appstruct['first_name'],
                last_name=appstruct['last_name'],
                distance=60,
                comment=appstruct['comment'],
                )
            with transaction.manager:
                populaire = get_populaire(pop_short_name)
                populaire.riders.append(rider)
                DBSession.add(rider)
                self.request.session.flash('success')
                self.request.session.flash(rider.email)
                entry_form_url = (
                    populaire.entry_form_url
                    or DBSession.query(Link)
                        .filter_by(key='entry_form')
                        .one().url)
                self.request.session.flash(entry_form_url)
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
