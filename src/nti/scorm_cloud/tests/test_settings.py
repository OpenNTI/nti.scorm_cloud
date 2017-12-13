#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods

from hamcrest import is_
from hamcrest import assert_that
from hamcrest import has_entries

from nti.testing.matchers import validly_provides
from nti.testing.matchers import verifiably_provides

import unittest
from six.moves import urllib_parse

from nti.scorm_cloud.client import TagSettings
from nti.scorm_cloud.client import WidgetSettings
from nti.scorm_cloud.client import DateRangeSettings

from nti.scorm_cloud.interfaces import ITagSettings
from nti.scorm_cloud.interfaces import IWidgetSettings
from nti.scorm_cloud.interfaces import IDateRangeSettings

from nti.scorm_cloud.tests import SharedConfiguringTestLayer


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
                    is_('Ichigo,Rukia'))
        assert_that(urllib_parse.parse_qs(s.get_url_encoding()),
                    has_entries('viewLearnerTagGroups', ['Ichigo,Rukia'],
                                'registrationTags', ['SoulSociety|_all'],
                                'viewCourseTagGroups', ['Bankai'],
                                'courseTags', ['Bankai|_all'],
                                'learnerTags', ['Ichigo,Rukia|_all'],
                                'viewRegistrationTagGroups', ['SoulSociety']))

    def test_widget(self):
        s = WidgetSettings()
        assert_that(s, validly_provides(IWidgetSettings))
        assert_that(s, verifiably_provides(IWidgetSettings))

        s.iframe = True
        s.courseId = 'Bankai'
        s.learnerId = 'Ichigo'

        assert_that(urllib_parse.parse_qs(s.get_url_encoding()),
                    has_entries('scriptBased', ['true'],
                                'embedded', ['true'],
                                'vertical', ['false'],
                                'standalone', ['true'],
                                'courseId', ['Bankai'],
                                'showTitle', ['true'],
                                'learnerId', ['Ichigo'],
                                'iframe', ['true'],
                                'expand', ['true']))

        s.dateRangeSettings = DateRangeSettings('z', '2016', '2017', 'strict')
        s.tagSettings = TagSettings()
        s.tagSettings.add('course', 'Bankai')

        assert_that(urllib_parse.parse_qs(s.get_url_encoding()),
                    has_entries('scriptBased', ['true'],
                                'embedded', ['true'],
                                'vertical', ['false'],
                                'standalone', ['true'],
                                'courseId', ['Bankai'],
                                'showTitle', ['true'],
                                'learnerId', ['Ichigo'],
                                'iframe', ['true'],
                                'expand', ['true'],
                                'dateRangeType', ['z'],
                                'courseTags', ['Bankai|_all'],
                                'dateCriteria', ['strict'],
                                'viewCourseTagGroups', ['Bankai']))
