#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

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
