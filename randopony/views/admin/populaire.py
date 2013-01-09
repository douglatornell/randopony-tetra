# -*- coding: utf-8 -*-
"""RandoPony populaire admin views.
"""
from deform import Button
from gdata.docs.client import DocsClient
from pyramid_deform import FormView
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
import transaction
from .core import (
    google_drive_login,
    get_rider_list_template,
    share_rider_list_publicly,
    )
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
    route_name='admin.populaires.create_rider_list',
    permission='admin',
    )
def create_rider_list(request):
    short_name = request.matchdict['item']
    populaire = get_populaire(short_name)
    redirect_url = request.route_url('admin.populaires.view', item=short_name)
    if populaire.google_doc_id:
        request.session.flash('error')
        request.session.flash('Rider list spreadsheet already created')
        return HTTPFound(redirect_url)
    client = google_drive_login(
        DocsClient,
        request.registry.settings['google_drive.username'],
        request.registry.settings['google_drive.password'])
    template = get_rider_list_template('Populaire Rider List Template', client)
    created_doc = client.copy_resource(
        template, '{0} {0.date_time:%d-%b-%Y}'.format(populaire))
    share_rider_list_publicly(created_doc, client)
    with transaction.manager:
        populaire = get_populaire(short_name)
        populaire.google_doc_id = created_doc.resource_id.text
        request.session.flash('success')
        request.session.flash('Rider list spreadsheet created')
    return HTTPFound(redirect_url)


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
        with transaction.manager:
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
