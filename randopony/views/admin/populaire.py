# -*- coding: utf-8 -*-
"""RandoPony populaire admin views.
"""
from deform import Button
from gdata.docs.client import DocsClient
from pyramid_deform import FormView
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message
from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import render
from pyramid.view import view_config
from .google_drive import (
    google_drive_login,
    get_rider_list_template,
    share_rider_list_publicly,
    )
from ...models import (
    EmailAddress,
    Populaire,
    PopulaireSchema,
    )
from ...models.meta import DBSession


def get_populaire(short_name):
    return (DBSession.query(Populaire)
        .filter_by(short_name=short_name)
        .first()
        )


@view_config(
    route_name='admin.populaires.view',
    renderer='admin/populaire.mako',
    permission='admin',
    )
def populaire_details(request):
    short_name = request.matchdict['item']
    populaire = get_populaire(short_name)
    return {
        'logout_btn': True,
        'populaire': populaire,
        }


@view_config(
    route_name='admin.populaires.create',
    renderer='admin/populaire_edit.mako',
    permission='admin',
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
            'logout_btn': True,
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
            'logout_btn': True,
            'cancel_url': self.list_url()
            })
        return tmpl_vars


@view_config(
    route_name='admin.populaires.edit',
    renderer='admin/populaire_edit.mako',
    permission='admin',
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
        populaire = get_populaire(short_name)
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
            'logout_btn': True,
            'cancel_url': self._redirect_url(self.request.matchdict['item']),
            })
        return tmpl_vars

    def save_success(self, appstruct):
        populaire = (DBSession.query(Populaire)
            .filter_by(id=appstruct['id'])
            .one())
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
            'logout_btn': True,
            'cancel_url': self._redirect_url(self.request.matchdict['item']),
            })
        return tmpl_vars


@view_config(
    route_name='admin.populaires.create_rider_list',
    permission='admin',
    )
def create_rider_list(request):
    short_name = request.matchdict['item']
    populaire = get_populaire(short_name)
    _create_rider_list(request, populaire)
    redirect_url = request.route_url('admin.populaires.view', item=short_name)
    return HTTPFound(redirect_url)


def _create_rider_list(request, populaire):
    if populaire.google_doc_id:
        request.session.flash('error')
        request.session.flash('Rider list spreadsheet already created')
        return 'error'
    google_doc_id = _create_google_drive_list(populaire, request)
    populaire.google_doc_id = google_doc_id
    request.session.flash('success')
    request.session.flash('Rider list spreadsheet created')
    return 'success'


def _create_google_drive_list(populaire, request):      # pragma: no cover
    """Execute Google Drive operations to create rider list from template,
    and share it publicly.

    Returns the id of the created document that is used to construct its
    URL.
    """
    client = google_drive_login(
        DocsClient,
        request.registry.settings['google_drive.username'],
        request.registry.settings['google_drive.password'])
    template = get_rider_list_template('Populaire Rider List Template', client)
    created_doc = client.copy_resource(
        template, '{0} {0.date_time:%d-%b-%Y}'.format(populaire))
    share_rider_list_publicly(created_doc, client)
    return created_doc.resource_id.text


@view_config(
    route_name='admin.populaires.email_to_organizer',
    permission='admin',
    )
def email_to_organizer(request):
    short_name = request.matchdict['item']
    populaire = get_populaire(short_name)
    _email_to_organizer(request, populaire)
    redirect_url = request.route_url('admin.populaires.view', item=short_name)
    return HTTPFound(redirect_url)


def _email_to_organizer(request, populaire):
    if not populaire.google_doc_id:
        request.session.flash('error')
        request.session.flash(
            'Google Drive rider list must be created before email to '
            'organizer(s) can be sent')
        return
    from_randopony = (
        DBSession.query(EmailAddress)
        .filter_by(key='from_randopony')
        .first().email
        )
    pop_page_url = request.route_url(
        'populaire', short_name=populaire.short_name)
    rider_list_url = (
        'https://spreadsheets.google.com/ccc?key={0}'
        .format(populaire.google_doc_id.split(':')[1]))
    rider_emails_url = request.route_url(
        'populaire.rider_emails',
        short_name=populaire.short_name,
        uuid=populaire.uuid)
    admin_email = (
        DBSession.query(EmailAddress)
        .filter_by(key='admin_email')
        .first().email
        )
    message = Message(
        subject='RandoPony URLs for {.event_name}'.format(populaire),
        sender=from_randopony,
        recipients=[
            addr.strip() for addr in populaire.organizer_email.split(',')],
        body=render(
            'email/populaire_URLs_to_organizer.mako',
            {
                'populaire': populaire.event_name,
                'pop_page_url': pop_page_url,
                'rider_list_url': rider_list_url,
                'rider_emails_url': rider_emails_url,
                'admin_email': admin_email,
            }))
    mailer = get_mailer(request)
    mailer.send(message)
    request.session.flash('success')
    request.session.flash(
        'Email sent to {} organizer(s)'.format(populaire.short_name))


@view_config(
    route_name='admin.populaires.email_to_webmaster',
    permission='admin',
    )
def email_to_webmaster(request):
    short_name = request.matchdict['item']
    populaire = get_populaire(short_name)
    _email_to_webmaster(request, populaire)
    redirect_url = request.route_url('admin.populaires.view', item=short_name)
    return HTTPFound(redirect_url)


def _email_to_webmaster(request, populaire):
    from_randopony = (
        DBSession.query(EmailAddress)
        .filter_by(key='from_randopony')
        .first().email
        )
    club_webmaster = (
        DBSession.query(EmailAddress)
        .filter_by(key='club_webmaster').first().email)
    pop_page_url = request.route_url(
        'populaire', short_name=populaire.short_name)
    admin_email = (
        DBSession.query(EmailAddress)
        .filter_by(key='admin_email')
        .first().email
        )
    message = Message(
        subject='RandoPony Pre-registration page for {.event_name}'
                .format(populaire),
        sender=from_randopony,
        recipients=[club_webmaster],
        body=render(
            'email/event_URL_to_webmaster.mako',
            {
                'event': populaire.event_name,
                'event_page_url': pop_page_url,
                'admin_email': admin_email,
            }))
    mailer = get_mailer(request)
    mailer.send(message)
    request.session.flash('success')
    request.session.flash(
        'Email with {} page URL sent to webmaster'
        .format(populaire.short_name))


@view_config(
    route_name='admin.populaires.setup_123',
    permission='admin',
    )
def setup_123(request):
    short_name = request.matchdict['item']
    populaire = get_populaire(short_name)
    result = _create_rider_list(request, populaire)
    if result == 'success':
        _email_to_organizer(request, populaire)
        _email_to_webmaster(request, populaire)
        # Rewrite flash message list with only 1 success element
        flash = request.session.pop_flash()
        request.session.flash('success')
        for msg in flash:
            if msg != 'success':
                request.session.flash(msg)
    redirect_url = request.route_url('admin.populaires.view', item=short_name)
    return HTTPFound(redirect_url)
