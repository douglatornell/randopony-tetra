# -*- coding: utf-8 -*-
"""RandoPony public site populaire views.
"""
from datetime import (
    datetime,
    timedelta,
)
import logging
from operator import attrgetter
from celery.task import task
from deform import Button
from gdata.spreadsheet.service import SpreadsheetsService
from pyramid_deform import FormView
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
)
from pyramid_mailer import get_mailer
from pyramid_mailer.message import Message
from pyramid.renderers import render
from pyramid.response import Response
from pyramid.view import view_config
import pytz
from .core import SiteViews
from ..admin.google_drive import google_drive_login
from ...models import (
    Brevet,
    EmailAddress,
    Link,
    Populaire,
    PopulaireEntrySchema,
    PopulaireRider,
)
from ...models.meta import DBSession


log = logging.getLogger(__name__)


def get_populaire(short_name):
    populaire = (
        DBSession.query(Populaire)
        .filter_by(short_name=short_name)
        .first()
    )
    return populaire


class PopulaireViews(SiteViews):
    """Views for populaires section of RandoPony public site
    """
    def __init__(self, request):
        super(PopulaireViews, self).__init__(request)
        self.tz = pytz.timezone(request.registry.settings['timezone'])
        try:
            self.populaire = get_populaire(request.matchdict['short_name'])
        except KeyError:
            self.populaire = None
        self.tmpl_vars.update({'active_tab': 'populaires'})

    @view_config(route_name='populaire.list', renderer='populaire-list.mako')
    def populaire_list(self):
        admin_email = (
            DBSession.query(EmailAddress)
            .filter_by(key='admin_email')
            .one()
        )
        self.tmpl_vars.update({'admin_email': admin_email.email})
        return self.tmpl_vars

    @view_config(route_name='populaire', renderer='populaire.mako')
    def populaire_page(self):
        if self._in_past():
            body = self._moved_on_page()
            return Response(body, status='200 OK')
        self.tmpl_vars.update({
            'populaire': self.populaire,
            'registration_closed': self._registration_closed,
            'event_started': self._event_started,
        })
        return self.tmpl_vars

    @view_config(route_name='populaire.rider_emails', renderer='string')
    def rider_emails(self):
        populaire = get_populaire(self.request.matchdict['short_name'])
        uuid = self.request.matchdict['uuid']
        if uuid != str(populaire.uuid) or self._in_past():
            raise HTTPNotFound
        return (', '.join(rider.email for rider in populaire.riders)
                or 'No riders have registered yet!')

    @property
    def _registration_closed(self):
        utc_registration_end = (
            self.tz.localize(self.populaire.registration_end)
            .astimezone(pytz.utc))
        utc_now = pytz.utc.localize(datetime.utcnow())
        return utc_now > utc_registration_end

    @property
    def _event_started(self):
        utc_start_date_time = (
            self.tz.localize(self.populaire.date_time)
            .astimezone(pytz.utc))
        utc_now = pytz.utc.localize(datetime.utcnow())
        return utc_now > utc_start_date_time

    def _in_past(self, recent_days=7):
        today = datetime.today()
        today = today.replace(hour=0, minute=0, second=0, microsecond=0)
        days_ago = today - timedelta(days=recent_days)
        return self.populaire.date_time < days_ago

    def _moved_on_page(self):
        results_link = (
            DBSession.query(Link.url)
            .filter_by(key='results_link')
            .one()[0]
        )
        body = render(
            'moved-on.mako',
            {
                'active_tab': 'populaires',
                'brevets': self.tmpl_vars['brevets'],
                'populaires': self.tmpl_vars['populaires'],
                'event': '{0} {0.date_time:%d-%b-%Y}'.format(self.populaire),
                'results_link': results_link,
            },
            request=self.request)
        return body


@view_config(
    route_name='populaire.entry',
    renderer='populaire-entry.mako',
)
class PopulaireEntry(FormView):
    def maybe_include_distance(node, kw):
        if not kw.get('include_distance'):
            del node['distance']

    schema = PopulaireEntrySchema(after_bind=maybe_include_distance)
    buttons = (
        Button(name='register', css_class='btn btn-primary'),
        Button(name='cancel', css_class='btn', type='reset'),
    )

    def _redirect_url(self, short_name):
        return self.request.route_url('populaire', short_name=short_name)

    def get_bind_data(self):
        data = super(PopulaireEntry, self).get_bind_data()
        populaire = get_populaire(self.request.matchdict['short_name'])
        distances = [
            (int(d.split()[0]), d.strip())
            for d in populaire.distance.split(',')
        ]
        data.update({
            'distances': distances,
            'include_distance': len(distances) > 1,
        })
        return data

    def show(self, form):
        tmpl_vars = super(PopulaireEntry, self).show(form)
        populaire = get_populaire(self.request.matchdict['short_name'])
        tmpl_vars.update({
            'active_tab': 'populaires',
            'brevets': Brevet.get_current(),
            'populaires': Populaire.get_current(),
            'populaire': populaire,
            'cancel_url': self._redirect_url(
                self.request.matchdict['short_name']),
        })
        return tmpl_vars

    def register_success(self, appstruct):
        pop_short_name = self.request.matchdict['short_name']
        populaire = get_populaire(pop_short_name)
        # Check for rider already registered
        rider = (
            DBSession.query(PopulaireRider)
            .filter_by(
                email=appstruct['email'],
                first_name=appstruct['first_name'],
                last_name=appstruct['last_name'],
                populaire=populaire.id,
            )
            .first()
        )
        if rider is not None:
            # Rider with same name and email is already registered
            self.request.session.flash('duplicate')
            self.request.session.flash(
                ' '.join((rider.first_name, rider.last_name)))
            self.request.session.flash(rider.email)
        else:
            # New rider registration
            mailer = get_mailer(self.request)
            try:
                distance = appstruct['distance']
            except KeyError:
                distance = populaire.distance.split()[0]
            rider = PopulaireRider(
                email=appstruct['email'],
                first_name=appstruct['first_name'],
                last_name=appstruct['last_name'],
                distance=distance,
                comment=appstruct['comment'],
            )
            populaire.riders.append(rider)
            DBSession.add(rider)
            update_google_spreadsheet.delay(
                sorted(
                    populaire.riders, key=attrgetter('lowercase_last_name')),
                populaire.google_doc_id.split(':')[1],
                self.request.registry.settings['google_drive.username'],
                self.request.registry.settings['google_drive.password'],
            )
            message = self._rider_message(populaire, rider)
            mailer.send(message)
            message = self._organizer_message(populaire, rider)
            mailer.send(message)
            self.request.session.flash('success')
            self.request.session.flash(rider.email)
        return HTTPFound(self._redirect_url(pop_short_name))

    def failure(self, e):
        tmpl_vars = super(PopulaireEntry, self).failure(e)
        populaire = get_populaire(self.request.matchdict['short_name'])
        tmpl_vars.update({
            'active_tab': 'populaires',
            'brevets': Brevet.get_current(),
            'populaires': Populaire.get_current(),
            'populaire': populaire,
            'cancel_url': self._redirect_url(
                self.request.matchdict['short_name']),
        })
        return tmpl_vars

    def _rider_message(self, populaire, rider):
        from_randopony = (
            DBSession.query(EmailAddress)
            .filter_by(key='from_randopony')
            .first().email
        )
        pop_page_url = self._redirect_url(populaire.short_name)
        message = Message(
            subject='Pre-registration Confirmation for {0}'
                    .format(populaire),
            sender=from_randopony,
            recipients=[rider.email],
            extra_headers={
                'Sender': from_randopony,
                'Reply-To': populaire.organizer_email,
            },
            body=render(
                'email/populaire_rider.mako',
                {
                    'populaire': populaire,
                    'pop_page_url': pop_page_url,
                }))
        return message

    def _organizer_message(self, populaire, rider):
        from_randopony = (
            DBSession.query(EmailAddress)
            .filter_by(key='from_randopony')
            .first().email
        )
        pop_page_url = self._redirect_url(populaire.short_name)
        rider_list_url = (
            'https://spreadsheets.google.com/ccc?key={0}'
            .format(populaire.google_doc_id.split(':')[1]))
        rider_emails = self.request.route_url(
            'populaire.rider_emails',
            short_name=populaire.short_name,
            uuid=populaire.uuid)
        admin_email = (
            DBSession.query(EmailAddress)
            .filter_by(key='admin_email')
            .first().email
        )
        message = Message(
            subject='{0} has Pre-registered for the {1}'
                    .format(rider, populaire),
            sender=from_randopony,
            recipients=[
                addr.strip() for addr in populaire.organizer_email.split(',')],
            body=render(
                'email/populaire_organizer_entry.mako',
                {
                    'rider': rider,
                    'populaire': populaire,
                    'pop_page_url': pop_page_url,
                    'rider_list_url': rider_list_url,
                    'rider_emails': rider_emails,
                    'admin_email': admin_email,
                }))
        return message


@task(ignore_result=True)
def update_google_spreadsheet(riders, doc_key, username, password):
    client = google_drive_login(SpreadsheetsService, username, password)
    spreadsheet_list = client.GetListFeed(doc_key)
    spreadsheet_rows = len(spreadsheet_list.entry)
    # Update the rows already in the spreadsheet
    for row, rider in enumerate(riders[:spreadsheet_rows]):
        rider_number = row + 1
        new_row_data = _make_spreadsheet_row_dict(rider_number, rider)
        client.UpdateRow(spreadsheet_list.entry[row], new_row_data)
    # Add remaining rows
    for row, rider in enumerate(riders[spreadsheet_rows:]):
        rider_number = spreadsheet_rows + row + 1
        row_data = _make_spreadsheet_row_dict(rider_number, rider)
        client.InsertRow(row_data, doc_key)


def _make_spreadsheet_row_dict(rider_number, rider):
    row_data = {
        'ridernumber': str(rider_number),
        'lastname': rider.last_name,
        'firstname': rider.first_name,
        'distance': str(rider.distance),
    }
    return row_data
