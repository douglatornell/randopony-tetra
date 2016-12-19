"""RandoPony populaire admin views.
"""
from deform import Button
# from gdata.docs.client import DocsClient
from pyramid_deform import FormView
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message
from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import render
from pyramid.view import view_config
# from randopony.views.admin import google_drive
from randopony.views.admin import core as admin_core
from randopony.models import (
    EmailAddress,
    Populaire,
    PopulaireSchema,
)
from randopony.models.meta import DBSession
from randopony import __pkg_metadata__ as version


@view_config(
    route_name='admin.populaires.view',
    renderer='admin/populaire.mako',
    permission='authenticated',
)
def populaire_details(request):
    short_name = request.matchdict['item']
    populaire = admin_core.get_populaire(short_name)
    return {
        'version': version.number + version.release,
        'populaire': populaire,
    }


@view_config(
    route_name='admin.populaires.create',
    renderer='admin/populaire_edit.mako',
    permission='authenticated',
)
class PopulaireCreate(FormView):
    schema = PopulaireSchema()
    for field in 'id start_map_url'.split():
        schema.__delitem__(field)
    buttons = (
        Button(name='add', css_class='btn btn-primary'),
        Button(name='cancel', css_class='btn', type='reset'),
    )

    def list_url(self):
        return self.request.route_url('admin.list', list='populaires')

    def show(self, form):
        tmpl_vars = super(PopulaireCreate, self).show(form)
        tmpl_vars.update({
            'version': version.number + version.release,
            'cancel_url': self.list_url()
        })
        return tmpl_vars

    def add_success(self, appstruct):
        populaire = Populaire(
            event_name=appstruct['event_name'],
            short_name=appstruct['short_name'],
            distance=appstruct['distance'],
            date_time=appstruct['date_time'],
            start_locn=appstruct['start_locn'],
            organizer_email=appstruct['organizer_email'],
            registration_end=appstruct['registration_end'],
            entry_form_url=appstruct['entry_form_url'],
        )
        DBSession.add(populaire)
        return HTTPFound(
            self.request.route_url('admin.populaires.view', item=populaire))

    def failure(self, e):
        tmpl_vars = super(PopulaireCreate, self).failure(e)
        tmpl_vars.update({
            'version': version.number + version.release,
            'cancel_url': self.list_url()
        })
        return tmpl_vars


@view_config(
    route_name='admin.populaires.edit',
    renderer='admin/populaire_edit.mako',
    permission='authenticated',
)
class PopulaireEdit(FormView):
    schema = PopulaireSchema()
    buttons = (
        Button(name='save', css_class='btn btn-primary'),
        Button(name='cancel', css_class='btn', type='reset'),
    )

    def _redirect_url(self, item):
        return self.request.route_url('admin.populaires.view', item=item)

    def appstruct(self):
        short_name = self.request.matchdict['item']
        populaire = admin_core.get_populaire(short_name)
        return {
            'id': populaire.id,
            'event_name': populaire.event_name,
            'short_name': populaire.short_name,
            'distance': populaire.distance,
            'date_time': populaire.date_time,
            'start_locn': populaire.start_locn,
            'start_map_url': populaire.start_map_url,
            'organizer_email': populaire.organizer_email,
            'registration_end': populaire.registration_end,
            'entry_form_url': populaire.entry_form_url,
        }

    def show(self, form):
        tmpl_vars = super(PopulaireEdit, self).show(form)
        tmpl_vars.update({
            'version': version.number + version.release,
            'cancel_url': self._redirect_url(self.request.matchdict['item']),
        })
        return tmpl_vars

    def save_success(self, appstruct):
        populaire = (
            DBSession.query(Populaire)
            .filter_by(id=appstruct['id'])
            .one()
        )
        populaire.event_name = appstruct['event_name']
        populaire.short_name = appstruct['short_name']
        populaire.distance = appstruct['distance']
        populaire.date_time = appstruct['date_time']
        populaire.start_locn = appstruct['start_locn']
        populaire.start_map_url = appstruct['start_map_url']
        populaire.organizer_email = appstruct['organizer_email']
        populaire.registration_end = appstruct['registration_end']
        populaire.entry_form_url = appstruct['entry_form_url']
        return HTTPFound(self._redirect_url(populaire))

    def failure(self, e):
        tmpl_vars = super(PopulaireEdit, self).failure(e)
        tmpl_vars.update({
            'version': version.number + version.release,
            'cancel_url': self._redirect_url(self.request.matchdict['item']),
        })
        return tmpl_vars


@view_config(
    route_name='admin.populaires.create_rider_list',
    permission='authenticated',
)
def create_rider_list(request):
    short_name = request.matchdict['item']
    populaire = admin_core.get_populaire(short_name)
    flash = _create_rider_list(request, populaire)
    admin_core.finalize_flash_msg(request, flash)
    redirect_url = request.route_url('admin.populaires.view', item=short_name)
    return HTTPFound(redirect_url)


def _create_rider_list(request, populaire):
    """Actual creation of rider list spreadsheet on Google Drive.

    For use by :func:`create_rider_list` and :func:`setup_123` views.
    """
    username = request.registry.settings['google_drive.username']
    password = request.registry.settings['google_drive.password']
    flash = google_drive.create_rider_list(
        populaire, 'Populaire Rider List Template', username, password)
    return flash


@view_config(
    route_name='admin.populaires.email_to_organizer',
    permission='authenticated',
)
def email_to_organizer(request):
    short_name = request.matchdict['item']
    populaire = admin_core.get_populaire(short_name)
    _email_to_organizer(request, populaire)
    redirect_url = request.route_url('admin.populaires.view', item=short_name)
    return HTTPFound(redirect_url)


def _email_to_organizer(request, populaire):
    """Actual sending of email to populaire organizer(s) to notify them of
    event URLs, etc..

    For use by :func:`email_to_organizer` and :func:`setup_123` views.
    """
    event_page_url = request.route_url(
        'populaire', short_name=populaire.short_name)
    rider_emails_url = request.route_url(
        'populaire.rider_emails',
        short_name=populaire.short_name,
        uuid=populaire.uuid)
    flash = admin_core.email_to_organizer(
        request, populaire, event_page_url, rider_emails_url)
    return flash


@view_config(
    route_name='admin.populaires.email_to_webmaster',
    permission='authenticated',
)
def email_to_webmaster(request):
    short_name = request.matchdict['item']
    populaire = admin_core.get_populaire(short_name)
    _email_to_webmaster(request, populaire)
    redirect_url = request.route_url('admin.populaires.view', item=short_name)
    return HTTPFound(redirect_url)


def _email_to_webmaster(request, populaire):
    """Actual sending of email to club webmaster to notify them of
    event URLs, etc.

    For use by :func:`email_to_webmaster` and :func:`setup_123` views.
    """
    event_page_url = request.route_url(
        'populaire', short_name=populaire.short_name)
    flash = admin_core.email_to_webmaster(request, populaire, event_page_url)
    return flash


@view_config(
    route_name='admin.populaires.setup_123',
    permission='authenticated',
)
def setup_123(request):
    short_name = request.matchdict['item']
    populaire = admin_core.get_populaire(short_name)
    flash = _create_rider_list(request, populaire)
    if 'error' not in flash:
        flash += _email_to_organizer(request, populaire)
        flash += _email_to_webmaster(request, populaire)
    admin_core.finalize_flash_msg(request, flash)
    redirect_url = request.route_url('admin.populaires.view', item=short_name)
    return HTTPFound(redirect_url)
