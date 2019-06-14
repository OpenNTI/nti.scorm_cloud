#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# pylint: disable=inherit-non-class

from zope import interface

from zope.configuration.fields import Bool

from zope.schema import Object
from zope.schema import TextLine


class IScormCloudService(interface.Interface):
    """
    Primary cloud service object that provides access to the more specific
    service areas, like the RegistrationService.
    """

    def get_course_service():
        """
        Retrieves the CourseService.

        :return: return a new course service object
        :rtype: :class:`.ICourseService`
        """

    def get_tag_service():
        """
        Retrieves the TagService.

        :return: return a new tag service object
        :rtype: :class:`.ITagService`
        """

    def get_debug_service():
        """
        Retrieves the DebugService.

        :return: return a new debug service object
        :rtype: :class:`.IDebugService`
        """

    def get_registration_service():
        """
        Retrieves the RegistrationService.

        :return: return a new registration service object
        :rtype: :class:`.IRegistrationService`
        """

    def get_invitation_service():
        """
        Retrieves the InvitationService.

        :return: return a new invitation service object
        :rtype: :class:`.IInvitationService`
        """

    def get_reporting_service():
        """
        Retrieves the ReportingService.

        :return: return a new reporting service object
        :rtype: :class:`.IReportingService`
        """

    def get_upload_service():
        """
        Retrieves the UploadService.

        :return: return a new upload service object
        :rtype: :class:`.IUploadService`
        """


class IDebugService(interface.Interface):
    """
    Debugging and testing service that allows you to check the status of the
    SCORM Cloud and test your configuration settings.
    """

    service = Object(IScormCloudService,
                     title=u"The scorm cloud service")

    def ping():
        """
        A simple ping that checks the connection to the SCORM Cloud.
        """

    def authping():
        """
        An authenticated ping that checks the connection to the SCORM Cloud
        and verifies the configured credentials.
        """

    def gettime():
        """
        Returns the time on the running instance, in (UTC/GMT) timezone in the
        form ‘yyyyMMddHHmmss’. This format is used for the timestamp that is part of
        the security mechanism.
        """


class ITagService(interface.Interface):
    """
    Service that provides methods for managing and interacting with
    tags on the SCORM Cloud.

    The API allows tagging learners and registration, but that is not
    yet implemented.
    """

    service = Object(IScormCloudService,
                     title=u"The scorm cloud service")

    def get_scorm_tags(scorm_id):
        """
        Get tags for the given scorm_id

        :param scorm_id: the scorm_id to fetch tags for
        :return: an iterable of tags
        """

    def set_scorm_tags(scorm_id, tag_list_str):
        """
        Set tags for the given scorm_id

        :param scorm_id: the scorm_id to set tags on
        :param tag_list_str: A comma separated list of tags
        """

    def add_scorm_tag(scorm_id, tag):
        """
        Add a tag for the given scorm_id

        :param scorm_id: the scorm_id to add the tag
        :param tag: The new tag
        """

    def remove_scorm_tag(scorm_id, tag):
        """
        Remove a tag for the given scorm_id

        :param scorm_id: the scorm_id to remove the tag
        :param tag: The tag to remove
        """


class IRegistrationService(interface.Interface):
    """
    Service that provides methods for managing and interacting with
    registrations on the SCORM Cloud. These methods correspond to the
    "rustici.registration.*" web service methods.
    """

    service = Object(IScormCloudService,
                     title=u"The scorm cloud service")

    def createRegistration(courseid, regid, fname, lname, learnerid,
                           email=None, postbackurl=None, authtype=None, urlname=None,
                           urlpass=None, resultsformat=None):
        """
        Creates a new registration (an instance of a user taking a course).

        :param courseid: the course for which this registration is being created
        :param regid: (optional) the id used to identify this registration (it must be unique)
        :param fname: the first name of the learner associated with this registration
        :param lname: the last name of the learner associated with this registration
        :param learnerid: The learner id associated with this registration
        :param email: the learner's email address
        :param postbackurl: specifies a URL for which to post activity and status data in real time as the course is completed
        :param authtype: specify how to authorize against the given postbackurl, can be “form” or “httpbasic”
        :param urlname: an optional login name to be used for credentials when posting to the URL specified in postbackurl
        :param urlpass: credentials for the postbackurl
        :param resultsformat: level of detail in the information that is posted back while the course is being taken.
            It may be one of three values: “course” (course summary), “activity” (activity summary), or “full” (full detail)
        :type courseid: str
        :type regid: str
        :type fname: str
        :type fname: str
        :type email: str
        :type email: str
        :type postbackurl: str
        :type authtype: str
        :type urlname: str
        :type urlpass: str
        :type resultsformat: str
        :return: return unique identifier for the registration
        :rtype: str
        """

    def exists(regid):
        """
        check a whether or not the specified registration exist

        :param regid: the unique identifier for the registration
        :type regid: str
        :return: whether or not the specified registration exist
        :rtype: bool
        """

    def deleteRegistration(regid):
        """
        Deletes the specified registration.

        :param regid: the unique identifier for the registration
        :type regid: str
        """

    def resetRegistration(regid):
        """
        Resets all status data for the specified registration, essentially
        restarting the course for the associated learner.

        :param regid: the unique identifier for the registration
        :type regid: str
        """

    def getRegistrationList(courseid=None, learnerid=None, after=None, until=None):
        """
        Return a list of registrations associated with the given appid.

        :param courseid: limit search to only registrations for the course specified by this courseid
        :param learnerid: limit search to only registrations for the learner specified by this learnerid
        :param after: return registrations updated (strictly) after this timestamp.
        :param until: return registrations updated up to and including this timestamp.
        :type courseid: str
        :type learnerid: str
        :type after: str
        :type until: str
        """

    def getRegistrationDetail(regid):
        """
        Return detail for a registration

        :param regid: the registration id
        :type regid: str
        """

    def getRegistrationResult(regid, resultsformat=None, instanceid=None):
        """
        Gets information about the specified registration.

        :param regid: the unique identifier for the registration
        :param resultsformat: (optional) can be "course", "activity", or "full" to
            determine the level of detail returned. The default is "course"
        :param instanceid: the ID of a particular registration instance
        :type regid: str
        :type resultsformat: str
        :type instanceid: str
        """

    def launch(regid, redirecturl, cssUrl=None, courseTags=None,
               learnerTags=None, registrationTags=None, disableTracking=False, culture=None):
        """
        Gets the URL to directly launch the course in a web browser.

        :param regid: the unique identifier for the registration
        :param redirecturl: the URL to which the SCORM player will redirect upon
            course exit
        :param cssUrl: the URL to a custom stylesheet
        :param courseTags: comma-delimited list of tags to associate with the
            launched course
        :param learnerTags: comma-delimited list of tags to associate with the
            learner launching the course
        :param registrationTags: comma-delimited list of tags to associate with the
            launched registration
        :param disableTracking: if set to True the registration will be launched with tracking disabled,
            and the launch will not result in any changes to the registration
        :param culture: culture code
        :type regid: str
        :type redirecturl: str
        :type cssUrl: str
        :type courseTags: list of str
        :type learnerTags: list of str
        :type disableTracking: bool
        :type disableTracking: code
        :type registrationTags: list of str
        """

    def getLaunchHistory(regid):
        """
        Retrieves a list of LaunchInfo objects describing each launch. These
        LaunchInfo objects do not contain the full launch history log; use
        get_launch_info to retrieve the full launch information.

        :param regid: the unique identifier for the registration
        :type regid: str
        """

    def getLaunchInfo(launchid):
        """
        Fetch detailed historical data for the specified launch

        :param launchid: the launch identifier
        :type launchid: str
        """

    def resetGlobalObjectives(regid):
        """
        Clears global objective data for the specified registration.

        :param regid: the unique identifier for the registration
        :type regid: str
        """

    def updateLearnerInfo(learnerid, fname, lname, newid=None, email=None):
        """
        Update the learner information that was given during previous createRegistration calls.

        :param learnerid: The id of the learner whose info is being updated
        :param fname: the first name of the learner
        :param lname: the last name of the learner
        :param newid: the new id to assign to this learner
        :param email: the email of the learner

        :type learnerid: str
        :type fname: str
        :type fname: str
        :type newid: str
        :type email: str
        """

    def getPostbackInfo(regid):
        """
        Provides a way to retrieve the postback attributes

        :param regid: the unique identifier for the registration
        :type regid: str
        """

    def updatePostbackInfo(regid, url, name=None, password=None, authtype=None, resultsformat=None):
        """
        Provides a way to update the postback settings for a registration

        :param regid: the unique identifier for the registration
        :param url: URL for registration results to be posted to
        :param name: auth name for the postback.
        :param password: credentials for the postbackurl
        :param authtype: type of authentication used
        :param resultsformat: level of detail in the information that is posted back
            while the course is being taken
        :type regid: str
        :type url: str
        :type name: str
        :type password: str
        :type authtype: str
        :type resultsformat: str
        """

    def deletePostbackInfo(regid):
        """
        Clear postback settings so that registration results no longer invoke a postback url.

        :param regid: the unique identifier for the registration
        :type regid: str
        """


class IInvitationService(interface.Interface):
    """
    Service that provides methods for interacting with the invitation service.
    """

    service = Object(IScormCloudService,
                     title=u"The scorm cloud service")

    def createInvitation(courseid, public=True, send=True, addresses=None,
                         emailSubject=None, emailBody=None, creatingUserEmail=None,
                         registrationCap=None, postbackurl=None, authtype=None, urlname=None,
                         urlpass=None, resultsformat=None, expirationdate=None):
        """
        Creates a new invitation in your SCORM Cloud account, customized with the given parameters,
        and will return the id for the newly created invitation.

        :param courseid: the course to which this invitation is being created
        :param public: whether the invitation is public or private
        :param send: whether the private invitations will be emailed to the provided addresses or not.
        :param addresses: a comma separated list of email addresse
        :param emailSubject: the subject of the email
        :param emailBody: the test that will be sent in the body
        :param creatingUserEmail: the email of the user who is creating the invitation.
        :param registrationCap: limit of public invitation registrations to allow
        :param postbackurl: specifies a URL for which to post activity and status data in real time as the course is completed
        :param authtype: specify how to authorize against the given postbackurl, can be “form” or “httpbasic”
        :param urlname: an optional login name to be used for credentials when posting to the URL specified in postbackurl
        :param urlpass: credentials for the postbackurl
        :param resultsformat: level of detail in the information that is posted back while the course is being taken.
            It may be one of three values: “course” (course summary), “activity” (activity summary), or “full” (full detail)
        :param expirationdate: the date this invitation will expire (formatted yyyyMMddHHmmss in UTC time)
        :type courseid: str
        :type public: bool
        :type send: bool
        :type addresses: str
        :type emailSubject: str
        :type emailBody: str
        :type registrationCap: int
        :type postbackurl: str
        :type authtype: str
        :type urlname: str
        :type urlpass: str
        :type resultsformat: str
        :type expirationdate: str
        """

    def createInvitationAsync(courseid, public=True, send=True, addresses=None,
                              emailSubject=None, emailBody=None, creatingUserEmail=None,
                              registrationCap=None, postbackurl=None, authtype=None, urlname=None,
                              urlpass=None, resultsformat=None, expirationdate=None):
        """
        Creates a new invitation in your SCORM Cloud account, customized with the given parameters,
        and will return the id for the newly created invitation. The method will still return the invitation Id,
        but the job of creating the registrations and sending the invitation email may not yet be complete.

        :param courseid: the course to which this invitation is being created
        :param public: whether the invitation is public or private
        :param send: whether the private invitations will be emailed to the provided addresses or not.
        :param addresses: a comma separated list of email addresse
        :param emailSubject: the subject of the email
        :param emailBody: the test that will be sent in the body
        :param creatingUserEmail: the email of the user who is creating the invitation.
        :param registrationCap: limit of public invitation registrations to allow
        :param postbackurl: specifies a URL for which to post activity and status data in real time as the course is completed
        :param authtype: specify how to authorize against the given postbackurl, can be “form” or “httpbasic”
        :param urlname: an optional login name to be used for credentials when posting to the URL specified in postbackurl
        :param urlpass: credentials for the postbackurl
        :param resultsformat: level of detail in the information that is posted back while the course is being taken.
            It may be one of three values: “course” (course summary), “activity” (activity summary), or “full” (full detail)
        :param expirationdate: the date this invitation will expire (formatted yyyyMMddHHmmss in UTC time)
        :type courseid: str
        :type public: bool
        :type send: bool
        :type addresses: str
        :type emailSubject: str
        :type emailBody: str
        :type registrationCap: int
        :type postbackurl: str
        :type authtype: str
        :type urlname: str
        :type urlpass: str
        :type resultsformat: str
        :type expirationdate: str
        """

    def getInvitationStatus(invitationId):
        """
        Retrieves the status of an invitation

        :param invitationId: the invitation identifier
        """

    def getInvitationInfo(invitationId, detail=True):
        """
        Retrieves the information associated with an invitation

        :param invitationId: the invitation identifier
        :param detail: whether to return registration summary info
        :type invitationId: str
        :type detail: bool
        """

    def getInvitationList(filter_=None, coursefilter=None):
        """
        Retrieves a list of invitations

        :param filter_: a regular expression that will be used to filter the list of invitations
        :param coursefilter: A regular express that will be used to filter the list of invitations.
            Specifically only those invitations that are associated with courses whose courseid’s match
            the given expression will be returned in the list
        :type filter_: str
        :type coursefilter: str
        """

    def changeStatus(invitationId, enable, open_=True, expirationdate=None):
        """
        Change the status of an invitation

        :param invitationId: the invitation identifier
        :param enable: whether to set the invitation to enabled (launchable) or not.
        :param open_:  whether a public invitation is still available for learner’s to
            create new registrations.
        :param expirationdate: the date this invitation will expire and can not be launched
        :type invitationId: str
        :type enable: bool
        :type open_: bool
        :type expirationdate: str
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

    def update_assets(courseid, path):
        """
        This method can be used to update the assets of the course specified.
        Files found in the zip file, which is sent through the request or
        specified by the optional path parameter, will be overlayed on top of
        the files belonging to the course specifed by courseid.
        Note however that the existing manifest file will not be overwritten.

        :param courseid: The ID used to identify the course to update.
        :param path: The file or path to the file used for the update.
        """

    def update_attributes(courseid, attributePairs):
        """
        Updates the specified attributes for the course.

        :param courseid: the unique identifier for the course
        :param attributePairs: the attribute name/value pairs to update
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

    tagSettings = Object(ITagSettings,
                         title=u"Tag settings",
                         required=False)

    dateRangeSettings = Object(ITagSettings, title=u"Tag settings",
                               required=False)

    courseId = TextLine(title=u"The course identifier", required=False)
    learnerId = TextLine(title=u"The learner identifier", required=False)

    showTitle = Bool(title=u"Show title flag", default=True)
    vertical = Bool(title=u"Show vertical flag", default=False)
    public = Bool(title=u"Public flag", default=True)
    standalone = Bool(title=u"Standalone flag", default=True)
    iframe = Bool(title=u"iframe flag", default=False)
    expand = Bool(title=u"Expand flag", default=True)
    scriptBased = Bool(title=u"Script based flag", default=True)

    divname = TextLine(title=u"Div name", default=u'')

    embedded = Bool(title=u"Embedded flag", default=True)
    viewall = Bool(title=u"View all flag", default=True)
    export = Bool(title=u"Export flag", default=True)

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

    def get_account_info():
        """
        Returns information about the account this service is tied to
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


class IUnmarshalled(interface.Interface):

    _node = interface.Attribute('Minidom node object')

    def fromMinidom(node):
        """
        Construct an instance of this object using the minidom source node

        :param node: Minodom node
        :return: A new instance of the implementer object
        """
