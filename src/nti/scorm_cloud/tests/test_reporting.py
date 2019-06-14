#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods

from xml.dom import minidom

from hamcrest import is_
from hamcrest import not_none
from hamcrest import has_length
from hamcrest import assert_that
from hamcrest import contains_inanyorder

from nti.testing.matchers import validly_provides

import unittest

import fudge

from nti.scorm_cloud.client.scorm import ScormCloudService

from nti.scorm_cloud.tests import fake_response
from nti.scorm_cloud.tests import SharedConfiguringTestLayer

from nti.scorm_cloud.interfaces import IAccountInfo
from nti.scorm_cloud.interfaces import IAccountUsageInfo

from nti.scorm_cloud.client.reporting import AccountInfo
from nti.scorm_cloud.client.reporting import AccountUsageInfo

from nti.scorm_cloud.minidom import getText

ACCOUNT_RESPONSE = """<?xml version="1.0" ?><rsp stat="ok">
<account>
    <email>email@example.com</email>
    <firstname>Test</firstname>
    <lastname>Man</lastname>
    <company>Test Company, Inc.</company>
    <accounttype>little</accounttype>
    <reglimit>50</reglimit>
    <strictlimit>false</strictlimit>
    <createdate>2009-10-22T08:55:08-0500</createdate>
    <usage>
      <monthstart>2009-10-22T08:55:08-0500</monthstart>
      <regcount>23</regcount>
      <totalregistrations>89</totalregistrations>
      <totalcourses>8</totalcourses>
    </usage>
</account>
</rsp>
"""


class TestParseAccountInfo(unittest.TestCase):

    def test_parse_account_usage_info(self):
        dom = minidom.parseString(ACCOUNT_RESPONSE)
        usage_dom = dom.getElementsByTagName('usage')[0]

        assert_that(usage_dom, not_none())

        usage = AccountUsageInfo.createFromMinidom(usage_dom)
        assert_that(usage, validly_provides(IAccountUsageInfo))
        assert_that(usage.reg_count, is_(23))
        assert_that(usage.total_registrations, is_(89))
        assert_that(usage.total_courses, is_(8))
        assert_that(usage.month_start.strftime(u'%Y-%m-%dT%H:%M:%S%z'),
                    is_(u'2009-10-22T08:55:08-0500'))

    def test_parse_account_info(self):
        dom = minidom.parseString(ACCOUNT_RESPONSE)
        account_dom = dom.getElementsByTagName('account')[0]

        assert_that(account_dom, not_none())

        info = AccountInfo.createFromMinidom(account_dom)
        assert_that(info, validly_provides(IAccountInfo))
        assert_that(info.usage, validly_provides(IAccountUsageInfo))

        assert_that(info.email, is_(u'email@example.com'))
        assert_that(info.firstname, is_(u'Test'))
        assert_that(info.lastname, is_(u'Man'))
        assert_that(info.account_type, is_(u'little'))
        assert_that(info.reg_limit, is_(50))
        assert_that(info.strict_limit, is_(False))
        assert_that(info.create_date.strftime(u'%Y-%m-%dT%H:%M:%S%z'),
                    is_(u'2009-10-22T08:55:08-0500'))

class TestReporting(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    @fudge.patch('nti.scorm_cloud.client.request.ServiceRequest.session')
    def test_get_tags(self, mock_ss):
        service = ScormCloudService.withargs("appid", "secret",
                                             "http://cloud.scorm.com/api")
        reporting_service = service.get_reporting_service()

        data = fake_response(content=ACCOUNT_RESPONSE)
        session = fudge.Fake().expects('get').returns(data)
        mock_ss.is_callable().returns(session)

        info = reporting_service.get_account_info()
        assert_that(info, validly_provides(IAccountInfo))
        assert_that(info.reg_limit, is_(50))
        
