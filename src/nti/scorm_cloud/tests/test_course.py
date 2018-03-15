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
from hamcrest import has_entries
from hamcrest import starts_with
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
    
    @fudge.patch('nti.scorm_cloud.client.request.ServiceRequest.session')
    def test_get_assets(self, mock_ss):
        service = ScormCloudService.withargs("appid", "secret",
                                             "http://cloud.scorm.com/api")
        course = service.get_course_service()
        
        reply = u'bytes\uFFFD'
        data = fake_response(content=reply)
        session = fudge.Fake().expects('get').returns(data)
        mock_ss.is_callable().returns(session)
        
        result = course.get_assets('courseid')
        assert_that(result, is_(reply))
    
    @fudge.patch('nti.scorm_cloud.client.request.ServiceRequest.session')
    def test_get_course_list(self, mock_ss):
        service = ScormCloudService.withargs("appid", "secret",
                                             "http://cloud.scorm.com/api")
        course = service.get_course_service()
        
        reply = """
        <courselist>
            <course id="test321" title="Photoshop Example -- Competency" versions="-1" registrations="2" >
                <tags>
                    <tag>test1</tag>
                    <tag>test2</tag>
                </tags>
            </course>
            <course id="course321" title="Another Test Course" versions="-1" registrations="5" >
                <tags></tags>
            </course>
        </courselist>
        """
        reply = '<rsp stat="ok">%s</rsp>' % reply
        data = fake_response(content=reply)
        session = fudge.Fake().expects('get').returns(data)
        mock_ss.is_callable().returns(session)
        
        course_list = course.get_course_list()
        assert_that(course_list, has_length(2))
        assert_that(course_list[0],
                    has_properties('title', 'Photoshop Example -- Competency',
                                   'courseId', 'test321',
                                   'numberOfVersions', '-1',
                                   'numberOfRegistrations', '2'))
        assert_that(course_list[1],
                    has_properties('title', 'Another Test Course',
                                   'courseId', 'course321',
                                   'numberOfVersions', '-1',
                                   'numberOfRegistrations', '5'))
        
    def test_get_preview_url(self):
        service = ScormCloudService.withargs("appid", "secret",
                                             "http://cloud.scorm.com/api")
        course = service.get_course_service()
        url = course.get_preview_url('courseid', 'about:none')
        assert_that(url, starts_with("http://cloud.scorm.com/api?"))
        
    @fudge.patch('nti.scorm_cloud.client.request.ServiceRequest.session')
    def test_get_metadata(self, mock_ss):
        service = ScormCloudService.withargs("appid", "secret",
                                             "http://cloud.scorm.com/api")
        course = service.get_course_service()
        
        reply = """
        <package>
            <metadata>
                <title>Package Title</title>
                <description>Package Description</description>
                <duration>Package Duration</duration>
                <typicaltime>0</typicaltime>
                <keywords>
                    <keyword>Training</keyword>
                </keywords>
            </metadata>
            <object id="B0"
                    title="Root Title"
                    description="Root Description"
                    duration="0"
                    typicaltime="0" />
        </package>
        """
        reply = '<rsp stat="ok">%s</rsp>' % reply
        data = fake_response(content=reply)
        session = fudge.Fake().expects('get').returns(data)
        mock_ss.is_callable().returns(session)
        
        metadata = course.get_metadata('courseid')
        assert_that(metadata,
                    has_properties('title', 'Root Title'))
        
    def test_get_property_editor_url(self):
        service = ScormCloudService.withargs("appid", "secret",
                                             "http://cloud.scorm.com/api")
        course = service.get_course_service()
        url = course.get_property_editor_url('courseid')
        assert_that(url, starts_with("http://cloud.scorm.com/api?"))
    
    @fudge.patch('nti.scorm_cloud.client.request.ServiceRequest.session')
    def test_get_attributes(self, mock_ss):
        service = ScormCloudService.withargs("appid", "secret",
                                             "http://cloud.scorm.com/api")
        course = service.get_course_service()
        
        reply = """
        <attributes>
            <attribute name="alwaysFlowToFirstSco" value="false"/>
            <attribute name="commCommitFrequency" value="10000"/>
            <attribute name="commMaxFailedSubmissions" value="2"/>
            <attribute name="validateInteractionResponses" value="true"/>
            <attribute name="wrapScoWindowWithApi" value="false"/>
         </attributes>
        """
        reply = '<rsp stat="ok">%s</rsp>' % reply
        data = fake_response(content=reply)
        session = fudge.Fake().expects('get').returns(data)
        mock_ss.is_callable().returns(session)
        
        attributes = course.get_attributes('courseid')
        assert_that(attributes,
                    has_entries('alwaysFlowToFirstSco', 'false',
                                'commCommitFrequency', '10000',
                                'commMaxFailedSubmissions', '2',
                                'validateInteractionResponses', 'true',
                                'wrapScoWindowWithApi', 'false'))
        