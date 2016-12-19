"""RandoPony brevet admin views.
"""
from deform import Button
from pyramid_deform import FormView
from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
# from randopony.views.admin import google_drive
from randopony.views.admin import core as admin_core
from randopony.models import (
    Brevet,
    BrevetSchema,
)
from randopony.models.meta import DBSession
from randopony import __pkg_metadata__ as version


@view_config(
    route_name='admin.brevets.view',
    renderer='admin/brevet.mako',
    permission='authenticated',
)
def brevet_details(request):
    code, date = request.matchdict['item'].split()
    brevet = admin_core.get_brevet(code, date)
    return {
        'version': version.number + version.release,
        'brevet': brevet,
    }


@view_config(
    route_name='admin.brevets.create',
    renderer='admin/brevet_edit.mako',
    permission='authenticated',
)
class BrevetCreate(FormView):
    schema = BrevetSchema()
    for field in 'id registration_end start_map_url'.split():
        schema.__delitem__(field)
    buttons = (
        Button(name='add', css_class='btn btn-primary'),
        Button(name='cancel', css_class='btn', type='reset'),
    )

    def list_url(self):
        return self.request.route_url('admin.list', list='brevets')

    def show(self, form):
        tmpl_vars = super(BrevetCreate, self).show(form)
        tmpl_vars.update({
            'version': version.number + version.release,
            'cancel_url': self.list_url()
        })
        return tmpl_vars

    def add_success(self, appstruct):
        brevet = Brevet(
            region=appstruct['region'],
            distance=appstruct['distance'],
            date_time=appstruct['date_time'],
            route_name=appstruct['route_name'],
            start_locn=appstruct['start_locn'],
            organizer_email=appstruct['organizer_email'],
        )
        DBSession.add(brevet)
        return HTTPFound(
            self.request.route_url('admin.brevets.view', item=brevet))

    def failure(self, e):
        tmpl_vars = super(BrevetCreate, self).failure(e)
        tmpl_vars.update({
            'version': version.number + version.release,
            'cancel_url': self.list_url()
        })
        return tmpl_vars


@view_config(
    route_name='admin.brevets.edit',
    renderer='admin/brevet_edit.mako',
    permission='authenticated',
)
class BrevetEdit(FormView):
    schema = BrevetSchema()
    buttons = (
        Button(name='save', css_class='btn btn-primary'),
        Button(name='cancel', css_class='btn', type='reset'),
    )

    def view_url(self):
        return self.request.route_url(
            'admin.brevets.view', item=self.request.matchdict['item'])

    def appstruct(self):
        code, date = self.request.matchdict['item'].split()
        brevet = admin_core.get_brevet(code, date)
        return {
            'id': brevet.id,
            'region': brevet.region,
            'distance': brevet.distance,
            'date_time': brevet.date_time,
            'route_name': brevet.route_name,
            'start_locn': brevet.start_locn,
            'start_map_url': brevet.start_map_url,
            'organizer_email': brevet.organizer_email,
            'registration_end': brevet.registration_end,
        }

    def show(self, form):
        tmpl_vars = super(BrevetEdit, self).show(form)
        tmpl_vars.update({
            'version': version.number + version.release,
            'cancel_url': self.view_url()
        })
        return tmpl_vars

    def save_success(self, appstruct):
        brevet = (
            DBSession.query(Brevet)
            .filter_by(id=appstruct['id'])
            .one()
        )
        brevet.region = appstruct['region']
        brevet.distance = appstruct['distance']
        brevet.date_time = appstruct['date_time']
        brevet.route_name = appstruct['route_name']
        brevet.start_locn = appstruct['start_locn']
        brevet.start_map_url = appstruct['start_map_url']
        brevet.organizer_email = appstruct['organizer_email']
        brevet.registration_end = appstruct['registration_end']
        return HTTPFound(
            self.request.route_url('admin.brevets.view', item=brevet))

    def failure(self, e):
        tmpl_vars = super(BrevetEdit, self).failure(e)
        tmpl_vars.update({
            'version': version.number + version.release,
            'cancel_url': self.view_url()
        })
        return tmpl_vars


@view_config(
    route_name='admin.brevets.create_rider_list',
    permission='authenticated',
)
def create_rider_list(request):
    code, date = request.matchdict['item'].split()
    brevet = admin_core.get_brevet(code, date)
    # flash = _create_rider_list(request, brevet)
    # admin_core.finalize_flash_msg(request, flash)
    redirect_url = request.route_url(
        'admin.brevets.view', item=request.matchdict['item'])
    return HTTPFound(redirect_url)


# def _create_rider_list(request, brevet):
#     """Actual creation of rider list spreadsheet on Google Drive.
#
#     For use by :func:`create_rider_list` and :func:`setup_123` views.
#     """
#     username = request.registry.settings['google_drive.username']
#     password = request.registry.settings['google_drive.password']
#     flash = google_drive.create_rider_list(
#         brevet, 'Brevet Rider List Template', username, password)
#     if flash[0] == 'success':
#         flash += google_drive.update_rider_list_info_question(
#             brevet, username, password)
#     return flash


@view_config(
    route_name='admin.brevets.email_to_organizer',
    permission='authenticated',
)
def email_to_organizer(request):
    code, date = request.matchdict['item'].split()
    brevet = admin_core.get_brevet(code, date)
    flash = _email_to_organizer(request, brevet, date)
    admin_core.finalize_flash_msg(request, flash)
    redirect_url = request.route_url(
        'admin.brevets.view', item=request.matchdict['item'])
    return HTTPFound(redirect_url)


def _email_to_organizer(request, brevet, date):
    """Actual sending of email to brevet organizer(s) to notify them of
    event URLs, etc.

    For use by :func:`email_to_organizer` and :func:`setup_123` views.
    """
    event_page_url = request.route_url(
        'brevet', region=brevet.region, distance=brevet.distance, date=date)
    rider_emails_url = request.route_url(
        'brevet.rider_emails', region=brevet.region, distance=brevet.distance,
        date=date, uuid=brevet.uuid)
    flash = admin_core.email_to_organizer(
        request, brevet, event_page_url, rider_emails_url)
    return flash


@view_config(
    route_name='admin.brevets.email_to_webmaster',
    permission='authenticated',
)
def email_to_webmaster(request):
    code, date = request.matchdict['item'].split()
    brevet = admin_core.get_brevet(code, date)
    flash = _email_to_webmaster(request, brevet, date)
    admin_core.finalize_flash_msg(request, flash)
    redirect_url = request.route_url(
        'admin.brevets.view', item=request.matchdict['item'])
    return HTTPFound(redirect_url)


def _email_to_webmaster(request, brevet, date):
    """Actual sending of email to club webmaster to notify them of
    event URLs, etc.

    For use by :func:`email_to_webmaster` and :func:`setup_123` views.
    """
    event_page_url = request.route_url(
        'brevet', region=brevet.region, distance=brevet.distance, date=date)
    flash = admin_core.email_to_webmaster(request, brevet, event_page_url)
    return flash


@view_config(
    route_name='admin.brevets.setup_123',
    permission='authenticated',
)
def setup_123(request):
    code, date = request.matchdict['item'].split()
    brevet = admin_core.get_brevet(code, date)
    # flash = _create_rider_list(request, brevet)
    # if 'error' not in flash:
    #     flash += _email_to_organizer(request, brevet, date)
    #     flash += _email_to_webmaster(request, brevet, date)
    # admin_core.finalize_flash_msg(request, flash)
    redirect_url = request.route_url(
        'admin.brevets.view', item=request.matchdict['item'])
    return HTTPFound(redirect_url)
