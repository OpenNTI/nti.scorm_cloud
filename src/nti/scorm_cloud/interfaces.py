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


class ICourseService(interface.Interface):

    def import_uploaded_course(courseid, path):
        """
        Imports a SCORM PIF (zip file) from an existing zip file on the SCORM
        Cloud server.

        Arguments:
        courseid -- the unique identifier for the course
        path -- the relative path to the zip file to import
        """

    def delete_course(courseid):
        """
        Deletes the specified course.

        Arguments:
        courseid -- the unique identifier for the course
        """

    def get_assets(courseid, path=None):
        """
        Downloads a file from a course by path. If no path is provided, all the
        course files will be downloaded contained in a zip file.

        Arguments:
        courseid -- the unique identifier for the course
        path -- the path (relative to the course root) of the file to download.
            If not provided or is None, all course files will be downloaded.
        """

    def get_course_list(courseIdFilterRegex=None):
        """
        Retrieves a list of CourseData elements for all courses owned by the
        configured AppID that meet the specified filter criteria.

        Arguments:
        courseIdFilterRegex -- (optional) Regular expression to filter courses
            by ID
        """

    def get_preview_url(courseid, redirecturl, stylesheeturl=None):
        """
        Gets the URL that can be opened to preview the course without the need
        for a registration.

        Arguments:
        courseid -- the unique identifier for the course
        redirecturl -- the URL to which the browser should redirect upon course
            exit
        stylesheeturl -- the URL for the CSS stylesheet to include
        """

    def get_metadata(courseid):
        """
        Gets the course metadata in XML format.

        Arguments:
        courseid -- the unique identifier for the course
        """

    def get_property_editor_url(courseid, stylesheetUrl=None,
                                notificationFrameUrl=None):
        """
        Gets the URL to view/edit the package properties for the course.
        Typically used within an IFRAME element.

        Arguments:
        courseid -- the unique identifier for the course
        stylesheeturl -- URL to a custom editor stylesheet
        notificationFrameUrl -- Tells the property editor to render a sub-iframe
            with this URL as the source. This can be used to simulate an 
            "onload" by using a notificationFrameUrl that is on the same domain 
            as the host system and calling parent.parent.method()
        """

    def get_attributes(courseid):
        """
        Retrieves the list of associated attributes for the course. 

        Arguments:
        courseid -- the unique identifier for the course
        versionid -- the specific version of the course
        """

    def update_attributes(courseid, attributePairs):
        """
        Updates the specified attributes for the course.

        Arguments:
        courseid -- the unique identifier for the course
        attributePairs -- the attribute name/value pairs to update
        """
