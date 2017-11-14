#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import not_none
from hamcrest import assert_that

import unittest

import fudge

from nti.scorm_cloud.client.scorm import ScormCloudService

from nti.scorm_cloud.tests import SharedConfiguringTestLayer


class TestRegistrationService(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    @fudge.patch('nti.scorm_cloud.client.request.ServiceRequest.session')
    def test_create_registration(self, mock_ss):
        service = ScormCloudService.withargs("appid", "secret",
                                             "http://cloud.scorm.com/api")
        reg = service.get_registration_service()

        reply = '<rsp stat="ok"><success/></rsp>'
        data = fudge.Fake().has_attr(text=reply)
        session = fudge.Fake().expects('get').returns(data)
        mock_ss.is_callable().returns(session)

        regid = reg.createRegistration("bankai", None,
                                       'Ichigo', 'Kurosaki',
                                       'ichigo@bleach.org',
                                       'ichigo@bleach.org',
                                       "http://bleach.org",
                                       "httpbasic", "ichigo", "zangetsu",
                                       "course")
        assert_that(regid, is_(not_none()))
