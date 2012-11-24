# -*- coding: utf-8 -*-
"""Tests for RandoPony base site views and functionality.
"""
import unittest
import transaction

from pyramid import testing

from ..models import DBSession
