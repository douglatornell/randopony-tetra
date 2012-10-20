# -*- coding: utf-8 -*-
"""Tests for RandoPony admin views and functionality.
"""
import unittest
from pyramid import testing
from pyramid.exceptions import Forbidden


class TestAdmin(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_admin_auth_reqd(self):
        """admin_home view requires authentication
        """
        from ..views.admin import admin_home
        request = testing.DummyRequest()
        with self.assertRaises(Forbidden):
            admin_home(request)
