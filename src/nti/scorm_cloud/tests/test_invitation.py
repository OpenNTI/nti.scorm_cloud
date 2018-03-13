#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=protected-access,too-many-public-methods

from hamcrest import is_
from hamcrest import has_length
from hamcrest import assert_that
from hamcrest import has_properties

import unittest

import fudge

from nti.scorm_cloud.client.invitation import InvitationInfo

from nti.scorm_cloud.client.request import ScormCloudError

from nti.scorm_cloud.client.scorm import ScormCloudService

from nti.scorm_cloud.tests import SharedConfiguringTestLayer


class TestInvitationService(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    @fudge.patch('nti.scorm_cloud.client.request.ServiceRequest.session')
    def test_create_invitation(self, mock_ss):
        service = ScormCloudService.withargs("appid", "secret",
                                             "http://cloud.scorm.com/api")
        invitation = service.get_invitation_service()

        reply = '<rsp stat="ok">937296cb-ae79-4190-bb6f-9a39b97785ac</rsp>'
        data = fudge.Fake().has_attr(content=reply)
        session = fudge.Fake().expects('get').returns(data)
        mock_ss.is_callable().returns(session)

        for method in ('createInvitation', 'createInvitationAsync'):
            method = getattr(invitation, method)
            iden = method("mycourseid", True, True,
                          "myemail@sample.com",
                          "email subject", "email body",
                          True, 1,
                          "http://mysite.org",
                          "httpbasic", "myname", "mypassword",
                          "activity", "20171130152345")
            assert_that(iden, is_('937296cb-ae79-4190-bb6f-9a39b97785ac'))

    @fudge.patch('nti.scorm_cloud.client.request.ServiceRequest.session')
    def test_get_invitation_status(self, mock_ss):
        service = ScormCloudService.withargs("appid", "secret",
                                             "http://cloud.scorm.com/api")
        invitation = service.get_invitation_service()

        reply = '<rsp stat="ok"><status>complete</status></rsp>'
        data = fudge.Fake().has_attr(content=reply)
        session = fudge.Fake().expects('get').returns(data)
        mock_ss.is_callable().returns(session)

        assert_that(invitation.getInvitationStatus('937296cb-ae79-4190-bb6f-9a39b97785ac'),
                    is_('complete'))

    @fudge.patch('nti.scorm_cloud.client.request.ServiceRequest.session')
    def test_get_invitation_info(self, mock_ss):
        service = ScormCloudService.withargs("appid", "secret",
                                             "http://cloud.scorm.com/api")
        service = service.get_invitation_service()

        reply = """
        <invitationInfo>
            <id><![CDATA[35568984-16cf-4d81-92dd-ea69eb4dacd4]]></id>
            <body><![CDATA[Dear [USER],<p>You have been invited to take 'Feedback 1.2 invite app'. To start your training click on the Play button or copy the training URL into your browser.</p><a href='[URL]'>Play course</a><br><br>URL: [URL]]]></body>
            <courseId><![CDATA[Feedback1.2inviteapp00ec1901-a17c-4165-9294-fdb105707541]]></courseId>
            <subject><![CDATA[Feedback 1.2 invite app]]></subject>
            <url/>
            <allowLaunch>true</allowLaunch>
            <allowNewRegistrations>true</allowNewRegistrations>
            <public>false</public>
            <created>true</created>
            <createdDate>2012-05-02T22:13:47.503+0000</createdDate>
            <userInvitations>
                <userInvitation>
                    <email><![CDATA[email1@scorm.com]]></email>
                    <url><![CDATA[http://cloud.scorm.com/fasttrack/InvitationLaunch?userInvitationId=12af1419-7d4d-464a-9c24-e3b0271272e0]]></url>
                    <isStarted>false</isStarted>
                    <registrationId><![CDATA[as5a3fe8-8e02-4677-af83-f6d818256278]]></registrationId>
                    <registrationreport format="course" regid="as5a3fe8-8e02-4677-af83-f6d818256278" instanceid="0">
                        <complete>unknown</complete>
                        <success>unknown</success>
                        <totaltime>0</totaltime>
                        <score>unknown</score>
                    </registrationreport>
                </userInvitation>
                <userInvitation>
                    <email><![CDATA[email2@scorm.com]]></email>
                    <url><![CDATA[http://cloud.scorm.com/fasttrack/InvitationLaunch?userInvitationId=288bc606-765f-4c28-bf10-cb219ca8d9cd]]></url>
                    <isStarted>false</isStarted>
                    <registrationId><![CDATA[b2103cd4-8d94-44da-8e25-b0b8822e567b]]></registrationId>
                    <registrationreport format="course" regid="b2103cd4-8d94-44da-8e25-b0b8822e567b" instanceid="0">
                        <complete>unknown</complete>
                        <success>unknown</success>
                        <totaltime>0</totaltime>
                        <score>unknown</score>
                    </registrationreport>
                </userInvitation>
            </userInvitations>
        </invitationInfo>
        """
        reply = '<rsp stat="ok">%s</rsp>' % reply
        data = fudge.Fake().has_attr(content=reply)
        session = fudge.Fake().expects('get').returns(data)
        mock_ss.is_callable().returns(session)

        info = service.getInvitationInfo('35568984-16cf-4d81-92dd-ea69eb4dacd4', True)
        assert_that(info, is_(InvitationInfo))

        assert_that(info,
                    has_properties('id', '35568984-16cf-4d81-92dd-ea69eb4dacd4',
                                   'courseId', 'Feedback1.2inviteapp00ec1901-a17c-4165-9294-fdb105707541',
                                   'allowLaunch', is_(True),
                                   'createdDate', '2012-05-02T22:13:47.503+0000',
                                   'userInvitations', has_length(2)))

        ui = info.userInvitations[0]
        assert_that(ui,
                    has_properties('email', 'email1@scorm.com',
                                   'url', 'http://cloud.scorm.com/fasttrack/InvitationLaunch?userInvitationId=12af1419-7d4d-464a-9c24-e3b0271272e0',
                                   'isStarted', is_(False),
                                   'registrationId', 'as5a3fe8-8e02-4677-af83-f6d818256278',
                                   'registrationreport', has_properties('format', 'course',
                                                                        'regid', 'as5a3fe8-8e02-4677-af83-f6d818256278',
                                                                        'instanceid', '0',
                                                                        'totaltime', '0',
                                                                        'score', 'unknown')))

    @fudge.patch('nti.scorm_cloud.client.request.ServiceRequest.session')
    def test_get_invitation_list(self, mock_ss):
        service = ScormCloudService.withargs("appid", "secret",
                                             "http://cloud.scorm.com/api")
        service = service.get_invitation_service()

        reply = """
        <invitationlist>
            <invitationInfo>
                <id><![CDATA[35568984-16cf-4d81-92dd-ea69eb4dacd4]]></id>
                <body><![CDATA[Dear [USER],<p>You have been invited to take 'Feedback 1.2 invite app'. To start your training click on the Play button or copy the training URL into your browser.</p><a href='[URL]'>Play course</a><br><br>URL: [URL]]]></body>
                <courseId><![CDATA[Feedback1.2inviteapp00ec1901-a17c-4165-9294-fdb105707541]]></courseId>
                <subject><![CDATA[Feedback 1.2 invite app]]></subject>
                <url/>
                <allowLaunch>true</allowLaunch>
                <allowNewRegistrations>true</allowNewRegistrations>
                <public>false</public>
                <created>true</created>
                <createdDate>2012-05-02T22:13:47.503+0000</createdDate>
                <userInvitations/>
            </invitationInfo>
        </invitationlist>
        """
        reply = '<rsp stat="ok">%s</rsp>' % reply
        data = fudge.Fake().has_attr(content=reply)
        session = fudge.Fake().expects('get').returns(data)
        mock_ss.is_callable().returns(session)

        assert_that(service.getInvitationList('92dd', 'Feeback'), 
                    has_length(1))

    @fudge.patch('nti.scorm_cloud.client.request.ServiceRequest.session')
    def test_change_status(self, mock_ss):
        service = ScormCloudService.withargs("appid", "secret",
                                             "http://cloud.scorm.com/api")
        service = service.get_invitation_service()

        reply = '<rsp stat="ok"><success/></rsp>'
        data = fudge.Fake().has_attr(content=reply)
        session = fudge.Fake().expects('get').returns(data)
        mock_ss.is_callable().returns(session)

        service.changeStatus('35568984-16cf-4d81-92dd-ea69eb4dacd4',
                             True, True, '20171130152345')
        
        reply = '<rsp stat="ok"><failed/></rsp>'
        data = fudge.Fake().has_attr(content=reply)
        session = fudge.Fake().expects('get').returns(data)
        mock_ss.is_callable().returns(session)

        with self.assertRaises(ScormCloudError):
            service.changeStatus('35568984-16cf-4d81-92dd-ea69eb4dacd4', True)
