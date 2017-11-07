#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import assert_that
from hamcrest import has_entries

from nti.testing.matchers import validly_provides
from nti.testing.matchers import verifiably_provides

import six
import unittest

from nti.scorm_cloud.tests import SharedConfiguringTestLayer

from nti.scorm_cloud.client import make_utf8
from nti.scorm_cloud.client import Configuration
from nti.scorm_cloud.client import ScormCloudService

from nti.scorm_cloud.interfaces import IScormCloudService


class TestClient(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    def test_verify(self):
        config = Configuration("appid", "secret", "http://example.org")
        service = ScormCloudService.withconfig(config)
        assert_that(service, validly_provides(IScormCloudService))
        assert_that(service, verifiably_provides(IScormCloudService))
        
    def test_make_utf8(self):
        data = {
            'Bleach': u'Ichigo',
            'Shikai': u'黒衣の男'
        }
        assert_that(make_utf8(data),
                    has_entries('Bleach', b'Ichigo',
                                'Shikai', is_(six.binary_type)))
