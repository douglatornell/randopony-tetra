"""Tests for RandoPony public site core views and functionality.
"""
from unittest.mock import patch

from pyramid.threadlocal import get_current_request
import pytest


@pytest.fixture(scope='module')
def core_module():
    from randopony.views.site import core
    return core


@pytest.fixture(scope='function')
def views(core_module, pyramid_config):
    from randopony.views.site.core import SiteViews
    with patch.object(core_module, 'get_membership_link'):
        return SiteViews(get_current_request())


@pytest.mark.usefixtures('core_module', 'link_model', 'db_session')
class TestGetMembershipLink(object):
    """Unit test for get_membership_link() function.
    """
    def test_get_membership_link(self, core_module, link_model, db_session):
        """returns club membership sign-up site URL from database
        """
        link = link_model(
            key='membership_link', url='https://membership_link/')
        db_session.add(link)
        membership_link = core_module.get_membership_link()
        assert membership_link == 'https://membership_link/'


@pytest.mark.usefixtures('core_module', 'link_model', 'db_session')
class TestGetEntryFormURL(object):
    """Unit test for get_entry_form_url() function.
    """
    def test_get_entry_form_url(self, core_module, link_model, db_session):
        """returns event entry form URL from database
        """
        link = link_model(
            key='entry_form', url='http://entry_form.pdf/')
        db_session.add(link)
        entry_form_url = core_module.get_entry_form_url()
        assert entry_form_url == 'http://entry_form.pdf/'


@pytest.mark.usefixtures('core_module', 'link_model', 'db_session')
class TestGetResultsLink(object):
    """Unit test for get_entry_form_url() function.
    """
    def test_get_entry_form_url(self, core_module, link_model, db_session):
        """returns club event results page URL from database
        """
        link = link_model(
            key='results_link',
            url='https://database.randonneurs.bc.ca/browse/randonnees')
        db_session.add(link)
        results_link = core_module.get_results_link()
        expected = 'https://database.randonneurs.bc.ca/browse/randonnees'
        assert results_link == expected


@pytest.mark.usefixtures(
    'views', 'email_address_model', 'db_session', 'pyramid_config',
)
class TestSiteViews(object):
    """Unit tests for public site views.
    """
    def test_init(self, views):
        """SiteViews constructor sets request & tmpl_vars attrs
        """
        assert views.request == get_current_request()
        assert 'brevets' in views.tmpl_vars
        assert 'populaires' in views.tmpl_vars
        assert 'membership_link' in views.tmpl_vars

    def test_home(self, views):
        """home view has home tab set as active tab
        """
        tmpl_vars = views.home()
        assert tmpl_vars['active_tab'] == 'home'

    def test_organizer_info(self, views, email_address_model, db_session):
        """organizer_info view has expected tmpl_vars
        """
        email = email_address_model(
            key='admin_email', email='tom@example.com')
        db_session.add(email)
        tmpl_vars = views.organizer_info()
        assert tmpl_vars['active_tab'] == 'organizer-info'
        assert tmpl_vars['admin_email'] == 'tom@example.com'

    def test_about(self, views):
        """about view has about tab set as active tab
        """
        tmpl_vars = views.about()
        assert tmpl_vars['active_tab'] == 'about'

    def test_notfound(self, views):
        """notfound view has no active tab and 404 status
        """
        tmpl_vars = views.notfound()
        assert tmpl_vars['active_tab'] is None
        assert get_current_request().response.status == '404 Not Found'
