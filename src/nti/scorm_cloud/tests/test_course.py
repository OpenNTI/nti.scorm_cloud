#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods

from hamcrest import is_
from hamcrest import none
from hamcrest import not_none
from hamcrest import has_length
from hamcrest import assert_that
from hamcrest import has_entries
from hamcrest import starts_with
from hamcrest import has_properties
from hamcrest import contains_inanyorder

import unittest

import fudge

from io import BytesIO

from nti.scorm_cloud.client.scorm import ScormCloudService

from nti.scorm_cloud.tests import fake_response
from nti.scorm_cloud.tests import SharedConfiguringTestLayer


class TestCourseService(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    @fudge.patch('nti.scorm_cloud.client.request.ServiceRequest.session')
    def test_get_course_detail(self, mock_ss):
        reply = """
        <rsp stat="ok">
        <course id="31796ffa-e7b0-4848-a8dd-45a8e0933482" registrations="0" size="3180" title="ASPIRE Alpha" versions="1">
            <versions><version><versionId><![CDATA[0]]></versionId>
            <updateDate><![CDATA[2021-06-22T18:57:00.000+0000]]></updateDate>
            </version></versions>
            <tags><tag><![CDATA[6819436859104098208]]></tag><tag><![CDATA[alpha.dev]]></tag></tags>
            <learningStandard><![CDATA[cmi5]]></learningStandard>
            <createDate>2021-06-22T18:57:00.000+0000</createDate>
        </course>
        </rsp>
        """

        service = ScormCloudService.withargs("appid", "secret",
                                             "http://cloud.scorm.com/api")
        course = service.get_course_service()

        data = fake_response(content=reply)
        session = fudge.Fake().expects('get').returns(data)
        mock_ss.is_callable().returns(session)

        course_data = course.get_course_detail('31796ffa-e7b0-4848-a8dd-45a8e0933482')
        assert_that(course_data, has_properties('title', 'ASPIRE Alpha',
                                                'tags', ['6819436859104098208', 'alpha.dev'],
                                                'learningStandard', 'cmi5'))

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
    def test_import_uploaded_course_async(self, mock_ss):
        service = ScormCloudService.withargs("appid", "secret",
                                             "http://cloud.scorm.com/api")
        course = service.get_course_service()

        course_id = 'courseid'
        path = BytesIO(b'data')
        reply = """
        <token>
           <id>e2bfa26e-2e96-48e3-86a6-f435fba6dccb</id>
        </token>
        """
        reply = '<rsp stat="ok">%s</rsp>' % reply
        data = fake_response(content=reply)
        session = fudge.Fake().expects('post').returns(data)
        mock_ss.is_callable().returns(session)
        token = course.import_uploaded_course_async(course_id, path)
        assert_that(token, is_('e2bfa26e-2e96-48e3-86a6-f435fba6dccb'))

    @fudge.patch('nti.scorm_cloud.client.request.ServiceRequest.session')
    def test_get_async_import_result(self, mock_ss):
        service = ScormCloudService.withargs("appid", "secret",
                                             "http://cloud.scorm.com/api")
        course = service.get_course_service()

        token = 'e2bfa26e-2e96-48e3-86a6-f435fba6dccb'
        success_reply = """
           <status>finished</status>
           <importresults>
             <importresult successful="true">
             <title>Photoshop Example -- Competency</title>
             <message>Import Successful</message>
             </importresult>
           </importresults>
        """
        success_reply = '<rsp stat="ok">%s</rsp>' % success_reply
        data = fake_response(content=success_reply)
        session = fudge.Fake().expects('get').returns(data)
        mock_ss.is_callable().returns(session)
        import_result = course.get_async_import_result(token)
        assert_that(import_result, has_properties('title', 'Photoshop Example -- Competency',
                                                  'status', 'finished',
                                                  'error_message', none()))

        unsuccessful_reply = """
           <status>finished</status>
           <importresults>
             <importresult successful="false">
             <title>Photoshop Example -- Competency</title>
             <message>zip did not contain courses</message>
             </importresult>
           </importresults>
        """
        unsuccessful_reply = '<rsp stat="ok">%s</rsp>' % unsuccessful_reply
        data = fake_response(content=unsuccessful_reply)
        session = fudge.Fake().expects('get').returns(data)
        mock_ss.is_callable().returns(session)
        import_result = course.get_async_import_result(token)
        assert_that(import_result, has_properties('title', 'Photoshop Example -- Competency',
                                                  'status', 'error',
                                                  'error_message', 'zip did not contain courses'))

        error_reply = """
           <status>error</status>
           <error>Error during import</error>
        """
        error_reply = '<rsp stat="ok">%s</rsp>' % error_reply
        data = fake_response(content=error_reply)
        session = fudge.Fake().expects('get').returns(data)
        mock_ss.is_callable().returns(session)
        import_result = course.get_async_import_result(token)
        assert_that(import_result, has_properties('title', none(),
                                                  'status', 'error',
                                                  'error_message', 'Error during import'))

        running_reply = """
           <status>running</status>
        """
        running_reply = '<rsp stat="ok">%s</rsp>' % running_reply
        running_reply = '<rsp stat="ok">%s</rsp>' % running_reply
        data = fake_response(content=running_reply)
        session = fudge.Fake().expects('get').returns(data)
        mock_ss.is_callable().returns(session)
        import_result = course.get_async_import_result(token)
        assert_that(import_result, has_properties('title', none(),
                                                  'status', 'running',
                                                  'error_message', none()))


        created_reply = """
           <status>created</status>
        """
        created_reply = '<rsp stat="ok">%s</rsp>' % created_reply
        created_reply = '<rsp stat="ok">%s</rsp>' % created_reply
        data = fake_response(content=created_reply)
        session = fudge.Fake().expects('get').returns(data)
        mock_ss.is_callable().returns(session)
        import_result = course.get_async_import_result(token)
        assert_that(import_result, has_properties('title', none(),
                                                  'status', 'created',
                                                  'error_message', none()))


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
                                   'numberOfRegistrations', '2',
                                   'tags', contains_inanyorder('test1', 'test2')))
        assert_that(course_list[1],
                    has_properties('title', 'Another Test Course',
                                   'courseId', 'course321',
                                   'numberOfVersions', '-1',
                                   'numberOfRegistrations', '5',
                                   'tags', []))

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

    @fudge.patch('nti.scorm_cloud.client.request.ServiceRequest.session')
    def test_update_assets(self, mock_ss):
        service = ScormCloudService.withargs("appid", "secret",
                                             "http://cloud.scorm.com/api")
        course = service.get_course_service()

        path = BytesIO(b'data')
        reply = '<success />'
        reply = '<rsp stat="ok">%s</rsp>' % reply
        data = fake_response(content=reply)
        session = fudge.Fake().expects('post').returns(data)
        mock_ss.is_callable().returns(session)

        result = course.update_assets('courseid', path)
        success_nodes = result.getElementsByTagName('success')
        assert_that(success_nodes, is_(not_none()))

    @fudge.patch('nti.scorm_cloud.client.request.ServiceRequest.session')
    def test_update_attributes(self, mock_ss):
        service = ScormCloudService.withargs("appid", "secret",
                                             "http://cloud.scorm.com/api")
        course = service.get_course_service()

        reply = """
        <attributes>
            <attribute name="showCourseStructure" value="false"/>
            <attribute name="showNavBar" value="true"/>
        </attributes>
         """
        reply = '<rsp stat="ok">%s</rsp>' % reply
        data = fake_response(content=reply)
        session = fudge.Fake().expects('get').returns(data)
        mock_ss.is_callable().returns(session)

        result = course.update_attributes('courseid', {'showCourseStructure': False,
                                                       'showNavBar': True})
        assert_that(result,
                    has_entries('showCourseStructure', 'false',
                                'showNavBar', 'true'))
