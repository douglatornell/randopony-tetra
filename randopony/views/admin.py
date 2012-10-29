# -*- coding: utf-8 -*-
"""RandoPony admin views.
"""
from deform import Form
from pyramid.renderers import render
from pyramid.response import Response
from pyramid.view import (
    forbidden_view_config,
    view_config,
    )
from ..models import (
    Administrator,
    AdministratorSchema,
    DBSession,
    )


@forbidden_view_config()
def login(request):
    body = render('admin/login.mako', {'logout_btn': False}, request=request)
    return Response(body, status='403 Forbidden')


@view_config(route_name='admin.home', renderer='admin/home.mako',
     permission='admin')
def home(request):
    return {'logout_btn': True}


@view_config(route_name='admin.list', renderer='admin/list.mako',
    permission='admin')
def items_list(request):
    lists = {
        'wranglers': {
            'model': Administrator,
            'order_by': Administrator.persona_email,
            'action': 'edit',
            'list_title': 'Pony Wranglers',
        },
    }
    list_name = request.matchdict['list']
    params = lists[list_name]
    tmpl_vars = {
        'logout_btn': True,
        'items': DBSession.query(params['model']).order_by(params['order_by']),
        'action': params['action'],
        'list': list_name,
        'list_title': params['list_title'],
    }
    return tmpl_vars


@view_config(route_name='admin.wranglers',
    renderer='admin/wrangler.mako',
    permission='admin')
def wrangler_edit(request):
    admin = request.matchdict['item']
    if admin == 'new':
        form = Form(
            AdministratorSchema(), buttons=('add', 'cancel'))
        appstruct = {'persona_email': ''}
    else:
        form = Form(
            AdministratorSchema(), buttons=('save', 'cancel'))
        appstruct = {'persona_email': admin}
    tmpl_vars = {
        'logout_btn': True,
        'form': form.render(appstruct),
    }
    return tmpl_vars
