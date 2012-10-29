# -*- coding: utf-8 -*-
"""RandoPony admin views.
"""
from pyramid.renderers import render
from pyramid.response import Response
from pyramid.view import (
    forbidden_view_config,
    view_config,
    )
from ..models import (
    DBSession,
    Administrator,
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
        },
    }
    tmpl_vars = {'logout_btn': True}
    list_name = request.matchdict['list']
    params = lists[list_name]
    items = DBSession.query(params['model']).\
        order_by(params['order_by'])
    tmpl_vars.update({
        'items': items, 'action': params['action'], 'list': list_name})
    return tmpl_vars


@view_config(route_name='admin.wranglers.edit',
    renderer='string',
    permission='admin')
def wrangler_edit(request):
    admin = request.matchdict['item']
    return 'wrangler edit stub for {}'.format(admin)
