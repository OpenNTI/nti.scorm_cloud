#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods

from hamcrest import is_
from hamcrest import not_none
from hamcrest import has_length
from hamcrest import assert_that
from hamcrest import contains_inanyorder

import unittest

import fudge

from nti.scorm_cloud.client.scorm import ScormCloudService

from nti.scorm_cloud.tests import fake_response
from nti.scorm_cloud.tests import SharedConfiguringTestLayer


class TestTagService(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    @fudge.patch('nti.scorm_cloud.client.request.ServiceRequest.session')
    def test_get_tags(self, mock_ss):
        service = ScormCloudService.withargs("appid", "secret",
                                             "http://cloud.scorm.com/api")
        tag_service = service.get_tag_service()

        course_id = 'courseid'
        reply = """
        <tags>
            <tag>tag1</tag>
            <tag>tag two</tag>
            <tag>tag3</tag>
        </tags>
        """
        reply = '<rsp stat="ok">%s</rsp>' % reply
        data = fake_response(content=reply)
        session = fudge.Fake().expects('get').returns(data)
        mock_ss.is_callable().returns(session)

        result_list = tag_service.get_scorm_tags(course_id)
        assert_that(result_list, has_length(3))
        assert_that(result_list,
                    contains_inanyorder('tag1', 'tag two', 'tag3'))

    @fudge.patch('nti.scorm_cloud.client.request.ServiceRequest.session')
    def test_set_scorm_tags(self, mock_ss):
        service = ScormCloudService.withargs("appid", "secret",
                                             "http://cloud.scorm.com/api")
        tag_service = service.get_tag_service()
        course_id = 'courseid'

        reply = '<success />'
        reply = '<rsp stat="ok">%s</rsp>' % reply
        data = fake_response(content=reply)
        session = fudge.Fake().expects('get').returns(data)
        mock_ss.is_callable().returns(session)

        result = tag_service.set_scorm_tags(course_id, ['tag1', 'tag two', 'tag3'])
        success_nodes = result.getElementsByTagName('success')
        assert_that(success_nodes, is_(not_none()))

    @fudge.patch('nti.scorm_cloud.client.request.ServiceRequest.session')
    def test_add_scorm_tag(self, mock_ss):
        service = ScormCloudService.withargs("appid", "secret",
                                             "http://cloud.scorm.com/api")
        tag_service = service.get_tag_service()
        course_id = 'courseid'

        reply = '<success />'
        reply = '<rsp stat="ok">%s</rsp>' % reply
        data = fake_response(content=reply)
        session = fudge.Fake().expects('get').returns(data)
        mock_ss.is_callable().returns(session)

        result = tag_service.add_scorm_tag(course_id, 'tag4')
        success_nodes = result.getElementsByTagName('success')
        assert_that(success_nodes, is_(not_none()))

    @fudge.patch('nti.scorm_cloud.client.request.ServiceRequest.session')
    def test_remove_scorm_tag(self, mock_ss):
        service = ScormCloudService.withargs("appid", "secret",
                                             "http://cloud.scorm.com/api")
        tag_service = service.get_tag_service()
        course_id = 'courseid'

        reply = '<success />'
        reply = '<rsp stat="ok">%s</rsp>' % reply
        data = fake_response(content=reply)
        session = fudge.Fake().expects('get').returns(data)
        mock_ss.is_callable().returns(session)

        result = tag_service.remove_scorm_tag(course_id, 'tag4')
        success_nodes = result.getElementsByTagName('success')
        assert_that(success_nodes, is_(not_none()))

