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
from hamcrest import instance_of
from hamcrest import starts_with

from nti.testing.matchers import validly_provides
from nti.testing.matchers import verifiably_provides

import six
import unittest

from nti.scorm_cloud.client import make_utf8
from nti.scorm_cloud.client import TagSettings
from nti.scorm_cloud.client import Configuration
from nti.scorm_cloud.client import WidgetSettings
from nti.scorm_cloud.client import DateRangeSettings
from nti.scorm_cloud.client import ScormCloudService
from nti.scorm_cloud.client import ScormCloudUtilities

from nti.scorm_cloud.interfaces import ITagSettings
from nti.scorm_cloud.interfaces import IDebugService
from nti.scorm_cloud.interfaces import ICourseService
from nti.scorm_cloud.interfaces import IUploadService
from nti.scorm_cloud.interfaces import IWidgetSettings
from nti.scorm_cloud.interfaces import IReportingService
from nti.scorm_cloud.interfaces import IDateRangeSettings
from nti.scorm_cloud.interfaces import IInvitationService
from nti.scorm_cloud.interfaces import IScormCloudService
from nti.scorm_cloud.interfaces import IRegistrationService

from nti.scorm_cloud.tests import SharedConfiguringTestLayer


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


class TestSettings(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    def test_daterange(self):
        d = DateRangeSettings('selection', '2016', '2017', 'strict')
        assert_that(d, validly_provides(IDateRangeSettings))
        assert_that(d, verifiably_provides(IDateRangeSettings))
        assert_that(d.get_url_encoding(),
                    is_('&dateRangeType=c&dateRangeStart=2016&dateRangeEnd=2017&dateCriteria=strict'))

        d = DateRangeSettings('z', '2016', '2017', 'strict')
        assert_that(d.get_url_encoding(),
                    is_('&dateRangeType=z&dateCriteria=strict'))

    def test_tags(self):
        s = TagSettings()
        assert_that(s, validly_provides(ITagSettings))
        assert_that(s, verifiably_provides(ITagSettings))

        s.add('course', 'Bankai')
        s.add('learner', 'Ichigo')
        s.add('learner', 'Rukia')
        s.add('registration', 'SoulSociety')
        assert_that(s.get_tag_str('course'),
                    is_('Bankai|_all'))
        assert_that(s.get_view_tag_str('learner'),
                    is_('Rukia,Ichigo'))
        assert_that(s.get_url_encoding(),
                    is_('&courseTags=Bankai%7C_all&viewCourseTagGroups=Bankai&learnerTags=Rukia%2CIchigo%7C_all&viewLearnerTagGroups=Rukia%2CIchigo&registrationTags=SoulSociety%7C_all&viewRegistrationTagGroups=SoulSociety'))

    def test_widget(self):
        s = WidgetSettings()
        assert_that(s, validly_provides(IWidgetSettings))
        assert_that(s, verifiably_provides(IWidgetSettings))

        s.iframe = True
        s.courseId = 'Bankai'
        s.learnerId = 'Ichigo'

        assert_that(s.get_url_encoding(),
                    is_('&courseId=Bankai&learnerId=Ichigo&showTitle=true&standalone=true&iframe=true&expand=true&scriptBased=true&divname=&vertical=false&embedded=true'))

        s.dateRangeSettings = DateRangeSettings('z', '2016', '2017', 'strict')
        s.tagSettings = TagSettings().add('course', 'Bankai')

        assert_that(s.get_url_encoding(),
                    starts_with('&courseId=Bankai&learnerId=Ichigo&showTitle=true&standalone=true&iframe=true&expand=true&scriptBased=true&divname=&vertical=false&embedded=true'))
