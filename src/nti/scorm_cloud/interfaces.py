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

        :param courseid: the unique identifier for the course
        :param path: the relative path to the zip file to import
        """

    def delete_course(courseid):
        """
        Deletes the specified course.

        :param courseid: the unique identifier for the course
        """

    def get_assets(courseid, path=None):
        """
        Downloads a file from a course by path. If no path is provided, all the
        course files will be downloaded contained in a zip file.

        :param courseid: the unique identifier for the course
        :param path: the path (relative to the course root) of the file to download.
            If not provided or is None, all course files will be downloaded.
        """

    def get_course_list(courseIdFilterRegex=None):
        """
        Retrieves a list of CourseData elements for all courses owned by the
        configured AppID that meet the specified filter criteria.

        :param courseIdFilterRegex: (optional) Regular expression to filter courses
            by ID
        :type courseIdFilterRegex: str
        """

    def get_preview_url(courseid, redirecturl, stylesheeturl=None):
        """
        Gets the URL that can be opened to preview the course without the need
        for a registration.

        Arguments:
        :param courseid: the unique identifier for the course
        :param redirecturl: the URL to which the browser should redirect upon course
            exit
        :param stylesheeturl: the URL for the CSS stylesheet to include
        :type redirecturl: str
        :type stylesheeturl: str
        """

    def get_metadata(courseid):
        """
        Gets the course metadata in XML format.

        :param courseid: the unique identifier for the course
        """

    def get_property_editor_url(courseid, stylesheetUrl=None,
                                notificationFrameUrl=None):
        """
        Gets the URL to view/edit the package properties for the course.
        Typically used within an IFRAME element.

        :param courseid: the unique identifier for the course
        :param stylesheeturl -- URL to a custom editor stylesheet
        :param notificationFrameUrl -- Tells the property editor to render a sub-iframe
            with this URL as the source. This can be used to simulate an 
            "onload" by using a notificationFrameUrl that is on the same domain 
            as the host system and calling parent.parent.method()
        :type stylesheeturl: str
        :type notificationFrameUrl: str
        """

    def get_attributes(courseid):
        """
        Retrieves the list of associated attributes for the course. 

        :param courseid: the unique identifier for the course
        :param versionid: the specific version of the course
        """

    def update_attributes(courseid, attributePairs):
        """
        Updates the specified attributes for the course.

        :param courseid: the unique identifier for the course
        :param attributePairs: the attribute name/value pairs to update
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

        :param regid: (optional) the unique identifier for the registration
        :param courseid: the unique identifier for the course
        :param userid: the unique identifier for the learner
        :param fname: the learner's first name
        :param lname: the learner's last name
        :param email: the learner's email address
        :type regid: str
        :type fname: str
        :type fname: str
        :type email: str
        :return: return unique identifier for the registration
        :rtype: email: str
        """

    def get_launch_url(regid, redirecturl, cssUrl=None, courseTags=None,
                       learnerTags=None, registrationTags=None):
        """
        Gets the URL to directly launch the course in a web browser.

        :param regid: the unique identifier for the registration
        :param redirecturl: the URL to which the SCORM player will redirect upon
            course exit
        :param cssUrl: the URL to a custom stylesheet
        :param courseTags -- comma-delimited list of tags to associate with the
            launched course
        :param learnerTags -- comma-delimited list of tags to associate with the
            learner launching the course
        :param registrationTags -- comma-delimited list of tags to associate with the
            launched registration
        :type regid: str
        :type redirecturl: str
        :type cssUrl: str
        :type courseTags: list of str
        :type learnerTags: list of str
        :type registrationTags: list of str
        """

    def get_registration_list(regIdFilterRegex=None,
                              courseIdFilterRegex=None):
        """
        Retrieves a list of registration associated with the configured AppID.
        Can optionally be filtered by registration or course ID.

        :param regIdFilterRegex: (optional) the regular expression used to filter the 
            list by registration ID
        :param courseIdFilterRegex: (optional) the regular expression used to filter
            the list by course ID
        :type regIdFilterRegex: str
        :type courseIdFilterRegex: str
        """

    def get_registration_result(regid, resultsformat):
        """
        Gets information about the specified registration.

        :param regid: the unique identifier for the registration
        :param resultsformat -- (optional) can be "course", "activity", or "full" to
            determine the level of detail returned. The default is "course"
        :type regid: str
        :type resultsformat: str
        """

    def get_launch_history(regid):
        """
        Retrieves a list of LaunchInfo objects describing each launch. These
        LaunchInfo objects do not contain the full launch history log; use
        get_launch_info to retrieve the full launch information.

        :param regid: the unique identifier for the registration
        :type regid: str
        """

    def reset_registration(regid):
        """
        Resets all status data for the specified registration, essentially
        restarting the course for the associated learner.

        :param regid: the unique identifier for the registration
        :type regid: str
        """

    def reset_global_objectives(regid):
        """
        Clears global objective data for the specified registration.

        :param regid: the unique identifier for the registration
        :type regid: str
        """

    def delete_registration(regid):
        """
        Deletes the specified registration.

        :param regid: the unique identifier for the registration
        :type regid: str
        """


class IInvitationService(interface.Interface):
    """
    Service that provides methods for interacting with the invitation service.
    """

    def create_invitation(courseid, publicInvitation=True, send=True, addresses=None,
                          emailSubject=None, emailBody=None, creatingUserEmail=None,
                          registrationCap=None, postbackUrl=None, authType=None, urlName=None,
                          urlPass=None, resultsFormat=None, async_=False):
        """
        Creates an invitation

        :param courseid: the course identifier
        :param publicInvitation: public invitation flag
        :param send: Send invitation flag
        :param addresses: the email address
        :param emailSubject: the email subject
        :param emailBody: the email body
        :param async_: the async flag
        :type courseid: str
        :type publicInvitation: bool
        :type send: bool
        :type addresses: str
        :type emailSubject: str
        :type async_: bool
        """

    def get_invitation_list(filter_=None, coursefilter=None):
        """
        Retrieves a list of invitations

        :param filter_: (optional) invitation filter
        :param coursefilter: (optional) the course filter
        """

    def get_invitation_status(invitationId):
        """
        Retrieves the status of an invitation

        :param invitationId: the invitation identifier
        """

    def get_invitation_info(invitationId, detail=None):
        """
        Retrieves the information associated with an invitation

        :param invitationId: the invitation identifier
        :param detail: the detail flag
        """

    def change_status(invitationId, enable, open_=None):
        """
        Change the status of an invitation

        :param invitationId: the invitation identifier
        :param enable: the enable invitation flag
        :param open_: the open invitation flag
        """


class IDateRangeSettings(interface.Interface):

    def get_url_encoding():
        """
        Returns the DateRangeSettings as encoded URL parameters to add to a
        Reportage widget URL.
        """


class ITagSettings(interface.Interface):

    def add(tagType, tagValue):
        """
        Add a tag

        :param tagType: the tag type
        :param tagValue: the tag value
        """

    def get_tag_str(tagType):
        """
        Return the tagType string

        :param tagType: the tag type
        """

    def get_view_tag_str(tagType):
        """
        Return the tagType view string

        :param tagType: the tag type
        """

    def get_url_encoding():
        """
        Return the TagSettings as encoded URL parameters
        """


class IWidgetSettings(interface.Interface):

    def get_url_encoding():
        """
        Returns the widget settings as encoded URL parameters to add to a 
        Reportage widget URL.
        """


class IReportingService(interface.Interface):
    """
    Service that provides methods for interacting with the Reportage service.
    """

    def get_reportage_date():
        """
        Gets the date/time, according to Reportage.
        """

    def get_reportage_auth(navperm, allowadmin):
        """
        Authenticates against the Reportage application, returning a session
        string used to make subsequent calls to launchReport.

        :param navperm: the Reportage navigation permissions to assign to the
            session. If "NONAV", the session will be prevented from navigating
            away from the original report/widget. "DOWNONLY" allows the user to
            drill down into additional detail. "FREENAV" allows the user full
            navigation privileges and the ability to change any reporting
            parameter.
        :param allowadmin: if True, the Reportage session will have admin privileges
        :type navperm: str
        :type allowadmin: bool
        """

    def get_report_url(auth, reportUrl):
        """
        Returns an authenticated URL that can launch a Reportage session at
        the specified Reportage entry point.

        :param auth: the Reportage authentication string, as retrieved from
            get_reportage_auth
        :param reportUrl -- the URL to the desired Reportage entry point
        :type reportUrl: str
        """

    def get_reportage_url(auth):
        """
        Returns the authenticated URL to the main Reportage entry point.

        :param auth: the Reportage authentication string, as retrieved from
            get_reportage_auth
        """

    def get_course_reportage_url(auth, courseid):
        """
        Returns the course reportage url

        :param auth: the Reportage authentication string, as retrieved from
            get_reportage_auth
        :param courseid: the course identifier
        """

    def get_widget_url(auth, widgettype, widgetSettings):
        """
        Gets the URL to a specific Reportage widget, using the provided
        widget settings.

        :param auth: the Reportage authentication string, as retrieved from
            get_reportage_auth
        :param widgettype: the widget type desired (for example, learnerSummary)
        :param widgetSettings: the :class:`IWidgetSettings` object for the widget type
        """
