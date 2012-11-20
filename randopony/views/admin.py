# -*- coding: utf-8 -*-
"""RandoPony admin views.
"""
from deform import (
    Button,
    Form,
    ValidationFailure,
    ZPTRendererFactory,
    )
from pkg_resources import resource_filename
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


deform_templates = resource_filename('deform', 'deform_templates')
search_path = ('randopony/templates/deform', deform_templates)
renderer = ZPTRendererFactory(search_path)


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
            criterion = {
                'wranglers': Administrator.persona_email == item,
            }
            with transaction.manager:
                DBSession.query(params['model']).\
                    filter(criterion[list_name]).delete()
            return HTTPFound(list_view)
        return tmpl_vars

    @view_config(route_name='admin.brevets', renderer='admin/brevet.mako')
    def brevet(self):
        """Brevet create/update/view form handler.
        """
        tmpl_vars = {'logout_btn': True}
        # Render create/update form
        brevet = self.request.matchdict['item']
        if brevet == 'new':
            form = Form(
                BrevetSchema(),
                renderer=renderer,
                buttons=(
                    Button(name='add', css_class='btn btn-primary'),
                    Button(name='cancel', css_class='btn'),
                    ),
                )
            tmpl_vars['form'] = form.render()
        # Handle form submission
        list_view = self.request.route_url('admin.list', list='brevets')
        if 'cancel' in self.request.POST:
            return HTTPFound(list_view)
        if 'add' in self.request.POST or 'save' in self.request.POST:
            controls = self.request.POST.items()
            try:
                appstruct = form.validate(controls)
            except ValidationFailure as e:
                tmpl_vars['form'] = e.render()
                return tmpl_vars
            with transaction.manager:
                if 'add' in self.request.POST:
                    brevet = Brevet(
                        region=appstruct['region'],
                        distance=appstruct['distance'],
                        date_time=appstruct['date_time'],
                        route_name=appstruct['route_name'],
                        start_locn=appstruct['start_locn'],
                        organizer_email=appstruct['organizer_email'],
                        )
                    DBSession.add(brevet)
            return HTTPFound(list_view)
        return tmpl_vars


@view_config(
    route_name='admin.wranglers.create',
    renderer='admin/wrangler.mako',
    permission='admin',
    )
class WranglerCreate(FormView):
    schema = AdministratorSchema()
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

    def get_userid(self):
        return self.request.matchdict['item']

    def appstruct(self):
        return {'persona_email': self.get_userid()}

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
                .filter_by(persona_email=self.get_userid())
                .first())
            admin.persona_email = appstruct['persona_email']
        return HTTPFound(self.list_url())
