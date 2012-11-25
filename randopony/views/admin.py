# -*- coding: utf-8 -*-
"""RandoPony admin views.
"""
from datetime import (
    datetime,
    timedelta,
    )
from deform import Button
from pyramid_deform import FormView
from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import render
from pyramid.response import Response
from pyramid.view import (
    forbidden_view_config,
    view_config,
    view_defaults,
    )
from sqlalchemy import desc
import transaction
from ..models import (
    Administrator,
    AdministratorSchema,
    Brevet,
    BrevetSchema,
    DBSession,
    )


@forbidden_view_config()
def login(request):
    body = render('admin/login.mako', {'logout_btn': False}, request=request)
    return Response(body, status='403 Forbidden')


@view_defaults(permission='admin')
class AdminViews(object):
    """Views for the RandoPony admin interface.
    """
    lists = {
        'wranglers': {
            'model': Administrator,
            'item_type': 'administrator',
            'list_title': 'Pony Wranglers',
            'order_by': Administrator.persona_email,
            'action': 'edit',
        },
        'brevets': {
            'model': Brevet,
            'item_type': 'brevet',
            'list_title': 'Brevets',
            'order_by': desc(Brevet.date_time),
            'action': 'view',
        },
    }

    def __init__(self, request):
        self.request = request

    @view_config(route_name='admin.home', renderer='admin/home.mako')
    def home(self):
        return {'logout_btn': True}

    @view_config(route_name='admin.list', renderer='admin/list.mako')
    def items_list(self):
        list_name = self.request.matchdict['list']
        params = self.lists[list_name]
        tmpl_vars = {
            'logout_btn': True,
            'items': (DBSession.query(params['model'])
                .order_by(params['order_by'])),
            'action': params['action'],
            'list': list_name,
            'list_title': params['list_title'],
        }
        return tmpl_vars

    @view_config(route_name='admin.delete',
        renderer='admin/confirm_delete.mako')
    def delete(self):
        """Delete the specified list item, after confirmation.
        """
        list_name = self.request.matchdict['list']
        item = self.request.matchdict['item']
        # Render confirmation form
        params = self.lists[list_name]
        tmpl_vars = {
            'logout_btn': True,
            'list': list_name,
            'item': item,
            'item_type': params['item_type'],
        }
        # Handle form submission
        list_view = self.request.route_url('admin.list', list=list_name)
        if 'cancel' in self.request.POST:
            return HTTPFound(list_view)
        if 'delete' in self.request.POST:
            if list_name == 'brevets':
                criterion = Brevet.id == get_brevet(*item.split()).id
            elif list_name == 'wranglers':
                criterion = Administrator.persona_email == item
            with transaction.manager:
                (DBSession.query(params['model'])
                    .filter(criterion)
                    .delete())
            return HTTPFound(list_view)
        return tmpl_vars


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
        print(e)
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


@view_config(
    route_name='admin.wranglers.create',
    renderer='admin/wrangler.mako',
    permission='admin',
    )
class WranglerCreate(FormView):
    schema = AdministratorSchema()
    schema.__delitem__('id')
    buttons = (
        Button(name='add', css_class='btn btn-primary'),
        Button(name='cancel', css_class='btn', type='reset'),
        )

    def list_url(self):
        return self.request.route_url('admin.list', list='wranglers')

    def show(self, form):
        tmpl_vars = super(WranglerCreate, self).show(form)
        tmpl_vars.update({
            'logout_btn': True,
            'list_url': self.list_url()
            })
        return tmpl_vars

    def add_success(self, appstruct):
        with transaction.manager:
            admin = Administrator(appstruct['persona_email'])
            DBSession.add(admin)
        return HTTPFound(self.list_url())

    def failure(self, e):
        tmpl_vars = super(WranglerCreate, self).failure(e)
        tmpl_vars.update({
            'logout_btn': True,
            'list_url': self.list_url()
            })
        return tmpl_vars


@view_config(
    route_name='admin.wranglers.edit',
    renderer='admin/wrangler.mako',
    permission='admin',
    )
class WranglerEdit(FormView):
    schema = AdministratorSchema()
    buttons = (
        Button(name='save', css_class='btn btn-primary'),
        Button(name='cancel', css_class='btn', type='reset'),
        )

    def list_url(self):
        return self.request.route_url('admin.list', list='wranglers')

    def appstruct(self):
        admin = (DBSession.query(Administrator)
            .filter_by(persona_email=self.request.matchdict['item'])
            .one())
        return {
            'id': admin.id,
            'persona_email': admin.persona_email,
            }

    def show(self, form):
        tmpl_vars = super(WranglerEdit, self).show(form)
        tmpl_vars.update({
            'logout_btn': True,
            'list_url': self.list_url()
            })
        return tmpl_vars

    def save_success(self, appstruct):
        with transaction.manager:
            admin = (DBSession.query(Administrator)
                .filter_by(id=appstruct['id'])
                .one())
            admin.persona_email = appstruct['persona_email']
        return HTTPFound(self.list_url())

    def failure(self, e):
        tmpl_vars = super(WranglerEdit, self).failure(e)
        tmpl_vars.update({
            'logout_btn': True,
            'list_url': self.list_url()
            })
        return tmpl_vars
