#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import not_none
from hamcrest import has_length
from hamcrest import assert_that
from hamcrest import has_properties

import unittest

import fudge

from nti.scorm_cloud.client.request import ScormCloudError

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

        reply = '<rsp stat="ok"><failed/></rsp>'
        data = fudge.Fake().has_attr(text=reply)
        session = fudge.Fake().expects('get').returns(data)
        mock_ss.is_callable().returns(session)

        with self.assertRaises(ScormCloudError):
            reg.createRegistration("bankai", None,
                                   'Ichigo', 'Kurosaki',
                                   'ichigo@bleach.org',
                                   'ichigo@bleach.org',
                                   "http://bleach.org",
                                   "httpbasic", "ichigo", "zangetsu",
                                   "course")

    @fudge.patch('nti.scorm_cloud.client.request.ServiceRequest.session')
    def test_exists(self, mock_ss):
        service = ScormCloudService.withargs("appid", "secret",
                                             "http://cloud.scorm.com/api")
        reg = service.get_registration_service()

        reply = '<rsp stat="ok"><result>false</result></rsp>'
        data = fudge.Fake().has_attr(text=reply)
        session = fudge.Fake().expects('get').returns(data)
        mock_ss.is_callable().returns(session)

        regid = reg.exists("bankai")
        assert_that(regid, is_(False))

    @fudge.patch('nti.scorm_cloud.client.request.ServiceRequest.session')
    def test_delete_registration(self, mock_ss):
        service = ScormCloudService.withargs("appid", "secret",
                                             "http://cloud.scorm.com/api")
        reg = service.get_registration_service()

        reply = '<rsp stat="ok"><success/></rsp>'
        data = fudge.Fake().has_attr(text=reply)
        session = fudge.Fake().expects('get').returns(data)
        mock_ss.is_callable().returns(session)

        reg.deleteRegistration("bankai")

        reply = '<rsp stat="ok"><failed/></rsp>'
        data = fudge.Fake().has_attr(text=reply)
        session = fudge.Fake().expects('get').returns(data)
        mock_ss.is_callable().returns(session)
        with self.assertRaises(ScormCloudError):
            reg.deleteRegistration("bankai")

    @fudge.patch('nti.scorm_cloud.client.request.ServiceRequest.session')
    def test_reset_registration(self, mock_ss):
        service = ScormCloudService.withargs("appid", "secret",
                                             "http://cloud.scorm.com/api")
        reg = service.get_registration_service()

        reply = '<rsp stat="ok"><success/></rsp>'
        data = fudge.Fake().has_attr(text=reply)
        session = fudge.Fake().expects('get').returns(data)
        mock_ss.is_callable().returns(session)

        reg.resetRegistration("bankai")

        reply = '<rsp stat="ok"><failed/></rsp>'
        data = fudge.Fake().has_attr(text=reply)
        session = fudge.Fake().expects('get').returns(data)
        mock_ss.is_callable().returns(session)
        with self.assertRaises(ScormCloudError):
            reg.resetRegistration("bankai")

    @fudge.patch('nti.scorm_cloud.client.request.ServiceRequest.session')
    def test_get_registration_list(self, mock_ss):
        service = ScormCloudService.withargs("appid", "secret",
                                             "http://cloud.scorm.com/api")
        reg = service.get_registration_service()

        reply = """
        <registrationlist>
            <registration id="reg4" courseid="test321">
                <appId>myappid</appId>
                <registrationId>reg4</registrationId>
                <courseId>test321</courseId>
                <courseTitle>Test Course</courseTitle>
                <learnerId>test_learner</learnerId>
                <learnerFirstName>Test</learnerFirstName>
                <learnerLastName>Learner</learnerLastName>
                <email>test@test.com</email>
                <createDate>2011-03-23T14:00:45.000+0000</createDate>
                <firstAccessDate>2011-06-06T16:08:18.000+0000</firstAccessDate>
                <lastAccessDate>2011-06-06T16:36:12.000+0000</lastAccessDate>
                <completedDate>2011-06-06T16:36:12.000+0000</completedDate>
                <instances />
            </registration>
        </registrationlist>
        """
        reply = '<rsp stat="ok">%s</rsp>' % reply
        data = fudge.Fake().has_attr(text=reply)
        session = fudge.Fake().expects('get').returns(data)
        mock_ss.is_callable().returns(session)

        registrations = reg.getRegistrationList(after="2011-02-01T21:39:23Z")
        assert_that(registrations, has_length(1))

        assert_that(registrations[0],
                    has_properties('appId', 'myappid',
                                   'registrationId', 'reg4',
                                   'courseId', 'test321',
                                   'courseTitle', 'Test Course',
                                   'learnerId', 'test_learner',
                                   'learnerFirstName', 'Test',
                                   'learnerLastName', 'Learner',
                                   'email', 'test@test.com',
                                   'createDate', '2011-03-23T14:00:45.000+0000',
                                   'instances', has_length(0)))
        
    @fudge.patch('nti.scorm_cloud.client.request.ServiceRequest.session')
    def test_get_registration_detail(self, mock_ss):
        service = ScormCloudService.withargs("appid", "secret",
                                             "http://cloud.scorm.com/api")
        reg = service.get_registration_service()

        reply = """
        <registration id="reg123" courseid="SequencingForcedSequential_SCORM20043rdEditionb0535515-a4c9-4dad-bd85-04bcc54f96b7">
            <appId><![CDATA[myappid]]></appId>
            <registrationId><![CDATA[reg123]]></registrationId>
            <courseId><![CDATA[course123]]></courseId>
            <courseTitle><![CDATA[Golf Explained - Sequencing Forced]]></courseTitle>
            <lastCourseVersionLaunched><![CDATA[2]]></lastCourseVersionLaunched>
            <learnerId><![CDATA[test@test.com]]></learnerId>
            <learnerFirstName><![CDATA[Test]]></learnerFirstName>
            <learnerLastName><![CDATA[Man]]></learnerLastName>
            <email><![CDATA[test@test.com]]></email>
            <createDate><![CDATA[2011-07-25T20:05:01.000+0000]]></createDate>
            <firstAccessDate><![CDATA[2011-07-25T20:23:44.000+0000]]></firstAccessDate>
            <lastAccessDate><![CDATA[2011-07-25T20:55:09.000+0000]]></lastAccessDate>
            <completedDate><![CDATA[2011-07-25T20:33:20.000+0000]]></completedDate>
            <instances>
                <instance>
                    <instanceId><![CDATA[0]]></instanceId>
                    <courseVersion><![CDATA[1]]></courseVersion>
                    <updateDate><![CDATA[2011-07-25T20:33:20.000+0000]]></updateDate>
                </instance>
                <instance>
                    <instanceId><![CDATA[1]]></instanceId>
                    <courseVersion><![CDATA[2]]></courseVersion>
                    <updateDate><![CDATA[2011-07-25T20:55:08.000+0000]]></updateDate>
                </instance>
            </instances>
        </registration>
        """
        reply = '<rsp stat="ok">%s</rsp>' % reply
        data = fudge.Fake().has_attr(text=reply)
        session = fudge.Fake().expects('get').returns(data)
        mock_ss.is_callable().returns(session)

        registration = reg.getRegistrationDetail("reg123")
        assert_that(registration,
                    has_properties('appId', 'myappid',
                                   'courseId', 'course123',
                                   'instances', has_length(2)))
