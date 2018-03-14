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
from hamcrest import has_properties

import unittest

import fudge

from io import BytesIO

from nti.scorm_cloud.client.course import ImportResult

from nti.scorm_cloud.client.scorm import ScormCloudService

from nti.scorm_cloud.tests import fake_response
from nti.scorm_cloud.tests import SharedConfiguringTestLayer


class TestCourseService(unittest.TestCase):
    
    layer = SharedConfiguringTestLayer
    
    @fudge.patch('nti.scorm_cloud.client.request.ServiceRequest.session')
    def test_import_uploaded_course(self, mock_ss):
        service = ScormCloudService.withargs("appid", "secret",
                                             "http://cloud.scorm.com/api")
        course = service.get_course_service()
        
        course_id = 'courseid'
        path = BytesIO(b'data')
        reply = """
        <importresult successful="true">
            <title>Photoshop Example -- Competency</title>
            <message>Import Successful</message>
            <parserwarnings>
                <warning>[warning text]</warning>
            </parserwarnings>
        </importresult>
        """
        reply = '<rsp stat="ok">%s</rsp>' % reply
        data = fake_response(content=reply)
        session = fudge.Fake().expects('post').returns(data)
        mock_ss.is_callable().returns(session)
        
        result_list = course.import_uploaded_course(course_id, path)
        assert_that(result_list[0],
                    has_properties('title', 'Photoshop Example -- Competency',
                                   'message', 'Import Successful',
                                   'parserWarnings', ['[warning text]'],
                                   'wasSuccessful', True))
    
    @fudge.patch('nti.scorm_cloud.client.request.ServiceRequest.session')
    def test_delete_course(self, mock_ss):
        service = ScormCloudService.withargs("appid", "secret",
                                             "http://cloud.scorm.com/api")
        course = service.get_course_service()
        
        reply = '<success />'
        reply = '<rsp stat="ok">%s</rsp>' % reply
        data = fake_response(content=reply)
        session = fudge.Fake().expects('get').returns(data)
        mock_ss.is_callable().returns(session)
        
        result = course.delete_course('courseid')
        success_nodes = result.getElementsByTagName('success')
        assert_that(success_nodes, is_(not_none()))