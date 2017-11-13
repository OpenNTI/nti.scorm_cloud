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
        data = request.call_service('rustici.invitation.getInvitationList')
        return data
    get_invitation_list = getInvitationList

    def getInvitationStatus(self, invitationId):
        request = self.service.request()
        request.parameters['invitationId'] = invitationId
        data = request.call_service('rustici.invitation.getInvitationStatus')
        return data
    get_invitation_status = getInvitationStatus

    def getInvitationInfo(self, invitationId, detail=None):
        request = self.service.request()
        request.parameters['invitationId'] = invitationId
        if detail is not None:
            request.parameters['detail'] = detail
        data = request.call_service('rustici.invitation.getInvitationInfo')
        return data
    get_invitation_info = getInvitationInfo

    def changeStatus(self, invitationId, enable, open_=True, expirationdate=None):
        request = self.service.request()
        request.parameters['invitationId'] = invitationId
        request.parameters['enable'] = str(enable).lower()
        if open_ is not None:
            request.parameters['open'] = str(open_).lower()
        if expirationdate is not None:
            request.parameters['expirationdate'] = expirationdate
        data = request.call_service('rustici.invitation.changeStatus')
        return data
    change_status = changeStatus
