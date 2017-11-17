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
from hamcrest import starts_with
from hamcrest import has_property
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

    def test_get_launch_url(self):
        service = ScormCloudService.withargs("appid", "secret",
                                             "http://cloud.scorm.com/api")
        reg = service.get_registration_service()
        url = reg.launch("regid", "http://www.myapp.com")
        assert_that(url, starts_with("http://cloud.scorm.com/api?"))

    @fudge.patch('nti.scorm_cloud.client.request.ServiceRequest.session')
    def test_get_launch_history(self, mock_ss):
        service = ScormCloudService.withargs("appid", "secret",
                                             "http://cloud.scorm.com/api")
        reg = service.get_registration_service()

        reply = """
        <launchhistory regid="e222daf6-6005-4344-a07e-0aaa46b21dc9">
            <launch id="c7f31a43">
                <completion>complete</completion>
                <satisfaction>failed</satisfaction>
                <measure_status>1</measure_status>
                <normalized_measure>0.2</normalized_measure>
                <experienced_duration_tracked>2628</experienced_duration_tracked>
                <launch_time>2011-04-05T19:06:37.780+0000</launch_time>
                <exit_time>2011-04-05T19:07:06.616+0000</exit_time>
                <update_dt>2011-04-05T19:07:06.616+0000</update_dt>
            </launch>
        </launchhistory>
        """
        reply = '<rsp stat="ok">%s</rsp>' % reply
        data = fudge.Fake().has_attr(text=reply)
        session = fudge.Fake().expects('get').returns(data)
        mock_ss.is_callable().returns(session)

        history = reg.getLaunchHistory("e222daf6-6005-4344-a07e-0aaa46b21dc9")
        assert_that(history,
                    has_properties('launches', has_length(1),
                                   'regid', 'e222daf6-6005-4344-a07e-0aaa46b21dc9'))

        launch = history.launches[0]
        assert_that(launch,
                    has_properties('id', 'c7f31a43',
                                   'completion', 'complete',
                                   'satisfaction', 'failed',
                                   'measure_status', '1',
                                   'normalized_measure', '0.2',
                                   'experienced_duration_tracked', '2628',
                                   'launch_time', '2011-04-05T19:06:37.780+0000',
                                   'exit_time', '2011-04-05T19:07:06.616+0000',
                                   'update_dt', '2011-04-05T19:07:06.616+0000'))

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
        <registration id="reg123" courseid="course123">
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

    @fudge.patch('nti.scorm_cloud.client.request.ServiceRequest.session')
    def test_get_registration_result(self, mock_ss):
        service = ScormCloudService.withargs("appid", "secret",
                                             "http://cloud.scorm.com/api")
        reg = service.get_registration_service()

        reply = """
        <registrationreport format="summary" regid="myreg001" instanceid="0">
            <complete>complete</complete>
            <success>failed</success>
            <totaltime>19</totaltime>
            <score>0</score>
        </registrationreport>
        """
        reply = '<rsp stat="ok">%s</rsp>' % reply
        data = fudge.Fake().has_attr(text=reply)
        session = fudge.Fake().expects('get').returns(data)
        mock_ss.is_callable().returns(session)

        result = reg.getRegistrationResult("reg123")
        assert_that(result,
                    has_properties('complete', 'complete',
                                   'success', 'failed',
                                   'totaltime', "19",
                                   'format', 'summary',
                                   'score', '0'))

        reply = """
        <registrationreport format="activity" regid="myreg001" instanceid="0">
            <activity id="TOC1">
                <title>Photoshop Example</title>
                <attempts>1</attempts>
                <complete>incomplete</complete>
                <success>unknown</success>
                <time/>
                <score>0</score>
                <children>
                    <activity id="LESSON1">
                      <title>Lesson 1</title>
                      <score>0</score>
                    </activity>
                </children>
            </activity>
        </registrationreport>
        """
        reply = '<rsp stat="ok">%s</rsp>' % reply
        data = fudge.Fake().has_attr(text=reply)
        session = fudge.Fake().expects('get').returns(data)
        mock_ss.is_callable().returns(session)

        result = reg.getRegistrationResult("reg123")
        assert_that(result,
                    has_property('activity',
                                 has_properties('id', 'TOC1',
                                                'attempts', 1,
                                                'complete', "incomplete",
                                                'success', 'unknown',
                                                'score', '0',
                                                'children', has_length(1))))

        reply = """
        <registrationreport format="full" regid="myreg001" instanceid="0">
            <activity id="preTEST">
                <title>Pre Assessment</title>
                <satisfied>true</satisfied>
                <completed>true</completed>
                <progressstatus>true</progressstatus>
                <attempts>1</attempts>
                <suspended>false</suspended>
                <objectives>
                    <objective id="PRIMARYOBJ">
                        <measurestatus>false</measurestatus>
                        <normalizedmeasure>0.0</normalizedmeasure>
                        <progressstatus>true</progressstatus>
                        <satisfiedstatus>true</satisfiedstatus>
                    </objective>
                </objectives>
                <runtime>
                    <completion_status>completed</completion_status>
                    <credit>Credit</credit>
                    <entry>AbInitio</entry>
                    <exit>Unknown</exit>
                    <learnerpreference>
                        <audio_level>1.0</audio_level>
                        <language/>
                        <delivery_speed>1.0</delivery_speed>
                        <audio_captioning>0</audio_captioning>
                    </learnerpreference>
                    <location>null</location>
                    <mode>Normal</mode>
                    <progress_measure/>
                    <score_scaled>68</score_scaled>
                    <score_raw>534</score_raw>
                    <total_time>0000:00:00.00</total_time>
                    <timetracked>0000:00:04.47</timetracked>
                    <success_status>Unknown</success_status>
                    <suspend_data><![CDATA[user data]]></suspend_data>
                    <comments_from_learner>
                        <comment>
                            <value />
                            <location />
                            <date_time />
                        </comment>
                    </comments_from_learner>
                    <comments_from_lms />
                    <interactions>
                        <interaction id="1">
                            <objectives>
                                <objective id="1" />
                            </objectives>
                            <timestamp />
                            <correct_responses>
                                <response id="1" />
                            </correct_responses>
                            <weighting />
                            <learner_response />
                            <result />
                            <latency />
                            <description />
                        </interaction>
                    </interactions>
                    <objectives>
                        <objective id="PRIMARYOBJ">
                            <score_scaled/>
                            <score_min/>
                            <score_raw/>
                            <score_max/>
                            <success_status>unknown</success_status>
                            <completion_status>unknown</completion_status>
                            <progress_measure/>
                            <description>null</description>
                        </objective>
                    </objectives>
                    <static>
                        <completion_threshold/>
                        <launch_data/>
                        <learner_id>daveid</learner_id>
                        <learner_name>dave e</learner_name>
                        <max_time_allowed/>
                        <scaled_passing_score/>
                        <time_limit_action>Undefined</time_limit_action>
                    </static>
                </runtime>
            </activity>
        </registrationreport>
        """
        reply = '<rsp stat="ok">%s</rsp>' % reply
        data = fudge.Fake().has_attr(text=reply)
        session = fudge.Fake().expects('get').returns(data)
        mock_ss.is_callable().returns(session)

        result = reg.getRegistrationResult("reg123")
        assert_that(result,
                    has_property('activity',
                                 has_properties('id', 'preTEST',
                                                'title', 'Pre Assessment',
                                                'suspended', False,
                                                'progressstatus', True,
                                                'objectives', has_length(1),
                                                'runtime',
                                                has_properties('completion_status', 'completed',
                                                               'credit', 'Credit',
                                                               'mode', 'Normal',
                                                               'score_raw', '534',
                                                               'timetracked', '0000:00:04.47',
                                                               'learnerpreference',
                                                               has_properties('audio_level', '1.0',
                                                                              'delivery_speed', '1.0'),
                                                               'static',
                                                               has_properties('learner_id', 'daveid',
                                                                              'learner_name', 'dave e',
                                                                              'time_limit_action', 'Undefined'),
                                                               'objectives', has_length(
                                                                   1),
                                                               'interactions', has_length(1)))))

        assert_that(result.activity.objectives[0],
                    has_properties('id', "PRIMARYOBJ",
                                   'normalizedmeasure', 0.0,
                                   'measurestatus', False,
                                   'progressstatus', True,
                                   'satisfiedstatus', True))

        assert_that(result.activity.runtime.objectives[0],
                    has_properties('id', "PRIMARYOBJ",
                                   'success_status', "unknown"))

        assert_that(result.activity.runtime.interactions[0],
                    has_properties('id', "1",
                                   'objectives', has_length(1),
                                   'correct_responses', has_length(1)))
