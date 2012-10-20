# -*- coding: utf-8 -*-
"""RandoPony admin views.
"""
from pyramid.exceptions import Forbidden
from pyramid.response import Response
from pyramid.security import authenticated_userid
from pyramid.view import view_config


@view_config(route_name='admin')
def admin_home(request):
    userid = authenticated_userid(request)
    if userid is None:
        raise Forbidden()
    return Response('Hello {}'.format(userid))
