# -*- coding: utf-8 -*-
"""RandoPony brevet admin views.
"""
from datetime import (
    datetime,
    timedelta,
    )
from deform import Button
from pyramid_deform import FormView
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
import transaction
from ...models import (
    Brevet,
    BrevetSchema,
    )
from ...models.meta import DBSession


def get_brevet(code, date):
    region = code[:2]
    distance = code[2:]
    date = datetime.strptime(date, '%d%b%Y')
    return (DBSession.query(Brevet)
        .filter_by(region=region)
        .filter_by(distance=distance)
        .filter(Brevet.date_time >= date)
        .filter(Brevet.date_time < date + timedelta(days=1))
        .first()
        )


@view_config(
    route_name='admin.brevets.view',
    renderer='admin/brevet.mako',
    permission='admin',
    )
def brevet_details(request):
    code, date = request.matchdict['item'].split()
    brevet = get_brevet(code, date)
    return {
        'logout_btn': True,
        'brevet': brevet,
        }


@view_config(
    route_name='admin.brevets.create',
    renderer='admin/brevet_edit.mako',
    permission='admin',
    )
class BrevetCreate(FormView):
    schema = BrevetSchema()
    for field in 'id registration_end start_map_url'.split():
        schema.__delitem__(field)
    buttons = (
        Button(name='add', css_class='btn btn-primary'),
        Button(name='cancel', css_class='btn', type='reset'),
        )

    def list_url(self):
        return self.request.route_url('admin.list', list='brevets')

    def show(self, form):
        tmpl_vars = super(BrevetCreate, self).show(form)
        tmpl_vars.update({
            'logout_btn': True,
            'cancel_url': self.list_url()
            })
        return tmpl_vars

    def add_success(self, appstruct):
        with transaction.manager:
            brevet = Brevet(
                region=appstruct['region'],
                distance=appstruct['distance'],
                date_time=appstruct['date_time'],
                route_name=appstruct['route_name'],
                start_locn=appstruct['start_locn'],
                organizer_email=appstruct['organizer_email'],
                )
            brevet_id = str(brevet)
            DBSession.add(brevet)
        return HTTPFound(
            self.request.route_url('admin.brevets.view', item=brevet_id))

    def failure(self, e):
        tmpl_vars = super(BrevetCreate, self).failure(e)
        tmpl_vars.update({
            'logout_btn': True,
            'cancel_url': self.list_url()
            })
        return tmpl_vars


@view_config(
    route_name='admin.brevets.edit',
    renderer='admin/brevet_edit.mako',
    permission='admin',
    )
class BrevetEdit(FormView):
    schema = BrevetSchema()
    buttons = (
        Button(name='save', css_class='btn btn-primary'),
        Button(name='cancel', css_class='btn', type='reset'),
        )

    def view_url(self):
        return self.request.route_url(
            'admin.brevets.view', item=self.request.matchdict['item'])

    def appstruct(self):
        code, date = self.request.matchdict['item'].split()
        brevet = get_brevet(code, date)
        return {
            'id': brevet.id,
            'region': brevet.region,
            'distance': brevet.distance,
            'date_time': brevet.date_time,
            'route_name': brevet.route_name,
            'start_locn': brevet.start_locn,
            'start_map_url': brevet.start_map_url,
            'organizer_email': brevet.organizer_email,
            'registration_end': brevet.registration_end,
        }

    def show(self, form):
        tmpl_vars = super(BrevetEdit, self).show(form)
        tmpl_vars.update({
            'logout_btn': True,
            'cancel_url': self.view_url()
            })
        return tmpl_vars

    def save_success(self, appstruct):
        with transaction.manager:
            brevet = (DBSession.query(Brevet)
                .filter_by(id=appstruct['id'])
                .one())
            brevet.region = appstruct['region']
            brevet.distance = appstruct['distance']
            brevet.date_time = appstruct['date_time']
            brevet.route_name = appstruct['route_name']
            brevet.start_locn = appstruct['start_locn']
            brevet.start_map_url = appstruct['start_map_url']
            brevet.organizer_email = appstruct['organizer_email']
            brevet.registration_end = appstruct['registration_end']
            brevet_id = str(brevet)
        return HTTPFound(
            self.request.route_url('admin.brevets.view', item=brevet_id))

    def failure(self, e):
        tmpl_vars = super(BrevetEdit, self).failure(e)
        tmpl_vars.update({
            'logout_btn': True,
            'cancel_url': self.view_url()
            })
        return tmpl_vars
