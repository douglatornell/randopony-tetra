# -*- coding: utf-8 -*-
"""RandoPony public site brevet views.
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
import requests
from .core import SiteViews
from ..admin.google_drive import google_drive_login
from ...models import (
    Brevet,
    BrevetEntrySchema,
    BrevetRider,
    EmailAddress,
    Link,
    Populaire,
)
from ...models.meta import DBSession


log = logging.getLogger(__name__)


def get_brevet(region, distance, date):
    brevet = (DBSession.query(Brevet)
              .filter_by(region=region, distance=distance)
              .filter(Brevet.date_time >= date)
              .filter(Brevet.date_time < date + timedelta(days=1))
              .first())
    return brevet


class BrevetViews(SiteViews):
    """Views for brevets section of RandoPony public site
    """
    def __init__(self, request):
        super(BrevetViews, self).__init__(request)
        self.tz = pytz.timezone(request.registry.settings['timezone'])
        try:
            self.brevet = get_brevet(
                request.matchdict['region'],
                int(request.matchdict['distance']),
                datetime.strptime(request.matchdict['date'], '%d%b%Y'),
            )
        except KeyError:
            self.brevet = None
        self.tmpl_vars.update({'active_tab': 'brevets'})

    @view_config(route_name='region.list', renderer='region-list.mako')
    @view_config(route_name='register', renderer='region-list.mako')
    def region_list(self):
        region_brevets = {}
        for region in Brevet.REGIONS.keys():
            region_brevets[region] = (
                self.tmpl_vars['brevets'].filter_by(region=region))
        admin_email = (DBSession.query(EmailAddress)
                       .filter_by(key='admin_email')
                       .one())
        self.tmpl_vars.update({
            'regions': Brevet.REGIONS,
            'region_brevets': region_brevets,
            'admin_email': admin_email.email,
        })
        return self.tmpl_vars

    @view_config(route_name='brevet.list', renderer='brevet-list.mako')
    @view_config(route_name='register.region', renderer='brevet-list.mako')
    def brevet_list(self):
        region = self.request.matchdict['region']
        region_brevets = (self.tmpl_vars['brevets']
                          .filter_by(region=region))
        images = {
            'HW': {
                'file': 'VI400UnionBay.jpg',
                'alt': 'Van Isle - Ocean and Mountains',
                'credit': 'John McGillivray',
            },
            '6K': {
                'file': 'SI600Cheryl.jpg',
                'alt': 'You and the Road in the Southern Interior',
                'credit': 'Nigel Press',
            },
            'LM': {
                'file': 'LowerMainlandQuartet.jpg',
                'alt': 'Harrison Hotsprings Road',
                'credit': 'Nobo Yonemitsu',
            },
            'SI': {
                'file': 'SouthIntLivestock.jpg',
                'alt': 'Southern Interior Peloton',
                'credit': 'Bud MacRae',
            },
            'VI': {
                'file': 'VanIsDuo.jpg',
                'alt': 'Van Isle Duo',
                'credit': 'Raymond Parker'},
        }
        self.tmpl_vars.update({
            'region': region,
            'regions': Brevet.REGIONS,
            'region_brevets': region_brevets,
            'image': images[region],
        })
        return self.tmpl_vars

    @view_config(route_name='brevet', renderer='brevet.mako')
    def brevet_page(self):
        if self.brevet is None:
            if self._maybe_coming_soon:
                body = self._coming_soon_page()
                return Response(body, status='200 OK')
            else:
                raise HTTPNotFound
        if self._in_past():
            body = self._moved_on_page()
            return Response(body, status='200 OK')
        entry_form_url = (
            DBSession.query(Link.url)
            .filter_by(key='entry_form')
            .one()[0])
        self.tmpl_vars.update({
            'brevet': self.brevet,
            'REGIONS': Brevet.REGIONS,
            'registration_closed': self._registration_closed,
            'event_started': self._event_started,
            'entry_form_url': entry_form_url,
        })
        return self.tmpl_vars

    @property
    def _maybe_coming_soon(self):
        brevet_date = datetime.strptime(
            self.request.matchdict['date'], '%d%b%Y')
        today = datetime.today()
        if today.month >= 11:
            return brevet_date.year in (today.year, today.year + 1)
        else:
            return brevet_date.year == today.year

    @property
    def _registration_closed(self):
        utc_registration_end = (
            self.tz.localize(self.brevet.registration_end)
            .astimezone(pytz.utc))
        utc_now = pytz.utc.localize(datetime.utcnow())
        return utc_now > utc_registration_end

    @property
    def _event_started(self):
        utc_start_date_time = (
            self.tz.localize(self.brevet.date_time)
            .astimezone(pytz.utc))
        utc_now = pytz.utc.localize(datetime.utcnow())
        return utc_now > utc_start_date_time

    def _in_past(self, recent_days=7):
        today = datetime.today()
        today = today.replace(hour=0, minute=0, second=0, microsecond=0)
        days_ago = today - timedelta(days=recent_days)
        return self.brevet.date_time < days_ago

    def _coming_soon_page(self):
        maybe_brevet = (
            '{0[region]}{0[distance]} {0[date]}'.format(self.request.matchdict))
        body = render(
            'coming-soon.mako',
            {
                'active_tab': 'brevets',
                'brevets': self.tmpl_vars['brevets'],
                'populaires': self.tmpl_vars['populaires'],
                'maybe_brevet': maybe_brevet,
            },
            request=self.request)
        return body

    def _moved_on_page(self):
        results_link = (
            DBSession.query(Link.url)
            .filter_by(key='results_link')
            .one()[0])
        results_link = results_link.format(
            year=str(self.brevet.date_time.year)[-2:])
        body = render(
            'moved-on.mako',
            {
                'active_tab': 'brevets',
                'brevets': self.tmpl_vars['brevets'],
                'populaires': self.tmpl_vars['populaires'],
                'event': self.brevet,
                'results_link': results_link,
            },
            request=self.request)
        return body


@view_config(route_name='brevet.entry', renderer='brevet-entry.mako')
class BrevetEntry(FormView):
    schema = BrevetEntrySchema()
    buttons = (
        Button(name='register', css_class='btn btn-primary'),
        Button(name='cancel', css_class='btn', type='reset'),
    )

    def _redirect_url(self, region, distance, date):
        return self.request.route_url(
            'brevet', region=region, distance=distance, date=date)

    def show(self, form):
        tmpl_vars = super(BrevetEntry, self).show(form)
        region = self.request.matchdict['region']
        distance = int(self.request.matchdict['distance'])
        date = self.request.matchdict['date']
        brevet = get_brevet(
            region, distance, datetime.strptime(date, '%d%b%Y'))
        tmpl_vars.update({
            'active_tab': 'brevets',
            'brevets': Brevet.get_current(),
            'populaires': Populaire.get_current(),
            'brevet': brevet,
            'cancel_url': self._redirect_url(region, distance, date),
        })
        return tmpl_vars

    def register_success(self, appstruct):
        region = self.request.matchdict['region']
        distance = int(self.request.matchdict['distance'])
        date = self.request.matchdict['date']
        brevet = get_brevet(
            region, distance, datetime.strptime(date, '%d%b%Y'))
        # Check for rider already registered
        rider = (
            DBSession.query(BrevetRider)
            .filter_by(
                email=appstruct['email'],
                first_name=appstruct['first_name'],
                last_name=appstruct['last_name'],
                brevet=brevet.id,
            )
            .first())
        if rider is not None:
            # Rider with same name and email is already registered
            self.request.session.flash('duplicate')
            self.request.session.flash(
                ' '.join((rider.first_name, rider.last_name)))
            self.request.session.flash(rider.email)
        else:
            # New rider registration
            mailer = get_mailer(self.request)
            first_name = appstruct['first_name']
            last_name = appstruct['last_name']
            is_club_member_url = _get_is_club_member_url()
            member_status = _get_member_status_by_name(
                first_name, last_name, is_club_member_url)
            rider = BrevetRider(
                email=appstruct['email'],
                first_name=first_name,
                last_name=last_name,
                comment=appstruct['comment'],
                member_status=member_status,
                bike_type=appstruct['bike_type'],
            )
            brevet.riders.append(rider)
            DBSession.add(rider)
            update_google_spreadsheet.delay(
                sorted(brevet.riders, key=attrgetter('lowercase_last_name')),
                brevet.google_doc_id.split(':')[1],
                self.request.registry.settings['google_drive.username'],
                self.request.registry.settings['google_drive.password'],
                is_club_member_url,
            )
            message = self._rider_message(brevet, rider)
            mailer.send(message)
            message = self._organizer_message(brevet, rider)
            mailer.send(message)
            membership_link = (
                DBSession.query(Link.url)
                .filter_by(key='membership_link')
                .one()[0])
            self.request.session.flash('success')
            self.request.session.flash(rider.email)
            self.request.session.flash(rider.member_status)
            self.request.session.flash(membership_link)
        return HTTPFound(self._redirect_url(region, distance, date))

    def failure(self, e):
        tmpl_vars = super(BrevetEntry, self).failure(e)
        region = self.request.matchdict['region']
        distance = int(self.request.matchdict['distance'])
        date = self.request.matchdict['date']
        brevet = get_brevet(
            region, distance, datetime.strptime(date, '%d%b%Y'))
        tmpl_vars.update({
            'active_tab': 'brevets',
            'brevets': Brevet.get_current(),
            'populaires': Populaire.get_current(),
            'brevet': brevet,
            'cancel_url': self._redirect_url(region, distance, date)
        })
        return tmpl_vars

    def _rider_message(self, brevet, rider):
        from_randopony = (
            DBSession.query(EmailAddress)
            .filter_by(key='from_randopony')
            .first().email
        )
        brevet_page_url = self._redirect_url(
            brevet.region, brevet.distance, brevet.date_time.strftime('%d%b%Y'))
        entry_form_url = (
            DBSession.query(Link.url)
            .filter_by(key='entry_form')
            .one()[0]
        )
        membership_link = (
            DBSession.query(Link.url)
            .filter_by(key='membership_link')
            .one()[0]
        )
        message = Message(
            subject='Pre-registration Confirmation for {0}'
                    .format(brevet),
            sender=from_randopony,
            recipients=[rider.email],
            extra_headers={
                'Sender': from_randopony,
                'Reply-To': brevet.organizer_email,
            },
            body=render(
                'email/brevet_rider.mako',
                {
                    'brevet': brevet,
                    'rider': rider,
                    'brevet_page_url': brevet_page_url,
                    'entry_form_url': entry_form_url,
                    'membership_link': membership_link,
                }))
        return message

    def _organizer_message(self, brevet, rider):
        from_randopony = (
            DBSession.query(EmailAddress)
            .filter_by(key='from_randopony')
            .first().email
        )
        date = brevet.date_time.strftime('%d%b%Y')
        brevet_page_url = self._redirect_url(
            brevet.region, brevet.distance, date)
        rider_list_url = (
            'https://spreadsheets.google.com/ccc?key={0}'
            .format(brevet.google_doc_id.split(':')[1]))
        rider_emails = self.request.route_url(
            'brevet.rider_emails',
            region=brevet.region,
            distance=brevet.distance,
            date=date,
            uuid=brevet.uuid,
        )
        admin_email = (
            DBSession.query(EmailAddress)
            .filter_by(key='admin_email')
            .first().email
        )
        message = Message(
            subject='{0} has Pre-registered for the {1}'
                    .format(rider, brevet),
            sender=from_randopony,
            recipients=[
                addr.strip() for addr in brevet.organizer_email.split(',')],
            body=render(
                'email/brevet_organizer_entry.mako',
                {
                    'rider': rider,
                    'brevet': brevet,
                    'brevet_page_url': brevet_page_url,
                    'rider_list_url': rider_list_url,
                    'rider_emails': rider_emails,
                    'admin_email': admin_email,
                }))
        return message


def _get_is_club_member_url():
    return (
        DBSession.query(Link.url)
        .filter_by(key='is_club_member_api')
        .one()[0]
    )


def _get_member_status_by_name(first_name, last_name, is_club_member_url):
    response = requests.get(
        is_club_member_url.format(last_name=last_name, first_name=first_name),
        verify=False)
    try:
        response.raise_for_status()
        is_club_member = response.json()['is_current_member']
    except (requests.HTTPError, KeyError):
        is_club_member = None
    return is_club_member


@task(ignore_result=True)
def update_google_spreadsheet(riders, doc_key, username, password,
                              is_club_member_url):
    client = google_drive_login(SpreadsheetsService, username, password)
    spreadsheet_list = client.GetListFeed(doc_key)
    spreadsheet_rows = len(spreadsheet_list.entry)
    # Update the rows already in the spreadsheet
    for row, rider in enumerate(riders[:spreadsheet_rows]):
        rider_number = row + 1
        new_row_data = _make_spreadsheet_row_dict(
            rider_number, rider, is_club_member_url)
        client.UpdateRow(spreadsheet_list.entry[row], new_row_data)
    # Add remaining rows
    for row, rider in enumerate(riders[spreadsheet_rows:]):
        rider_number = spreadsheet_rows + row + 1
        row_data = _make_spreadsheet_row_dict(
            rider_number, rider, is_club_member_url)
        client.InsertRow(row_data, doc_key)


def _make_spreadsheet_row_dict(rider_number, rider, is_club_member_url):
    if not rider.member_status:
        rider.member_status = _get_member_status_by_name(
            rider.first_name, rider.last_name, is_club_member_url)
    if rider.member_status is None:
        current_member = 'Unknown'
    else:
        current_member = 'Yes' if rider.member_status else 'No'
    row_data = {
        'ridernumber': str(rider_number),
        'lastname': rider.last_name,
        'firstname': rider.first_name,
        'clubmember': current_member,
        'biketype': rider.bike_type,
    }
    return row_data
