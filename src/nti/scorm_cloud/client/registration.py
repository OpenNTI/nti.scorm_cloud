#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import uuid

from zope import interface

from nti.scorm_cloud.client.request import ScormCloudError

from nti.scorm_cloud.interfaces import IRegistrationService

logger = __import__('logging').getLogger(__name__)


@interface.implementer(IRegistrationService)
class RegistrationService(object):

    def __init__(self, service):
        self.service = service

    def create_registration(self, regid, courseid, userid, fname, lname,
                            email=None, learnerTags=None, courseTags=None,
                            registrationTags=None):
        if not regid:
            regid = str(uuid.uuid1())
        request = self.service.request()
        request.parameters['appid'] = self.service.config.appid
        request.parameters['courseid'] = courseid
        request.parameters['regid'] = regid
        request.parameters['fname'] = fname
        request.parameters['lname'] = lname
        request.parameters['learnerid'] = userid
        if email:
            request.parameters['email'] = email
        if learnerTags:
            request.parameters['learnerTags'] = learnerTags
        if courseTags:
            request.parameters['courseTags'] = courseTags
        if registrationTags is not None:
            request.parameters['registrationTags'] = registrationTags
        xmldoc = request.call_service(
            'rustici.registration.createRegistration')
        successNodes = xmldoc.getElementsByTagName('success')
        if successNodes is None or successNodes.length == 0:
            raise ScormCloudError("Create Registration failed.  " +
                                  xmldoc.err.attributes['msg'])
        return regid

    def get_launch_url(self, regid, redirecturl, cssUrl=None, courseTags=None,
                       learnerTags=None, registrationTags=None):
        request = self.service.request()
        request.parameters['regid'] = regid
        request.parameters['redirecturl'] = redirecturl + '?regid=' + regid
        if cssUrl:
            request.parameters['cssurl'] = cssUrl
        if courseTags:
            request.parameters['coursetags'] = courseTags
        if learnerTags:
            request.parameters['learnertags'] = learnerTags
        if registrationTags:
            request.parameters['registrationTags'] = registrationTags
        url = request.construct_url('rustici.registration.launch')
        return url

    def get_registration_list(self, regIdFilterRegex=None, courseIdFilterRegex=None):
        request = self.service.request()
        if regIdFilterRegex:
            request.parameters['filter'] = regIdFilterRegex
        if courseIdFilterRegex:
            request.parameters['coursefilter'] = courseIdFilterRegex
        result = request.call_service(
            'rustici.registration.getRegistrationList')
        regs = RegistrationData.list_from_result(result)
        return regs

    def get_registration_result(self, regid, resultsformat):
        request = self.service.request()
        request.parameters['regid'] = regid
        request.parameters['resultsformat'] = resultsformat
        return request.call_service('rustici.registration.getRegistrationResult')

    def get_launch_history(self, regid):
        request = self.service.request()
        request.parameters['regid'] = regid
        return request.call_service('rustici.registration.getLaunchHistory')

    def reset_registration(self, regid):
        request = self.service.request()
        request.parameters['regid'] = regid
        return request.call_service('rustici.registration.resetRegistration')

    def reset_global_objectives(self, regid):
        request = self.service.request()
        request.parameters['regid'] = regid
        return request.call_service('rustici.registration.resetGlobalObjectives')

    def delete_registration(self, regid):
        request = self.service.request()
        request.parameters['regid'] = regid
        return request.call_service('rustici.registration.deleteRegistration')


class RegistrationData(object):

    courseId = ""
    registrationId = ""

    def __init__(self, regDataElement):
        if regDataElement is not None:
            self.courseId = regDataElement.attributes['courseid'].value
            self.registrationId = regDataElement.attributes['id'].value

    @classmethod
    def list_from_result(cls, xmldoc):
        """
        Returns a list of RegistrationData objects by parsing the result of an
        API method that returns registration elements.

        Arguments:
        data -- the raw result of the API method
        """
        allResults = []
        regs = xmldoc.getElementsByTagName("registration")
        for reg in regs:
            allResults.append(cls(reg))
        return allResults
