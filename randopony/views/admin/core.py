# -*- coding: utf-8 -*-
"""RandoPony admin views core components.
"""
from datetime import (
    datetime,
    timedelta,
    )
from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import render
from pyramid.response import Response
from pyramid.view import (
    forbidden_view_config,
    view_config,
    view_defaults,
    )
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message
from sqlalchemy import desc
from .populaire import get_populaire
from ...models import (
    Administrator,
    Brevet,
    EmailAddress,
    Populaire,
    )
from ...models.meta import DBSession
from ... import __version__ as version


@forbidden_view_config()
def login(request):
    body = render(
        'admin/login.mako',
        {
            'version': version.number + version.release,
            'logout_btn': False
        },
        request=request)
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
        self.tmpl_vars = {
            'version': version.number + version.release,
            'logout_btn': True,
        }

    @view_config(route_name='admin.home', renderer='admin/home.mako')
    def home(self):
        return self.tmpl_vars

    @view_config(route_name='admin.list', renderer='admin/list.mako')
    def items_list(self):
        list_name = self.request.matchdict['list']
        params = self.lists[list_name]
        self.tmpl_vars.update({
            'version': version.number + version.release,
            'logout_btn': True,
            'items': (DBSession.query(params['model'])
                .order_by(params['order_by'])),
            'action': params['action'],
            'list': list_name,
            'list_title': params['list_title'],
        })
        return self.tmpl_vars

    @view_config(route_name='admin.delete',
        renderer='admin/confirm_delete.mako')
    def delete(self):
        """Delete the specified list item, after confirmation.
        """
        list_name = self.request.matchdict['list']
        item = self.request.matchdict['item']
        # Render confirmation form
        params = self.lists[list_name]
        self.tmpl_vars.update({
            'version': version.number + version.release,
            'logout_btn': True,
            'list': list_name,
            'item': item,
            'item_type': params['item_type'],
        })
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
        return self.tmpl_vars


def get_brevet(code, date):
    region = code[:2]
    distance = code[2:]
    date = datetime.strptime(date, '%d%b%Y')
    return (DBSession.query(Brevet)
        .filter_by(region=region)
        .filter_by(distance=distance)
        .filter(Brevet.date_time >= date)
        .filter(Brevet.date_time < date + timedelta(days=1))
        .first()
        )


def email_to_organizer(request, event, event_page_url, rider_emails_url):
    if not event.google_doc_id:
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
    rider_list_url = (
        'https://spreadsheets.google.com/ccc?key={0}'
        .format(event.google_doc_id.split(':')[1]))
    admin_email = (
        DBSession.query(EmailAddress)
        .filter_by(key='admin_email')
        .first().email
        )
    message = Message(
        subject='RandoPony URLs for {}'.format(event),
        sender=from_randopony,
        recipients=[
            addr.strip() for addr in event.organizer_email.split(',')],
        body=render(
            'email/event_URLs_to_organizer.mako',
            {
                'event': str(event),
                'event_page_url': event_page_url,
                'rider_list_url': rider_list_url,
                'rider_emails_url': rider_emails_url,
                'admin_email': admin_email,
            }))
    mailer = get_mailer(request)
    mailer.send(message)
    return [
        'success',
        'Email sent to {} organizer(s)'.format(event),
    ]


def email_to_webmaster(request, event, event_page_url):
    from_randopony = (
        DBSession.query(EmailAddress)
        .filter_by(key='from_randopony')
        .first().email
        )
    club_webmaster = (
        DBSession.query(EmailAddress)
        .filter_by(key='club_webmaster').first().email)
    admin_email = (
        DBSession.query(EmailAddress)
        .filter_by(key='admin_email')
        .first().email
        )
    message = Message(
        subject='RandoPony Pre-registration page for {}'.format(event),
        sender=from_randopony,
        recipients=[club_webmaster],
        body=render(
            'email/event_URL_to_webmaster.mako',
            {
                'event': str(event),
                'event_page_url': event_page_url,
                'admin_email': admin_email,
            }))
    mailer = get_mailer(request)
    mailer.send(message)
    return [
        'success',
        'Email with {} page URL sent to webmaster'.format(event),
    ]


def finalize_flash_msg(request, flash):
    if 'error' in flash:
        request.session.flash('error')
    else:
        request.session.flash('success')
    for msg in flash:
        if msg not in 'success error'.split():
            request.session.flash(msg)
