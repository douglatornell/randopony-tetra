# -*- coding: utf-8 -*-
"""RandoPony brevet admin views.
"""
from deform import Button
from pyramid_deform import FormView
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
import transaction
from ...models import (
    Populaire,
    PopulaireSchema,
    )
from ...models.meta import DBSession


def get_populaire(short_name):
    return (DBSession.query(Populaire)
        .filter_by(short_name=short_name)
        .first()
        )


@view_config(
    route_name='admin.populaires.view',
    renderer='admin/populaire.mako',
    permission='admin',
    )
def populaire_details(request):
    short_name = request.matchdict['item']
    populaire = get_populaire(short_name)
    return {
        'logout_btn': True,
        'populaire': populaire,
        }


@view_config(
    route_name='admin.populaires.create',
    renderer='admin/populaire_edit.mako',
    permission='admin',
    )
class PopulaireCreate(FormView):
    schema = PopulaireSchema()
    for field in 'id start_map_url'.split():
        schema.__delitem__(field)
    buttons = (
        Button(name='add', css_class='btn btn-primary'),
        Button(name='cancel', css_class='btn', type='reset'),
        )

    def list_url(self):
        return self.request.route_url('admin.list', list='populaires')

    def show(self, form):
        tmpl_vars = super(PopulaireCreate, self).show(form)
        tmpl_vars.update({
            'logout_btn': True,
            'cancel_url': self.list_url()
            })
        return tmpl_vars

    def add_success(self, appstruct):
        with transaction.manager:
            populaire = Populaire(
                event_name=appstruct['event_name'],
                short_name=appstruct['short_name'],
                distance=appstruct['distance'],
                date_time=appstruct['date_time'],
                start_locn=appstruct['start_locn'],
                organizer_email=appstruct['organizer_email'],
                registration_end=appstruct['registration_end'],
                entry_form_url=appstruct['entry_form_url'],
                )
            populaire_id = str(populaire)
            DBSession.add(populaire)
        return HTTPFound(
            self.request.route_url('admin.populaires.view', item=populaire_id))

    def failure(self, e):
        tmpl_vars = super(PopulaireCreate, self).failure(e)
        tmpl_vars.update({
            'logout_btn': True,
            'cancel_url': self.list_url()
            })
        return tmpl_vars


@view_config(
    route_name='admin.populaires.edit',
    renderer='admin/populaire_edit.mako',
    permission='admin',
    )
class PopulaireEdit(FormView):
    schema = PopulaireSchema()
    buttons = (
        Button(name='save', css_class='btn btn-primary'),
        Button(name='cancel', css_class='btn', type='reset'),
        )

    def _redirect_url(self, item):
        return self.request.route_url('admin.populaires.view', item=item)

    def appstruct(self):
        short_name = self.request.matchdict['item']
        populaire = get_populaire(short_name)
        return {
            'id': populaire.id,
            'event_name': populaire.event_name,
            'short_name': populaire.short_name,
            'distance': populaire.distance,
            'date_time': populaire.date_time,
            'start_locn': populaire.start_locn,
            'start_map_url': populaire.start_map_url,
            'organizer_email': populaire.organizer_email,
            'registration_end': populaire.registration_end,
            'entry_form_url': populaire.entry_form_url,
        }

    def show(self, form):
        tmpl_vars = super(PopulaireEdit, self).show(form)
        tmpl_vars.update({
            'logout_btn': True,
            'cancel_url': self._redirect_url(self.request.matchdict['item']),
            })
        return tmpl_vars

    def save_success(self, appstruct):
        with transaction.manager:
            populaire = (DBSession.query(Populaire)
                .filter_by(id=appstruct['id'])
                .one())
            populaire.event_name = appstruct['event_name']
            populaire.short_name = appstruct['short_name']
            populaire.distance = appstruct['distance']
            populaire.date_time = appstruct['date_time']
            populaire.start_locn = appstruct['start_locn']
            populaire.start_map_url = appstruct['start_map_url']
            populaire.organizer_email = appstruct['organizer_email']
            populaire.registration_end = appstruct['registration_end']
            populaire.entry_form_url = appstruct['entry_form_url']
            populaire_id = str(populaire)
        return HTTPFound(self._redirect_url(populaire_id))

    def failure(self, e):
        tmpl_vars = super(PopulaireEdit, self).failure(e)
        tmpl_vars.update({
            'logout_btn': True,
            'cancel_url': self._redirect_url(self.request.matchdict['item']),
            })
        return tmpl_vars
