# -*- coding: utf-8 -*-
"""RandoPony public site brevet views.
"""
from datetime import (
    datetime,
    timedelta,
    )
import logging
import pytz
from pyramid.httpexceptions import HTTPNotFound
from pyramid.renderers import render
from pyramid.response import Response
from pyramid.view import view_config
from .core import SiteViews
from ...models import (
    Brevet,
    EmailAddress,
    Link,
    )
from ...models.meta import DBSession


log = logging.getLogger(__name__)


def get_brevet(region, distance, date):
    brevet = (DBSession.query(Brevet)
        .filter_by(region=region, distance=distance)
        .filter(Brevet.date_time >= date)
        .filter(Brevet.date_time < date + timedelta(days=1))
        .first()
        )
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
            .one()
            )
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
            .filter_by(region=region)
            )
        images = {
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
            .one()[0]
            )
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
            .one()[0]
            )
        results_link = results_link.replace(
            '{year}', str(self.brevet.date_time.year)[-2:])
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
