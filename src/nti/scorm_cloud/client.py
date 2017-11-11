#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import re
import uuid
import datetime
from hashlib import md5
from xml.dom import minidom

from six import text_type
from six.moves.urllib_parse import quote_plus

try:
    from urllib2 import urlopen
except ImportError:  # pragma: no cover
    from urllib.request import urlopen

from zope import interface

from nti.scorm_cloud.compat import native_

from nti.scorm_cloud.interfaces import IDebugService
from nti.scorm_cloud.interfaces import ICourseService
from nti.scorm_cloud.interfaces import IUploadService
from nti.scorm_cloud.interfaces import IScormCloudService
from nti.scorm_cloud.interfaces import IRegistrationService

logger = __import__('logging').getLogger(__name__)


def make_utf8(dictionary):
    """
    Encodes all Unicode strings in the dictionary to UTF-8. Converts
    all other objects to regular strings.

    Returns a copy of the dictionary, doesn't touch the original.
    """
    result = {}
    for key, value in dictionary.items():
        if isinstance(value, text_type):
            value = native_(value, 'utf-8')
        else:
            value = str(value)
        result[key] = value
    return result


class Configuration(object):
    """
    Stores the configuration elements required by the API.
    """

    def __init__(self, appid, secret, serviceurl,
                 origin='rusticisoftware.pythonlibrary.2.0.0'):
        self.appid = appid
        self.secret = secret
        self.origin = origin
        self.serviceurl = serviceurl

    def __repr__(self):
        return 'Configuration for AppID %s from origin %s' % (self.appid, self.origin)


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


@interface.implementer(IDebugService)
class DebugService(object):

    def __init__(self, service):
        self.service = service

    def ping(self):
        try:
            xmldoc = self.service.make_call('rustici.debug.ping')
            return xmldoc.documentElement.attributes['stat'].value == 'ok'
        except Exception:
            return False

    def authping(self):
        try:
            xmldoc = self.service.make_call('rustici.debug.authPing')
            return xmldoc.documentElement.attributes['stat'].value == 'ok'
        except Exception:
            return False


@interface.implementer(IUploadService)
class UploadService(object):

    def __init__(self, service):
        self.service = service

    def get_upload_token(self):
        server = None
        xmldoc = self.service.make_call('rustici.upload.getUploadToken')
        serverNodes = xmldoc.getElementsByTagName('server')
        for s in serverNodes or ():
            server = s.childNodes[0].nodeValue

        tokenid = None
        tokenidNodes = xmldoc.getElementsByTagName('id')
        for t in tokenidNodes or ():
            tokenid = t.childNodes[0].nodeValue
        if server and tokenid:
            token = UploadToken(server, tokenid)
            return token
        else:
            return None

    def get_upload_url(self, callbackurl):
        token = self.get_upload_token()
        if token:
            request = self.service.request()
            request.parameters['tokenid'] = token.tokenid
            request.parameters['redirecturl'] = callbackurl
            return request.construct_url('rustici.upload.uploadFile')
        else:
            return None

    def delete_file(self, location):
        locParts = location.split("/")
        request = self.service.request()
        request.parameters['file'] = locParts[len(locParts) - 1]
        return request.call_service('rustici.upload.deleteFiles')


@interface.implementer(ICourseService)
class CourseService(object):

    def __init__(self, service):
        self.service = service

    def import_uploaded_course(self, courseid, path):
        request = self.service.request()
        request.parameters['courseid'] = courseid
        request.parameters['path'] = path
        result = request.call_service('rustici.course.importCourse')
        ir = ImportResult.list_from_result(result)
        return ir

    def delete_course(self, courseid):
        request = self.service.request()
        request.parameters['courseid'] = courseid
        return request.call_service('rustici.course.deleteCourse')

    def get_assets(self, courseid, path=None):
        request = self.service.request()
        request.parameters['courseid'] = courseid
        if (path is not None):
            request.parameters['path'] = path
        return request.call_service('rustici.course.getAssets')

    def get_course_list(self, courseIdFilterRegex=None):
        request = self.service.request()
        if courseIdFilterRegex is not None:
            request.parameters['filter'] = courseIdFilterRegex
        result = request.call_service('rustici.course.getCourseList')
        courses = CourseData.list_from_result(result)
        return courses

    def get_preview_url(self, courseid, redirecturl, stylesheeturl=None):
        request = self.service.request()
        request.parameters['courseid'] = courseid
        request.parameters['redirecturl'] = redirecturl
        if stylesheeturl is not None:
            request.parameters['stylesheet'] = stylesheeturl
        url = request.construct_url('rustici.course.preview')
        logger.info('preview link: ' + url)
        return url

    def get_metadata(self, courseid):
        request = self.service.request()
        request.parameters['courseid'] = courseid
        return request.call_service('rustici.course.getMetadata')

    def get_property_editor_url(self, courseid, stylesheetUrl=None,
                                notificationFrameUrl=None):
        request = self.service.request()
        request.parameters['courseid'] = courseid
        if stylesheetUrl is not None:
            request.parameters['stylesheet'] = stylesheetUrl
        if notificationFrameUrl is not None:
            request.parameters['notificationframesrc'] = notificationFrameUrl

        url = request.construct_url('rustici.course.properties')
        logger.info('properties link: ' + url)
        return url

    def get_attributes(self, courseid):
        request = self.service.request()
        request.parameters['courseid'] = courseid
        xmldoc = request.call_service('rustici.course.getAttributes')

        atts = {}
        attrNodes = xmldoc.getElementsByTagName('attribute')
        for an in attrNodes:
            atts[an.attributes['name'].value] = an.attributes['value'].value
        return atts

    def update_attributes(self, courseid, attributePairs):
        request = self.service.request()
        request.parameters['courseid'] = courseid
        for (key, value) in attributePairs.iteritems():
            request.parameters[key] = value
        xmldoc = request.call_service('rustici.course.updateAttributes')

        attrNodes = xmldoc.getElementsByTagName('attribute')
        atts = {}
        for an in attrNodes:
            atts[an.attributes['name'].value] = an.attributes['value'].value
        return atts


@interface.implementer(IRegistrationService)
class RegistrationService(object):

    def __init__(self, service):
        self.service = service

    def create_registration(self, regid, courseid, userid, fname, lname,
                            email=None, learnerTags=None, courseTags=None,
                            registrationTags=None):
        if regid is None:
            regid = str(uuid.uuid1())
        request = self.service.request()
        request.parameters['appid'] = self.service.config.appid
        request.parameters['courseid'] = courseid
        request.parameters['regid'] = regid
        request.parameters['fname'] = fname
        request.parameters['lname'] = lname
        request.parameters['learnerid'] = userid
        if email is not None:
            request.parameters['email'] = email
        if learnerTags is not None:
            request.parameters['learnerTags'] = learnerTags
        if courseTags is not None:
            request.parameters['courseTags'] = courseTags
        if registrationTags is not None:
            request.parameters['registrationTags'] = registrationTags
        xmldoc = request.call_service('rustici.registration.createRegistration')
        successNodes = xmldoc.getElementsByTagName('success')
        if successNodes.length == 0:
            raise ScormCloudError("Create Registration failed.  " +
                                  xmldoc.err.attributes['msg'])
        return regid

    def get_launch_url(self, regid, redirecturl, cssUrl=None, courseTags=None,
                       learnerTags=None, registrationTags=None):
        request = self.service.request()
        request.parameters['regid'] = regid
        request.parameters['redirecturl'] = redirecturl + '?regid=' + regid
        if cssUrl is not None:
            request.parameters['cssurl'] = cssUrl
        if courseTags is not None:
            request.parameters['coursetags'] = courseTags
        if learnerTags is not None:
            request.parameters['learnertags'] = learnerTags
        if registrationTags is not None:
            request.parameters['registrationTags'] = registrationTags
        url = request.construct_url('rustici.registration.launch')
        return url

    def get_registration_list(self, regIdFilterRegex=None, courseIdFilterRegex=None):
        request = self.service.request()
        if regIdFilterRegex is not None:
            request.parameters['filter'] = regIdFilterRegex
        if courseIdFilterRegex is not None:
            request.parameters['coursefilter'] = courseIdFilterRegex

        result = request.call_service('rustici.registration.getRegistrationList')
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


class InvitationService(object):

    def __init__(self, service):
        self.service = service

    def create_invitation(self, courseid, publicInvitation='true', send='true', addresses=None,
                          emailSubject=None, emailBody=None, creatingUserEmail=None,
                          registrationCap=None, postbackUrl=None, authType=None, urlName=None,
                          urlPass=None, resultsFormat=None, async=False):
        request = self.service.request()

        request.parameters['courseid'] = courseid
        request.parameters['send'] = send
        request.parameters['public'] = publicInvitation

        if addresses is not None:
            request.parameters['addresses'] = addresses
        if emailSubject is not None:
            request.parameters['emailSubject'] = emailSubject
        if emailBody is not None:
            request.parameters['emailBody'] = emailBody
        if creatingUserEmail is not None:
            request.parameters['creatingUserEmail'] = creatingUserEmail
        if registrationCap is not None:
            request.parameters['registrationCap'] = registrationCap
        if postbackUrl is not None:
            request.parameters['postbackUrl'] = postbackUrl
        if authType is not None:
            request.parameters['authType'] = authType
        if urlName is not None:
            request.parameters['urlName'] = urlName
        if urlPass is not None:
            request.parameters['urlPass'] = urlPass
        if resultsFormat is not None:
            request.parameters['resultsFormat'] = resultsFormat

        if async:
            data = request.call_service('rustici.invitation.createInvitationAsync')
        else:
            data = request.call_service('rustici.invitation.createInvitation')

        return data

    def get_invitation_list(self, filter_=None, coursefilter=None):
        request = self.service.request()
        if filter_ is not None:
            request.parameters['filter'] = filter_
        if coursefilter is not None:
            request.parameters['coursefilter'] = coursefilter
        data = request.call_service('rustici.invitation.getInvitationList')
        return data

    def get_invitation_status(self, invitationId):
        request = self.service.request()
        request.parameters['invitationId'] = invitationId
        data = request.call_service('rustici.invitation.getInvitationStatus')
        return data

    def get_invitation_info(self, invitationId, detail=None):
        request = self.service.request()
        request.parameters['invitationId'] = invitationId
        if detail is not None:
            request.parameters['detail'] = detail
        data = request.call_service('rustici.invitation.getInvitationInfo')
        return data

    def change_status(self, invitationId, enable, open_=None):
        request = self.service.request()
        request.parameters['invitationId'] = invitationId
        request.parameters['enable'] = enable
        if open_ is not None:
            request.parameters['open'] = open_
        data = request.call_service('rustici.invitation.changeStatus')
        return data


class ReportingService(object):
    """
    Service that provides methods for interacting with the Reportage service.
    """

    def __init__(self, service):
        self.service = service

    def get_reportage_date(self):
        """
        Gets the date/time, according to Reportage.
        """
        reportUrl = (
            self._get_reportage_service_url() +
            'Reportage/scormreports/api/getReportDate.php?appId=' +
            self.service.config.appid
        )
        cloudsocket = urlopen(reportUrl, None)
        reply = cloudsocket.read()
        cloudsocket.close()
        d = datetime.datetime
        return d.strptime(reply, "%Y-%m-%d %H:%M:%S")

    def get_reportage_auth(self, navperm, allowadmin):
        """
        Authenticates against the Reportage application, returning a session
        string used to make subsequent calls to launchReport.

        Arguments:
        navperm -- the Reportage navigation permissions to assign to the
            session. If "NONAV", the session will be prevented from navigating
            away from the original report/widget. "DOWNONLY" allows the user to
            drill down into additional detail. "FREENAV" allows the user full
            navigation privileges and the ability to change any reporting
            parameter.
        allowadmin -- if True, the Reportage session will have admin privileges
        """
        request = self.service.request()
        request.parameters['navpermission'] = navperm
        request.parameters['admin'] = 'true' if allowadmin else 'false'
        xmldoc = request.call_service('rustici.reporting.getReportageAuth')
        token = xmldoc.getElementsByTagName('auth')
        if token.length > 0:
            return token[0].childNodes[0].nodeValue
        else:
            return None

    def _get_reportage_service_url(self):
        """
        Returns the base Reportage URL.
        """
        return self.service.config.serviceurl.replace('EngineWebServices', '')

    def _get_base_reportage_url(self):
        return (self._get_reportage_service_url() + 'Reportage/reportage.php' +
                '?appId=' + self.service.config.appid)

    def get_report_url(self, auth, reportUrl):
        """
        Returns an authenticated URL that can launch a Reportage session at
        the specified Reportage entry point.

        Arguments:
        auth -- the Reportage authentication string, as retrieved from
            get_reportage_auth
        reportUrl -- the URL to the desired Reportage entry point
        """
        request = self.service.request()
        request.parameters['auth'] = auth
        request.parameters['reporturl'] = reportUrl
        url = request.construct_url('rustici.reporting.launchReport')
        return url

    def get_reportage_url(self, auth):
        """
        Returns the authenticated URL to the main Reportage entry point.

        Arguments:
        auth -- the Reportage authentication string, as retrieved from
            get_reportage_auth
        """
        reporturl = self._get_base_reportage_url()
        return self.get_report_url(auth, reporturl)

    def get_course_reportage_url(self, auth, courseid):
        reporturl = self._get_base_reportage_url() + '&courseid=' + courseid
        return self.get_report_url(auth, reporturl)

    def get_widget_url(self, auth, widgettype, widgetSettings):
        """
        Gets the URL to a specific Reportage widget, using the provided
        widget settings.

        Arguments:
        auth -- the Reportage authentication string, as retrieved from
            get_reportage_auth
        widgettype -- the widget type desired (for example, learnerSummary)
        widgetSettings -- the WidgetSettings object for the widget type
        """
        reportUrl = (self._get_reportage_service_url() +
                     'Reportage/scormreports/widgets/')
        widgetUrlTypeLib = {
            'allSummary': 'summary/SummaryWidget.php?srt=allLearnersAllCourses',
            'courseSummary': 'summary/SummaryWidget.php?srt=singleCourse',
            'learnerSummary': 'summary/SummaryWidget.php?srt=singleLearner',
            'learnerCourse': 'summary/SummaryWidget.php?srt='
            'singleLearnerSingleCourse',
            'courseActivities': 'DetailsWidget.php?drt=courseActivities',
            'learnerRegistration': 'DetailsWidget.php?drt=learnerRegistration',
            'courseComments': 'DetailsWidget.php?drt=courseComments',
            'learnerComments': 'DetailsWidget.php?drt=learnerComments',
            'courseInteractions': 'DetailsWidget.php?drt=courseInteractions',
            'learnerInteractions': 'DetailsWidget.php?drt=learnerInteractions',
            'learnerActivities': 'DetailsWidget.php?drt=learnerActivities',
            'courseRegistration': 'DetailsWidget.php?drt=courseRegistration',
            'learnerRegistration': 'DetailsWidget.php?drt=learnerRegistration',
            'learnerCourseActivities': 'DetailsWidget.php?drt='
            'learnerCourseActivities',
            'learnerTranscript': 'DetailsWidget.php?drt=learnerTranscript',
            'learnerCourseInteractions': 'DetailsWidget.php?drt='
            'learnerCourseInteractions',
            'learnerCourseComments': 'DetailsWidget.php?drt='
            'learnerCourseComments',
            'allLearners': 'ViewAllDetailsWidget.php?viewall=learners',
            'allCourses': 'ViewAllDetailsWidget.php?viewall=courses'
        }
        reportUrl += widgetUrlTypeLib[widgettype]
        reportUrl += '&appId=' + self.service.config.appid
        reportUrl += widgetSettings.get_url_encoding()
        reportUrl = self.get_report_url(auth, reportUrl)
        return reportUrl


class WidgetSettings(object):

    def __init__(self, dateRangeSettings, tagSettings):
        self.dateRangeSettings = dateRangeSettings
        self.tagSettings = tagSettings

        self.courseId = None
        self.learnerId = None

        self.showTitle = True
        self.vertical = False
        self.public = True
        self.standalone = True
        self.iframe = False
        self.expand = True
        self.scriptBased = True
        self.divname = ''
        self.embedded = True
        self.viewall = True
        self.export = True

    def get_url_encoding(self):
        """
        Returns the widget settings as encoded URL parameters to add to a 
        Reportage widget URL.
        """
        widgetUrlStr = ''
        if self.courseId is not None:
            widgetUrlStr += '&courseId=' + self.courseId
        if self.learnerId is not None:
            widgetUrlStr += '&learnerId=' + self.learnerId

        widgetUrlStr += '&showTitle=' + 'self.showTitle'.lower()
        widgetUrlStr += '&standalone=' + 'self.standalone'.lower()
        if self.iframe:
            widgetUrlStr += '&iframe=true'
        widgetUrlStr += '&expand=' + 'self.expand'.lower()
        widgetUrlStr += '&scriptBased=' + 'self.scriptBased'.lower()
        widgetUrlStr += '&divname=' + self.divname
        widgetUrlStr += '&vertical=' + 'self.vertical'.lower()
        widgetUrlStr += '&embedded=' + 'self.embedded'.lower()

        if self.dateRangeSettings is not None:
            widgetUrlStr += self.dateRangeSettings.get_url_encoding()

        if self.tagSettings is not None:
            widgetUrlStr += self.tagSettings.get_url_encoding()

        return widgetUrlStr


class DateRangeSettings(object):
    def __init__(self, dateRangeType, dateRangeStart,
                 dateRangeEnd, dateCriteria):
        self.dateRangeType = dateRangeType
        self.dateRangeStart = dateRangeStart
        self.dateRangeEnd = dateRangeEnd
        self.dateCriteria = dateCriteria

    def get_url_encoding(self):
        """
        Returns the DateRangeSettings as encoded URL parameters to add to a
        Reportage widget URL.
        """
        dateRangeStr = ''
        if self.dateRangeType == 'selection':
            dateRangeStr += '&dateRangeType=c'
            dateRangeStr += '&dateRangeStart=' + self.dateRangeStart
            dateRangeStr += '&dateRangeEnd=' + self.dateRangeEnd
        else:
            dateRangeStr += '&dateRangeType=' + self.dateRangeType

        dateRangeStr += '&dateCriteria=' + self.dateCriteria
        return dateRangeStr


class TagSettings(object):
    def __init__(self):
        self.tags = {'course': [], 'learner': [], 'registration': []}

    def add(self, tagType, tagValue):
        self.tags[tagType].append(tagValue)

    def get_tag_str(self, tagType):
        return ','.join(set(self.tags[tagType])) + "|_all"

    def get_view_tag_str(self, tagType):
        return ','.join(set(self.tags[tagType]))

    def get_url_encoding(self):
        tagUrlStr = ''
        for k in self.tags.keys():
            if len(set(self.tags[k])) > 0:
                tagUrlStr += '&' + k + 'Tags=' + self.get_tag_str(k)
                tagUrlStr += ('&view' + k.capitalize() + 'TagGroups=' +
                              self.get_view_tag_str(k))
        return tagUrlStr


class ScormCloudError(Exception):
    def __init__(self, msg, json=None):
        self.msg = msg
        self.json = json

    def __str__(self):
        return repr(self.msg)


class ImportResult(object):
    title = ""
    message = ""
    parserWarnings = []
    wasSuccessful = False

    def __init__(self, importResultElement):
        if importResultElement is not None:
            self.wasSuccessful = (importResultElement.attributes['successful'].value == 'true')
            self.title = (importResultElement.getElementsByTagName("title")[0]
                          .childNodes[0].nodeValue)
            self.message = (importResultElement
                            .getElementsByTagName("message")[0]
                            .childNodes[0].nodeValue)
            xmlpw = importResultElement.getElementsByTagName("warning")
            for pw in xmlpw:
                self.parserWarnings.append(pw.childNodes[0].nodeValue)

    @classmethod
    def list_from_result(cls, xmldoc):
        """
        Returns a list of ImportResult objects by parsing the raw result of an
        API method that returns importresult elements.

        Arguments:
        data -- the raw result of the API method
        """
        allResults = []
        importresults = xmldoc.getElementsByTagName("importresult")
        for ir in importresults:
            allResults.append(cls(ir))
        return allResults


class CourseData(object):
    title = ""
    courseId = ""
    numberOfVersions = 1
    numberOfRegistrations = 0

    def __init__(self, courseDataElement):
        if courseDataElement is not None:
            attributes = courseDataElement.attributes
            self.courseId = attributes['id'].value
            self.title = attributes['title'].value
            self.numberOfVersions = attributes['versions'].value
            self.numberOfRegistrations = attributes['registrations'].value

    @classmethod
    def list_from_result(cls, xmldoc):
        """
        Returns a list of CourseData objects by parsing the raw result of an
        API method that returns course elements.

        Arguments:
        data -- the raw result of the API method
        """
        allResults = []
        courses = xmldoc.getElementsByTagName("course")
        for course in courses:
            allResults.append(cls(course))
        return allResults


class UploadToken(object):

    server = ""
    tokenid = ""

    def __init__(self, server, tokenid):
        self.server = server
        self.tokenid = tokenid


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


class ServiceRequest(object):
    """
    Helper object that handles the details of web service URLs and parameter
    encoding and signing. Set the web service method parameters on the 
    parameters attribute of the ServiceRequest object and then call
    call_service with the method name to make a service request.
    """

    def __init__(self, service):
        self.service = service
        self.parameters = dict()
        self.file_ = None

    def call_service(self, method, serviceurl=None):
        """
        Calls the specified web service method using any parameters set on the
        ServiceRequest.

        Arguments:
        method -- the full name of the web service method to call.
            For example: rustici.registration.createRegistration
        serviceurl -- (optional) used to override the service host URL for a
            single call
        """
        postparams = None
        # if self.file_ is not None:
        # TODO: Implement file upload
        url = self.construct_url(method, serviceurl)
        rawresponse = self.send_post(url, postparams)
        response = self.get_xml(rawresponse)
        return response

    def construct_url(self, method, serviceurl=None):
        """
        Gets the full URL for a Cloud web service call, including parameters.

        Arguments:
        method -- the full name of the web service method to call.
            For example: rustici.registration.createRegistration
        serviceurl -- (optional) used to override the service host URL for a
            single call
        """
        params = {'method': method}

        # 'appid': self.service.config.appid,
        # 'origin': self.service.config.origin,
        # 'ts': datetime.datetime.utcnow().strftime('yyyyMMddHHmmss'),
        # 'applib': 'python'}
        for k, v in self.parameters.iteritems():
            params[k] = v
        url = self.service.config.serviceurl
        if serviceurl is not None:
            url = serviceurl
        url = (
            ScormCloudUtilities.clean_cloud_host_url(url) + '?' + self._encode_and_sign(params)
        )
        return url

    def get_xml(self, raw):
        """
        Parses the raw response string as XML and asserts that there was no
        error in the result.

        Arguments:
        raw -- the raw response string from an API method call
        """
        xmldoc = minidom.parseString(raw)
        rsp = xmldoc.documentElement
        if rsp.attributes['stat'].value != 'ok':
            err = rsp.firstChild
            raise Exception('SCORM Cloud Error: %s - %s' %
                            (err.attributes['code'].value,
                             err.attributes['msg'].value))
        return xmldoc

    def send_post(self, url, postparams):
        cloudsocket = urlopen(url, postparams)
        reply = cloudsocket.read()
        cloudsocket.close()
        return reply

    def _encode_and_sign(self, dictionary):
        """
        URL encodes the data in the dictionary, and signs it using the
        given secret, if a secret was given.

        Arguments:
        dictionary -- the dictionary containing the key/value parameter pairs
        """
        dictionary['appid'] = self.service.config.appid
        dictionary['origin'] = self.service.config.origin
        dictionary['ts'] = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
        dictionary['applib'] = "python"
        dictionary = make_utf8(dictionary)
        signing = ''
        values = list()
        secret = self.service.config.secret
        for key in sorted(dictionary.keys(), key=str.lower):
            signing += key + dictionary[key]
            values.append(key + '=' + quote_plus(dictionary[key]))
        values.append('sig=' + md5(secret + signing).hexdigest())
        return '&'.join(values)


class ScormCloudUtilities(object):
    """
    Provides utility functions for working with the SCORM Cloud.
    """

    @staticmethod
    def get_canonical_origin_string(organization, application, version):
        """
        Helper function to build a proper origin string to provide to the
        SCORM Cloud configuration. Takes the organization name, application
        name, and application version.

        Arguments:
        organization -- the name of the organization that created the software
            using the Python Cloud library
        application -- the name of the application software using the Python
            Cloud library
        version -- the version string for the application software
        """
        namepattern = re.compile(r'[^a-z0-9]')
        versionpattern = re.compile(r'[^a-z0-9\.\-]')
        org = namepattern.sub('', organization.lower())
        app = namepattern.sub('', application.lower())
        ver = versionpattern.sub('', version.lower())
        return "%s.%s.%s" % (org, app, ver)

    @staticmethod
    def clean_cloud_host_url(url):
        """
        Simple function that helps ensure a working API URL. Assumes that the
        URL of the host service ends with /api and processes the given URL to
        meet this assumption.

        Arguments:
        url -- the URL for the Cloud service, typically as entered by a user
            in their configuration
        """
        parts = url.split('/')
        if not parts[len(parts) - 1] == 'api':
            parts.append('api')
        return '/'.join(parts)
