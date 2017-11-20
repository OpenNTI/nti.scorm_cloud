#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import none
from hamcrest import is_not
from hamcrest import assert_that
from hamcrest import has_properties
from hamcrest import contains_string

import unittest
from io import BytesIO

from xml.dom import minidom

from nti.scorm_cloud.client import mixins


class TestWithRepr(unittest.TestCase):

    def test_default(self):

        @mixins.WithRepr
        class Foo(object):
            pass

        r = repr(Foo())
        assert_that(r,
                    contains_string('<nti.scorm_cloud.tests.test_mixins.Foo'))
        assert_that(r, contains_string('{}>'))

    def test_with_default_callable(self):
        @mixins.WithRepr(lambda unused_s: "<HI>")
        class Foo(object):
            pass

        r = repr(Foo())
        assert_that(r, is_("<HI>"))


class TestMixins(unittest.TestCase):

    def test_registration(self):
        dom = minidom.parseString('<registration format="f" regid="123" instanceid="1" />')
        r = mixins.RegistrationMixin.fromMinidom(dom.firstChild)
        assert_that(r,
                    has_properties('format', 'f',
                                   'regid', '123',
                                   'instanceid', '1',
                                   '_node', is_not(none())))
        
    def test_get_source(self):
        g = mixins.get_source(BytesIO(b'data'))
        assert_that(g, is_(BytesIO))
        
        g = mixins.get_source(b'data')
        assert_that(g, is_(BytesIO))

        g = mixins.get_source(__file__)
        assert_that(g, is_(BytesIO))
