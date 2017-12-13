#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods

from hamcrest import is_
from hamcrest import none
from hamcrest import assert_that

import unittest

from xml.dom import minidom

from nti.scorm_cloud.minidom import getChildText
from nti.scorm_cloud.minidom import getChildCDATA


class TestMinidom(unittest.TestCase):

    def test_coverage(self):
        dom = minidom.parseString('<slideshow />')
        assert_that(getChildText(dom, 'a'), is_(none()))
        assert_that(getChildCDATA(dom, 'a'), is_(none()))
