#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

import unittest

from hamcrest import is_
from hamcrest import assert_that

from nti.scorm_cloud.compat import native_


class TestCompat(unittest.TestCase):

    def test_native(self):
        class Foo(object):
            def __str__(self):
                return 'foo'

        assert_that(native_(Foo()), is_('foo'))