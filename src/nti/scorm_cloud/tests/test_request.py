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
from hamcrest import instance_of

import six
import unittest

from requests import Session

from nti.scorm_cloud.client.request import make_utf8
from nti.scorm_cloud.client.request import ServiceRequest
from nti.scorm_cloud.client.request import ScormCloudError
from nti.scorm_cloud.client.request import ScormCloudUtilities

from nti.scorm_cloud.tests import SharedConfiguringTestLayer


class TestRequest(unittest.TestCase):

    layer = SharedConfiguringTestLayer

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
                    has_entries('Bleach', 'Ichigo',
                                'Shikai', is_(instance_of(six.string_types)),
                                'Bankai', is_(instance_of(six.string_types))))
        
    def test_coverage(self):
        service = ServiceRequest(None)
        
        # get xml with error
        raw = '<rsp stat="failed"><error code="500" msg="server error"/></rsp>'
        with self.assertRaises(ScormCloudError):
            service.get_xml(raw)
        
        # get a requests session
        assert_that(service.session(), is_(Session))
