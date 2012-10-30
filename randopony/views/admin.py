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


@view_config(route_name='admin.delete', renderer='admin/confirm_delete.mako',
    permission='admin')
def delete(request):
    """Delete the specified list item, after confirmation.
    """
    list_name = request.matchdict['list']
    item = request.matchdict['item']
    # Render confirmation form
    lists = {
        'wranglers': {
            'model': Administrator,
            'item_type': 'administrator',
            'criterion': Administrator.persona_email == item,
        },
    }
    params = lists[list_name]
    tmpl_vars = {
        'logout_btn': True,
        'list': list_name,
        'item': item,
        'item_type': params['item_type'],
    }
    # Handle form submission
    list_view = request.route_url('admin.list', list=list_name)
    if 'cancel' in request.POST:
        return HTTPFound(list_view)
    if 'delete' in request.POST:
        with transaction.manager:
            DBSession.query(params['model']).\
                filter(params['criterion']).delete()
        return HTTPFound(list_view)
    return tmpl_vars


@view_config(route_name='admin.wranglers', renderer='admin/wrangler.mako',
    permission='admin')
def wrangler(request):
    """Wrangler (aka administrator) create/update form handler.
    """
    tmpl_vars = {'logout_btn': True}
    # Render create/update form
    userid = request.matchdict['item']
    if userid == 'new':
        form = Form(
            AdministratorSchema(), buttons=('add', 'cancel'))
        tmpl_vars['form'] = form.render()
    else:
        appstruct = {'persona_email': userid}
        form = Form(
            AdministratorSchema(), buttons=('save', 'cancel'))
        tmpl_vars['form'] = form.render(appstruct)
    # Handle form submission
    list_view = request.route_url('admin.list', list='wranglers')
    if 'cancel' in request.POST:
        return HTTPFound(list_view)
    if 'add' in request.POST or 'save' in request.POST:
        controls = request.POST.items()
        try:
            appstruct = form.validate(controls)
        except ValidationFailure as e:
            tmpl_vars['form'] = e.render()
            return tmpl_vars
        with transaction.manager:
            if 'add' in request.POST:
                admin = Administrator(appstruct['persona_email'])
                DBSession.add(admin)
            else:
                admin = DBSession.query(Administrator).\
                    filter_by(persona_email=userid).first()
                admin.persona_email = appstruct['persona_email']
        return HTTPFound(list_view)
    return tmpl_vars
