"""RandoPony brevet admin views.
"""
from deform import Button
from passlib.apps import custom_app_context
from pyramid_deform import FormView
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

from randopony.models import (
    Administrator,
    AdministratorSchema,
)
from randopony.models.meta import DBSession
from randopony import __pkg_metadata__ as version


@view_config(
    route_name='admin.wranglers.create',
    renderer='admin/wrangler.mako',
    permission='authenticated',
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
            'version': version.number + version.release,
            'list_url': self.list_url()
        })
        return tmpl_vars

    def add_success(self, appstruct):
        password_hash = custom_app_context.encrypt(appstruct['password'])
        admin = Administrator(appstruct['email'], password_hash)
        DBSession.add(admin)
        return HTTPFound(self.list_url())

    def failure(self, e):
        tmpl_vars = super(WranglerCreate, self).failure(e)
        tmpl_vars.update({
            'version': version.number + version.release,
            'list_url': self.list_url()
        })
        return tmpl_vars


@view_config(
    route_name='admin.wranglers.edit',
    renderer='admin/wrangler.mako',
    permission='authenticated',
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
        admin = (
            DBSession.query(Administrator)
            .filter_by(email=self.request.matchdict['item'])
            .one()
        )
        return {
            'id': admin.id,
            'email': admin.email,
        }

    def show(self, form):
        tmpl_vars = super(WranglerEdit, self).show(form)
        tmpl_vars.update({
            'version': version.number + version.release,
            'list_url': self.list_url()
        })
        return tmpl_vars

    def save_success(self, appstruct):
        admin = (
            DBSession.query(Administrator)
            .filter_by(id=appstruct['id'])
            .one()
        )
        admin.email = appstruct['email']
        admin.password_hash = custom_app_context.encrypt(appstruct['password'])
        return HTTPFound(self.list_url())

    def failure(self, e):
        tmpl_vars = super(WranglerEdit, self).failure(e)
        tmpl_vars.update({
            'version': version.number + version.release,
            'list_url': self.list_url()
        })
        return tmpl_vars
