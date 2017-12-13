#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods

from hamcrest import none
from hamcrest import is_not
from hamcrest import assert_that

from nti.testing.matchers import validly_provides
from nti.testing.matchers import verifiably_provides

import unittest

from nti.scorm_cloud.client.config import Configuration

from nti.scorm_cloud.client.scorm import ScormCloudService

from nti.scorm_cloud.interfaces import IDebugService
from nti.scorm_cloud.interfaces import ICourseService
from nti.scorm_cloud.interfaces import IUploadService
from nti.scorm_cloud.interfaces import IReportingService
from nti.scorm_cloud.interfaces import IInvitationService
from nti.scorm_cloud.interfaces import IScormCloudService
from nti.scorm_cloud.interfaces import IRegistrationService

from nti.scorm_cloud.tests import SharedConfiguringTestLayer


class TestScorm(unittest.TestCase):

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

        ds = service.get_debug_service()
        assert_that(ds, validly_provides(IDebugService))
        assert_that(ds, verifiably_provides(IDebugService))

        us = service.get_upload_service()
        assert_that(us, validly_provides(IUploadService))
        assert_that(us, verifiably_provides(IUploadService))

        rs = service.get_registration_service()
        assert_that(rs, validly_provides(IRegistrationService))
        assert_that(rs, verifiably_provides(IRegistrationService))

        rs = service.get_reporting_service()
        assert_that(rs, validly_provides(IReportingService))
        assert_that(rs, verifiably_provides(IReportingService))

        isv = service.get_invitation_service()
        assert_that(isv, validly_provides(IInvitationService))
        assert_that(isv, verifiably_provides(IInvitationService))
