#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from zope import interface

from nti.scorm_cloud.client import CourseService
from nti.scorm_cloud.client import UploadService
from nti.scorm_cloud.client import ServiceRequest
from nti.scorm_cloud.client import ReportingService

from nti.scorm_cloud.client.config import Configuration

from nti.scorm_cloud.client.debug import DebugService

from nti.scorm_cloud.client.invitation import InvitationService

from nti.scorm_cloud.client.registration import RegistrationService

from nti.scorm_cloud.client.tag import TagService

from nti.scorm_cloud.interfaces import IScormCloudService

logger = __import__('logging').getLogger(__name__)


@interface.implementer(IScormCloudService)
class ScormCloudService(object):

    def __init__(self, configuration):
        self.config = configuration
        self.__handler_cache = {}

    @classmethod
    def withconfig(cls, config):
        """
        Named constructor that creates a ScormCloudService with the specified
        Configuration object.

        Arguments:
        config -- the Configuration object holding the required configuration
            values for the SCORM Cloud API
        """
        return cls(config)

    @classmethod
    def withargs(cls, appid, secret, serviceurl,
                 origin='rusticisoftware.pythonlibrary.2.0.0'):
        """
        Named constructor that creates a ScormCloudService with the specified
        configuration values.

        Arguments:
        appid -- the AppID for the application defined in the SCORM Cloud
            account
        secret -- the secret key for the application
        serviceurl -- the service URL for the SCORM Cloud web service. For
            example, http://cloud.scorm.com/EngineWebServices
        origin -- the origin string for the application software using the
            API/Python client library
        """
        return cls(Configuration(appid, secret, serviceurl, origin))

    def get_course_service(self):
        return CourseService(self)

    def get_tag_service(self):
        return TagService(self)

    def get_debug_service(self):
        return DebugService(self)

    def get_registration_service(self):
        return RegistrationService(self)

    def get_invitation_service(self):
        return InvitationService(self)

    def get_reporting_service(self):
        return ReportingService(self)

    def get_upload_service(self):
        return UploadService(self)

    def request(self):
        """
        Convenience method to create a new ServiceRequest.
        """
        return ServiceRequest(self)

    def make_call(self, method):
        """
        Convenience method to create and call a simple ServiceRequest (no
        parameters).
        """
        return self.request().call_service(method)
