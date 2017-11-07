#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from zope import interface


class IScormCloudService(interface.Interface):

    def get_course_service():
        """
        Retrieves the CourseService.
        """

    def get_debug_service():
        """
        Retrieves the DebugService.
        """

    def get_registration_service():
        """
        Retrieves the RegistrationService.
        """

    def get_invitation_service():
        """
        Retrieves the InvitationService.
        """

    def get_reporting_service():
        """
        Retrieves the ReportingService.
        """

    def get_upload_service():
        """
        Retrieves the UploadService.
        """
