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
from hamcrest import has_entries

from nti.testing.matchers import validly_provides
from nti.testing.matchers import verifiably_provides

import six
import unittest

from nti.scorm_cloud.tests import SharedConfiguringTestLayer

from nti.scorm_cloud.client import make_utf8
from nti.scorm_cloud.client import Configuration
from nti.scorm_cloud.client import ScormCloudService
from nti.scorm_cloud.client import ScormCloudUtilities

from nti.scorm_cloud.interfaces import ICourseService
from nti.scorm_cloud.interfaces import IScormCloudService


class TestClient(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    def test_verify(self):
        config = Configuration("appid", "secret", "http://example.org")
        assert_that(repr(config), is_not(none()))

        service = ScormCloudService.withconfig(config)
        assert_that(service, validly_provides(IScormCloudService))
        assert_that(service, verifiably_provides(IScormCloudService))

        service = ScormCloudService.withargs("appid", "secret", 
                                             "http://example.org")
        assert_that(service, validly_provides(IScormCloudService))

        cs = service.get_course_service()
        assert_that(cs, validly_provides(ICourseService))
        assert_that(cs, verifiably_provides(ICourseService))

    def test_scorm_cloud_utilities(self):
        s = ScormCloudUtilities.get_canonical_origin_string("NextThought&", "Dataserver*",
                                                            "2.0^")
        assert_that(s, is_('nextthought.dataserver.2.0'))

        url = 'http://scorm.nextthought.com'
        url = ScormCloudUtilities.clean_cloud_host_url(url)
        assert_that(url, 'http://scorm.nextthought.com/api')

        assert_that(ScormCloudUtilities.clean_cloud_host_url('http://scorm.nti.com/api'),
                    is_('http://scorm.nti.com/api'))

    def test_make_utf8(self):
        data = {
            'Bleach': u'Ichigo',
            'Shikai': u'黒衣の男',
            'Bankai': object(),
        }
        assert_that(make_utf8(data),
                    has_entries('Bleach', b'Ichigo',
                                'Shikai', is_(six.binary_type)))
