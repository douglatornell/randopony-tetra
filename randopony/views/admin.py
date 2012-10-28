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
def admin_login(request):
    body = render('admin/login.mako', {'logout_btn': False}, request=request)
    return Response(body, status='403 Forbidden')


@view_config(route_name='admin.home', renderer='admin/home.mako',
             permission='admin')
def admin_home(request):
    return {'logout_btn': True}


@view_config(route_name='admin.brevets', renderer='string',
             permission='admin')
def admin_brevets(request):
    return 'brevets stub'


@view_config(route_name='admin.club_events', renderer='string',
             permission='admin')
def admin_club_events(request):
    return 'club events stub'


@view_config(route_name='admin.populaires', renderer='string',
             permission='admin')
def admin_populaires(request):
    return 'populaires stub'


@view_config(route_name='admin.wranglers',
    renderer='admin/wranglers.mako',
    permission='admin')
def admin_wranglers(request):
    tmpl_vars = {'logout_btn': True}
    wranglers = DBSession.query(Administrator).\
        order_by(Administrator.persona_email)
    tmpl_vars.update({'wranglers': wranglers})
    return tmpl_vars


@view_config(route_name='admin.wrangler.edit',
    renderer='string',
    permission='admin')
def admin_wrangler_edit(request):
    admin = request.matchdict['item']
    return 'wrangler edit stub for {}'.format(admin)
