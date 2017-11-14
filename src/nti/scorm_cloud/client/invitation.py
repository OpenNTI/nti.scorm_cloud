#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from zope import interface

from nti.scorm_cloud.interfaces import IInvitationService

from nti.scorm_cloud.client.request import ScormCloudError

from nti.scorm_cloud.minidom import getChildText
from nti.scorm_cloud.minidom import getChildCDATA
from nti.scorm_cloud.minidom import getAttributeValue

logger = __import__('logging').getLogger(__name__)


@interface.implementer(IInvitationService)
class InvitationService(object):

    def __init__(self, service):
        self.service = service

    def create_invitation(self, courseid, public=True, send=True, addresses=None,
                          emailSubject=None, emailBody=None, creatingUserEmail=None,
                          registrationCap=None, postbackurl=None, authtype=None, urlname=None,
                          urlpass=None, resultsformat=None, expirationdate=None, async_=False):
        request = self.service.request()

        request.parameters['courseid'] = courseid
        request.parameters['send'] = str(send).lower()
        request.parameters['public'] = str(public).lower()

        if addresses:
            request.parameters['addresses'] = addresses
        if emailSubject:
            request.parameters['emailSubject'] = emailSubject
        if emailBody:
            request.parameters['emailBody'] = emailBody
        if creatingUserEmail:
            request.parameters['creatingUserEmail'] = creatingUserEmail
        if registrationCap:
            request.parameters['registrationCap'] = registrationCap
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
        if expirationdate:
            request.parameters['expirationdate'] = expirationdate

        if async_:
            xmldoc = request.call_service('rustici.invitation.createInvitationAsync')
        else:
            xmldoc = request.call_service('rustici.invitation.createInvitation')
        return xmldoc.documentElement.firstChild.nodeValue

    def createInvitation(self, courseid, public=True, send=True, addresses=None,
                         emailSubject=None, emailBody=None, creatingUserEmail=None,
                         registrationCap=None, postbackurl=None, authtype=None, urlname=None,
                         urlpass=None, resultsformat=None, expirationdate=None):

        return self.create_invitation(courseid, public, send, addresses, emailSubject, emailBody,
                                      creatingUserEmail, registrationCap, postbackurl, authtype,
                                      urlname, urlpass, resultsformat, expirationdate, False)

    def createInvitationAsync(self, courseid, public=True, send=True, addresses=None,
                              emailSubject=None, emailBody=None, creatingUserEmail=None,
                              registrationCap=None, postbackurl=None, authtype=None, urlname=None,
                              urlpass=None, resultsformat=None, expirationdate=None):

        return self.create_invitation(courseid, public, send, addresses, emailSubject, emailBody,
                                      creatingUserEmail, registrationCap, postbackurl, authtype,
                                      urlname, urlpass, resultsformat, expirationdate, True)

    def getInvitationList(self, filter_=None, coursefilter=None):
        request = self.service.request()
        if filter_ is not None:
            request.parameters['filter'] = filter_
        if coursefilter is not None:
            request.parameters['coursefilter'] = coursefilter
        xmldoc = request.call_service('rustici.invitation.getInvitationList')
        nodes = xmldoc.documentElement.getElementsByTagName('invitationInfo')
        return [InvitationInfo.fromMinidom(n) for n in nodes or ()]
    get_invitation_list = getInvitationList

    def getInvitationStatus(self, invitationId):
        request = self.service.request()
        request.parameters['invitationId'] = invitationId
        xmldoc = request.call_service('rustici.invitation.getInvitationStatus')
        return xmldoc.documentElement.firstChild.firstChild.nodeValue
    get_invitation_status = getInvitationStatus

    def getInvitationInfo(self, invitationId, detail=False):
        request = self.service.request()
        request.parameters['invitationId'] = invitationId
        request.parameters['detail'] = str(detail).lower()
        xmldoc = request.call_service('rustici.invitation.getInvitationInfo')
        nodes = xmldoc.documentElement.getElementsByTagName('invitationInfo')
        return InvitationInfo.fromMinidom(nodes[0]) if nodes else None
    get_invitation_info = getInvitationInfo

    def changeStatus(self, invitationId, enable, open_=None, expirationdate=None):
        request = self.service.request()
        request.parameters['invitationId'] = invitationId
        request.parameters['enable'] = str(enable).lower()
        if open_ is not None:
            assert isinstance(open_, bool)
            request.parameters['open'] = str(open_).lower()
        if expirationdate is not None:
            request.parameters['expirationdate'] = expirationdate
        xmldoc = request.call_service('rustici.invitation.changeStatus')
        successNodes = xmldoc.getElementsByTagName('success')
        if not successNodes:
            raise ScormCloudError("Change Status failed.")
    change_status = changeStatus


class RegistrationReport(object):

    def __init__(self, format_, regid=None, instanceid=None,
                 complete=None, success=None, totaltime=0, score=None):
        self.regid = regid
        self.score = score
        self.format = format_
        self.success = success
        self.complete = complete
        self.totaltime = totaltime
        self.instanceid = instanceid

    @classmethod
    def fromMinidom(cls, node):
        return cls(getAttributeValue(node, 'format'),
                   getAttributeValue(node, 'regid'),
                   getAttributeValue(node, 'instanceid'),
                   getChildText(node, 'complete'),
                   getChildText(node, 'success'),
                   getChildText(node, 'totaltime'),
                   getChildText(node, 'score'))


class UserInvitation(object):

    def __init__(self, email, url=None, isStarted=None, registrationId=None,
                 registrationreport=None):
        self.url = url
        self.email = email
        self.isStarted = isStarted
        self.registrationId = registrationId
        self.registrationreport = registrationreport

    @classmethod
    def fromMinidom(cls, node):
        nodes = node.getElementsByTagName('registrationreport')
        report = RegistrationReport.fromMinidom(nodes[0]) if nodes else None
        return cls(getChildCDATA(node, 'email'),
                   getChildCDATA(node, 'url'),
                   getChildText(node, 'isStarted') == 'true',
                   getChildCDATA(node, 'registrationId'),
                   report)


class InvitationInfo(object):

    def __init__(self, id_, body=None, courseId=None, subject=None,
                 url=None, allowLaunch=True, allowNewRegistrations=True,
                 public=True, created=True, createdDate=None, userInvitations=()):
        self.id = id_
        self.url = url
        self.body = body
        self.public = public
        self.created = created
        self.subject = subject
        self.courseId = courseId
        self.allowLaunch = allowLaunch
        self.createdDate = createdDate
        self.userInvitations = userInvitations
        self.allowNewRegistrations = allowNewRegistrations

    @classmethod
    def fromMinidom(cls, node):
        userInvitations = []
        for child in node.getElementsByTagName('userInvitation') or ():
            userInvitations.append(UserInvitation.fromMinidom(child))
        return cls(getChildCDATA(node, 'id'),
                   getChildCDATA(node, 'body'),
                   getChildCDATA(node, 'courseId'),
                   getChildCDATA(node, 'subject'),
                   getChildCDATA(node, 'url'),
                   getChildText(node, 'allowLaunch') == 'true',
                   getChildText(node, 'allowNewRegistrations') == 'true',
                   getChildText(node, 'public') == 'true',
                   getChildText(node, 'created') == 'true',
                   getChildText(node, 'createdDate'),
                   userInvitations or ())
