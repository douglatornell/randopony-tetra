# -*- coding: utf-8 -*-
"""RandoPony public site populaire views.
"""
from deform import Button
from pyramid_deform import FormView
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from sqlalchemy.orm.exc import NoResultFound
import transaction
from ...models import (
    Brevet,
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


def get_populaire_rider(email, first_name, last_name, populaire):
    try:
        rider = (DBSession.query(PopulaireRider)
        .filter_by(
            email=email,
            first_name=first_name,
            last_name=last_name,
            populaire=populaire,
            )
        .first())
    except NoResultFound:
        rider = None
    return rider


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
        rider = get_populaire_rider(
            email=appstruct['email'],
            first_name=appstruct['first_name'],
            last_name=appstruct['last_name'],
            populaire=populaire.id,
            )
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
                rider = PopulaireRider(
                    email=appstruct['email'],
                    first_name=appstruct['first_name'],
                    last_name=appstruct['last_name'],
                    distance=60,
                    comment=appstruct['comment'],
                    )
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
