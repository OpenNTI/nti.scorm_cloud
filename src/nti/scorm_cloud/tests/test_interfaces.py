#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods

from hamcrest import assert_that
from hamcrest import is_

from nti.testing.matchers import verifiably_provides

import unittest

from rustici_software_cloud_v2.models import LaunchLinkSchema

from zope.dottedname import resolve as dottedname

from . import SharedConfiguringTestLayer

from ..interfaces import ILaunchLink

class TestInterfaces(unittest.TestCase):

    def test_import_interfaces(self):
        dottedname.resolve('nti.scorm_cloud.interfaces')

class TestScormCloudClientModels(unittest.TestCase):

    layer = SharedConfiguringTestLayer
    
    def test_launch_link_conformance(selt):
        lls = LaunchLinkSchema('https://scorm.cloud.com/launch')

        assert_that(lls, verifiably_provides(ILaunchLink))
