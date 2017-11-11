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
    """
    Primary cloud service object that provides access to the more specific
    service areas, like the RegistrationService.
    """

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
    """
    Service that provides methods to manage and interact with courses on the
    SCORM Cloud. These methods correspond to the "rustici.course.*" web service
    methods.
    """

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


class IDebugService(interface.Interface):
    """
    Debugging and testing service that allows you to check the status of the
    SCORM Cloud and test your configuration settings.
    """

    def ping():
        """
        A simple ping that checks the connection to the SCORM Cloud.
        """

    def authping():
        """
        An authenticated ping that checks the connection to the SCORM Cloud
        and verifies the configured credentials.
        """


class IUploadService(interface.Interface):
    """
    Service that provides functionality to upload files to the SCORM Cloud.
    """

    def get_upload_token():
        """
        Retrieves an upload token which must be used to successfully upload a
        file.
        """

    def get_upload_url(callbackurl):
        """
        Returns a URL that can be used to upload a file via HTTP POST, through
        an HTML form element action, for example.
        """

    def delete_file(location):
        """
        Deletes the specified file.
        """


class IRegistrationService(interface.Interface):
    """
    Service that provides methods for managing and interacting with
    registrations on the SCORM Cloud. These methods correspond to the
    "rustici.registration.*" web service methods.
    """

    def create_registration(regid, courseid, userid, fname, lname,
                            email=None, learnerTags=None, courseTags=None, registrationTags=None):
        """
        Creates a new registration (an instance of a user taking a course).

        Arguments:
        regid -- the unique identifier for the registration
        courseid -- the unique identifier for the course
        userid -- the unique identifier for the learner
        fname -- the learner's first name
        lname -- the learner's last name
        email -- the learner's email address
        """

    def get_launch_url(regid, redirecturl, cssUrl=None, courseTags=None,
                       learnerTags=None, registrationTags=None):
        """
        Gets the URL to directly launch the course in a web browser.

        Arguments:
        regid -- the unique identifier for the registration
        redirecturl -- the URL to which the SCORM player will redirect upon
            course exit
        cssUrl -- the URL to a custom stylesheet
        courseTags -- comma-delimited list of tags to associate with the
            launched course
        learnerTags -- comma-delimited list of tags to associate with the
            learner launching the course
        registrationTags -- comma-delimited list of tags to associate with the
            launched registration
        """

    def get_registration_list(regIdFilterRegex=None,
                              courseIdFilterRegex=None):
        """
        Retrieves a list of registration associated with the configured AppID.
        Can optionally be filtered by registration or course ID.

        Arguments:
        regIdFilterRegex -- (optional) the regular expression used to filter the 
            list by registration ID
        courseIdFilterRegex -- (optional) the regular expression used to filter
            the list by course ID
        """

    def get_registration_result(regid, resultsformat):
        """
        Gets information about the specified registration.

        Arguments:
        regid -- the unique identifier for the registration
        resultsformat -- (optional) can be "course", "activity", or "full" to
            determine the level of detail returned. The default is "course"
        """

    def get_launch_history(regid):
        """
        Retrieves a list of LaunchInfo objects describing each launch. These
        LaunchInfo objects do not contain the full launch history log; use
        get_launch_info to retrieve the full launch information.

        Arguments:
        regid -- the unique identifier for the registration
        """

    def reset_registration(regid):
        """
        Resets all status data for the specified registration, essentially
        restarting the course for the associated learner.

        Arguments:
        regid -- the unique identifier for the registration
        """

    def reset_global_objectives(regid):
        """
        Clears global objective data for the specified registration.

        Arguments:
        regid -- the unique identifier for the registration
        """

    def delete_registration(regid):
        """
        Deletes the specified registration.

        Arguments:
        regid -- the unique identifier for the registration
        """
