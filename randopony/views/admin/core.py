# -*- coding: utf-8 -*-
"""RandoPony admin views core components.
"""
from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import render
from pyramid.response import Response
from pyramid.view import (
    forbidden_view_config,
    view_config,
    view_defaults,
    )
from sqlalchemy import desc
from .brevet import get_brevet
from .populaire import get_populaire
from ...models import (
    Administrator,
    Brevet,
    Populaire,
    )
from ...models.meta import DBSession


@forbidden_view_config()
def login(request):
    body = render('admin/login.mako', {'logout_btn': False}, request=request)
    return Response(body, status='403 Forbidden')


@view_defaults(permission='admin')
class AdminViews(object):
    """Views for the RandoPony admin interface.
    """
    lists = {
        'brevets': {
            'model': Brevet,
            'item_type': 'brevet',
            'list_title': 'Brevets',
            'order_by': desc(Brevet.date_time),
            'action': 'view',
        },
        'populaires': {
            'model': Populaire,
            'item_type': 'populaire',
            'list_title': 'Populaires',
            'order_by': desc(Populaire.date_time),
            'action': 'view',
        },
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
            elif list_name == 'populaires':
                criterion = Populaire.id == get_populaire(item).id
            elif list_name == 'wranglers':
                criterion = Administrator.persona_email == item
            (DBSession.query(params['model'])
                .filter(criterion)
                .delete())
            return HTTPFound(list_view)
        return tmpl_vars
