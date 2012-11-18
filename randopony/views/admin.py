# -*- coding: utf-8 -*-
"""RandoPony admin views.
"""
from deform import (
    Form,
    ValidationFailure,
    )
from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import render
from pyramid.response import Response
from pyramid.view import (
    forbidden_view_config,
    view_config,
    view_defaults,
    )
import transaction
from ..models import (
    Administrator,
    AdministratorSchema,
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
            'items': DBSession.query(params['model']).order_by(params['order_by']),
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

    @view_config(route_name='admin.wranglers', renderer='admin/wrangler.mako')
    def wrangler(self):
        """Wrangler (aka administrator) create/update form handler.
        """
        tmpl_vars = {'logout_btn': True}
        # Render create/update form
        userid = self.request.matchdict['item']
        if userid == 'new':
            form = Form(
                AdministratorSchema(),
                renderer=mako_renderer,
                buttons=('add', 'cancel'),
                )
            tmpl_vars['form'] = form.render()
        else:
            appstruct = {'persona_email': userid}
            form = Form(
                AdministratorSchema(),
                renderer=mako_renderer,
                buttons=('save', 'cancel'),
                )
            tmpl_vars['form'] = form.render(appstruct)
        # Handle form submission
        list_view = self.request.route_url('admin.list', list='wranglers')
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
                    admin = Administrator(appstruct['persona_email'])
                    DBSession.add(admin)
                else:
                    admin = DBSession.query(Administrator).\
                        filter_by(persona_email=userid).first()
                    admin.persona_email = appstruct['persona_email']
            return HTTPFound(list_view)
        return tmpl_vars


def mako_renderer(tmpl_name, **kwargs):
    return render('{}.mako'.format(tmpl_name), kwargs)
