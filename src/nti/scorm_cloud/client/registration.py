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

from nti.scorm_cloud.client.mixins import RegistrationMixin

from nti.scorm_cloud.minidom import getChildren
from nti.scorm_cloud.minidom import getChildText
from nti.scorm_cloud.minidom import getFirstChild
from nti.scorm_cloud.minidom import getAttributeValue
from nti.scorm_cloud.minidom import getChildTextOrCDATA

logger = __import__('logging').getLogger(__name__)


@interface.implementer(IRegistrationService)
class RegistrationService(object):

    def __init__(self, service):
        self.service = service

    def createRegistration(self, courseid, regid, fname, lname, learnerid,
                           email=None, postbackurl=None, authtype=None, urlname=None,
                           urlpass=None, resultsformat=None):
        regid = regid or str(uuid.uuid1())
        request = self.service.request()
        request.parameters['regid'] = regid
        request.parameters['fname'] = fname
        request.parameters['lname'] = lname
        request.parameters['courseid'] = courseid
        request.parameters['learnerid'] = learnerid
        request.parameters['appid'] = self.service.config.appid
        if email:
            request.parameters['email'] = email
        if postbackurl:
            request.parameters['postbackurl'] = postbackurl
        if authtype:
            request.parameters['authtype'] = authtype
        if urlname:
            request.parameters['urlname'] = urlname
        if urlpass:
            request.parameters['urlpass'] = urlpass
        if resultsformat:
            request.parameters['resultsformat'] = resultsformat
        xmldoc = request.call_service('rustici.registration.createRegistration')
        successNodes = xmldoc.getElementsByTagName('success')
        if not successNodes:
            raise ScormCloudError("Create Registration failed.")
        return regid
    create_registration = createRegistration

    def exists(self, regid):
        request = self.service.request()
        request.parameters['regid'] = regid
        request.parameters['appid'] = self.service.config.appid
        xmldoc = request.call_service('rustici.registration.exists')
        result = xmldoc.documentElement.firstChild.firstChild.nodeValue
        return result == 'true'

    def deleteRegistration(self, regid):
        request = self.service.request()
        request.parameters['regid'] = regid
        xmldoc = request.call_service('rustici.registration.deleteRegistration')
        successNodes = xmldoc.getElementsByTagName('success')
        if not successNodes:
            raise ScormCloudError("Delete Registration failed.")
    delete_registration = deleteRegistration

    def resetRegistration(self, regid):
        request = self.service.request()
        request.parameters['regid'] = regid
        xmldoc = request.call_service('rustici.registration.resetRegistration')
        successNodes = xmldoc.getElementsByTagName('success')
        if not successNodes:
            raise ScormCloudError("Reset Registration failed.")
    reset_registration = resetRegistration

    def getRegistrationList(self, courseid=None, learnerid=None, after=None, until=None):
        request = self.service.request()
        if courseid:
            request.parameters['courseid'] = courseid
        if learnerid:
            request.parameters['learnerid'] = learnerid
        if after:
            request.parameters['after'] = after
        if until:
            request.parameters['until'] = until
        xmldoc = request.call_service('rustici.registration.getRegistrationList')
        nodes = xmldoc.documentElement.getElementsByTagName('registration')
        return [Registration.fromMinidom(n) for n in nodes or ()]
    get_registration_list = getRegistrationList

    def getRegistrationDetail(self, regid):
        request = self.service.request()
        request.parameters['regid'] = regid
        xmldoc = request.call_service('rustici.registration.getRegistrationDetail')
        nodes = xmldoc.getElementsByTagName('registration')
        return Registration.fromMinidom(nodes[0]) if nodes else None
    get_registration_detail = getRegistrationDetail

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

    def get_registration_result(self, regid, resultsformat):
        request = self.service.request()
        request.parameters['regid'] = regid
        request.parameters['resultsformat'] = resultsformat
        return request.call_service('rustici.registration.getRegistrationResult')

    def get_launch_history(self, regid):
        request = self.service.request()
        request.parameters['regid'] = regid
        return request.call_service('rustici.registration.getLaunchHistory')

    def reset_global_objectives(self, regid):
        request = self.service.request()
        request.parameters['regid'] = regid
        return request.call_service('rustici.registration.resetGlobalObjectives')


class Instance(object):

    def __init__(self, instanceId, courseVersion=None, updateDate=None):
        self.instanceId = instanceId
        self.updateDate = updateDate
        self.courseVersion = courseVersion

    @classmethod
    def fromMinidom(cls, node):
        return cls(getChildTextOrCDATA(node, 'instanceId'),
                   getChildTextOrCDATA(node, 'courseVersion'),
                   getChildTextOrCDATA(node, 'updateDate'))


class Registration(object):

    def __init__(self, appId, registrationId, courseId,
                 courseTitle=None, lastCourseVersionLaunched=None,
                 learnerId=None, learnerFirstName=None, learnerLastName=None,
                 email=None, createDate=None, firstAccessDate=None, lastAccessDate=None,
                 completedDate=None, instances=()):

        self.appId = appId
        self.email = email
        self.courseId = courseId
        self.instances = instances
        self.learnerId = learnerId
        self.createDate = createDate
        self.courseTitle = courseTitle
        self.completedDate = completedDate
        self.lastAccessDate = lastAccessDate
        self.registrationId = registrationId
        self.firstAccessDate = firstAccessDate
        self.learnerLastName = learnerLastName
        self.learnerFirstName = learnerFirstName
        self.lastCourseVersionLaunched = lastCourseVersionLaunched

    @classmethod
    def fromMinidom(cls, node):
        instances = []
        for n in getChildren(node, 'instances', 'instance') or ():
            instances.append(Instance.fromMinidom(n))
        return cls(getChildTextOrCDATA(node, 'appId'),
                   getChildTextOrCDATA(node, 'registrationId'),
                   getChildTextOrCDATA(node, 'courseId'),
                   getChildTextOrCDATA(node, 'courseTitle'),
                   getChildTextOrCDATA(node, 'lastCourseVersionLaunched'),
                   getChildTextOrCDATA(node, 'learnerId'),
                   getChildTextOrCDATA(node, 'learnerFirstName'),
                   getChildTextOrCDATA(node, 'learnerLastName'),
                   getChildTextOrCDATA(node, 'email'),
                   getChildTextOrCDATA(node, 'createDate'),
                   getChildTextOrCDATA(node, 'firstAccessDate'),
                   getChildTextOrCDATA(node, 'lastAccessDate'),
                   getChildTextOrCDATA(node, 'completedDate'),
                   instances or ())


class RegistrationReport(RegistrationMixin):

    def __init__(self, format_, regid=None, instanceid=None,
                 complete=None, success=None, totaltime=0, score=None,
                 activity=None):
        RegistrationMixin.__init__(self, format_, regid, instanceid)
        self.score = score
        self.success = success
        self.activity = activity
        self.complete = complete
        self.totaltime = totaltime

    @classmethod
    def fromMinidom(cls, node):
        activity = getFirstChild(node, 'activity')
        activity = Activity.fromMinidom(activity) if activity else None
        return cls(getAttributeValue(node, 'format'),
                   getAttributeValue(node, 'regid'),
                   getAttributeValue(node, 'instanceid'),
                   getChildText(node, 'complete'),
                   getChildText(node, 'success'),
                   getChildText(node, 'totaltime'),
                   getChildText(node, 'score'),
                   activity)


class Objective(object):

    def __init__(self, id_, measurestatus=False, normalizedmeasure=0.0,
                 progressstatus=False, satisfiedstatus=False,
                 score_scaled=None, score_min=None, score_raw=None,
                 success_status=None, completion_status=None, progress_measure=None,
                 description=None):

        self.id = id_
        self.score_min = score_min
        self.score_raw = score_raw
        self.description = description
        self.score_scaled = score_scaled
        self.measurestatus = measurestatus
        self.progressstatus = progressstatus
        self.success_status = success_status
        self.satisfiedstatus = satisfiedstatus
        self.progress_measure = progress_measure
        self.completion_status = completion_status
        self.normalizedmeasure = normalizedmeasure

    @classmethod
    def fromMinidom(cls, node):
        return cls(getAttributeValue(node, 'id'),
                   getChildText(node, 'measurestatus') == 'true',
                   float(getChildText(node, 'normalizedmeasure') or '0.0'),
                   getChildText(node, 'progressstatus') == 'true',
                   getChildText(node, 'satisfiedstatus') == 'true',
                   getChildText(node, 'score_scaled'),
                   getChildText(node, 'score_min'),
                   getChildText(node, 'score_raw'),
                   getChildText(node, 'success_status'),
                   getChildText(node, 'completion_status'),
                   getChildText(node, 'progress_measure'),
                   getChildText(node, 'description'))


class Activity(object):

    def __init__(self, id_, title, satisfied=False,
                 completed=False, progressstatus=False, attempts=1,
                 suspended=False, time_=None, score=None,
                 objectives=(), children=()):
        self.id = id_
        self.time = time_
        self.title = title
        self.score = score
        self.attempts = attempts
        self.children = children
        self.suspended = suspended
        self.completed = completed
        self.satisfied = satisfied
        self.objectives = objectives
        self.progressstatus = progressstatus

    @classmethod
    def fromMinidom(cls, node):
        objectives = []
        for n in getChildren(node, 'objectives', 'objective') or ():
            objectives.append(Objective.fromMinidom(n))
        children = []
        for n in getChildren(node, 'children', 'activity') or ():
            children.append(Activity.fromMinidom(n))
        return cls(getAttributeValue(node, 'id'),
                   getChildText(node, 'title'),
                   getChildText(node, 'satisfied') == 'true',
                   getChildText(node, 'completed') == 'true',
                   getChildText(node, 'progressstatus') == 'true',
                   int(getChildText(node, 'attempts') or '0'),
                   getChildText(node, 'time'),
                   getChildText(node, 'score'),
                   objectives or (),
                   children or ())
