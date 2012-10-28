# -*- coding: utf-8 -*-
"""RandoPony admin views.
"""
from pyramid.renderers import render
from pyramid.response import Response
from pyramid.security import authenticated_userid
from pyramid.view import (
    forbidden_view_config,
    view_config,
    )


@forbidden_view_config()
def admin_login(request):
    body = render('admin/login.mako', {'logout_btn': False}, request=request)
    return Response(body, status='403 Forbidden')


@view_config(route_name='admin.home', renderer='admin/home.mako',
             permission='admin')
def admin_home(request):
    userid = authenticated_userid(request)
    return {'logout_btn': True, 'user': userid}
