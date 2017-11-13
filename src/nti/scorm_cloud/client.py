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
from six.moves.urllib_parse import quote
from six.moves.urllib_parse import quote_plus

try:
    from urllib2 import urlopen
except ImportError:  # pragma: no cover
    from urllib.request import urlopen

from zope import interface

from nti.scorm_cloud.compat import bytes_
from nti.scorm_cloud.compat import native_

from nti.scorm_cloud.interfaces import ITagSettings
from nti.scorm_cloud.interfaces import IDebugService
from nti.scorm_cloud.interfaces import ICourseService
from nti.scorm_cloud.interfaces import IUploadService
from nti.scorm_cloud.interfaces import IWidgetSettings
from nti.scorm_cloud.interfaces import IReportingService
from nti.scorm_cloud.interfaces import IDateRangeSettings
from nti.scorm_cloud.interfaces import IInvitationService
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
        self.origin = origin
        self.secret = bytes_(secret)
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
    authPing = authping
        
    def gettime(self):
        try:
            xmldoc = self.service.make_call('rustici.debug.getTime')
            return xmldoc.documentElement.firstChild.firstChild.nodeValue
        except Exception:
            return None
    getTime = gettime


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
        return None

    def get_upload_url(self, callbackurl):
        token = self.get_upload_token()
        if token:
            request = self.service.request()
            request.parameters['tokenid'] = token.tokenid
            request.parameters['redirecturl'] = callbackurl
            return request.construct_url('rustici.upload.uploadFile')
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
        result = ImportResult.list_from_result(result)
        return result

    def delete_course(self, courseid):
        request = self.service.request()
        request.parameters['courseid'] = courseid
        return request.call_service('rustici.course.deleteCourse')

    def get_assets(self, courseid, path=None):
        request = self.service.request()
        request.parameters['courseid'] = courseid
        if path:
            request.parameters['path'] = path
        return request.call_service('rustici.course.getAssets')

    def get_course_list(self, courseIdFilterRegex=None):
        request = self.service.request()
        if courseIdFilterRegex:
            request.parameters['filter'] = courseIdFilterRegex
        result = request.call_service('rustici.course.getCourseList')
        courses = CourseData.list_from_result(result)
        return courses

    def get_preview_url(self, courseid, redirecturl, stylesheeturl=None):
        request = self.service.request()
        request.parameters['courseid'] = courseid
        request.parameters['redirecturl'] = redirecturl
        if stylesheeturl:
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
        if stylesheetUrl:
            request.parameters['stylesheet'] = stylesheetUrl
        if notificationFrameUrl:
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
        for an in attrNodes or ():
            atts[an.attributes['name'].value] = an.attributes['value'].value
        return atts

    def update_attributes(self, courseid, attributePairs):
        request = self.service.request()
        request.parameters['courseid'] = courseid
        for key, value in attributePairs.items():
            request.parameters[key] = value
        xmldoc = request.call_service('rustici.course.updateAttributes')
        atts = {}
        attrNodes = xmldoc.getElementsByTagName('attribute')
        for an in attrNodes or ():
            atts[an.attributes['name'].value] = an.attributes['value'].value
        return atts


@interface.implementer(IRegistrationService)
class RegistrationService(object):

    def __init__(self, service):
        self.service = service

    def create_registration(self, regid, courseid, userid, fname, lname,
                            email=None, learnerTags=None, courseTags=None,
                            registrationTags=None):
        if not regid:
            regid = str(uuid.uuid1())
        request = self.service.request()
        request.parameters['appid'] = self.service.config.appid
        request.parameters['courseid'] = courseid
        request.parameters['regid'] = regid
        request.parameters['fname'] = fname
        request.parameters['lname'] = lname
        request.parameters['learnerid'] = userid
        if email:
            request.parameters['email'] = email
        if learnerTags:
            request.parameters['learnerTags'] = learnerTags
        if courseTags:
            request.parameters['courseTags'] = courseTags
        if registrationTags is not None:
            request.parameters['registrationTags'] = registrationTags
        xmldoc = request.call_service('rustici.registration.createRegistration')
        successNodes = xmldoc.getElementsByTagName('success')
        if successNodes is None or successNodes.length == 0:
            raise ScormCloudError("Create Registration failed.  " +
                                  xmldoc.err.attributes['msg'])
        return regid

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

    def get_registration_list(self, regIdFilterRegex=None, courseIdFilterRegex=None):
        request = self.service.request()
        if regIdFilterRegex:
            request.parameters['filter'] = regIdFilterRegex
        if courseIdFilterRegex:
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


@interface.implementer(IInvitationService)
class InvitationService(object):

    def __init__(self, service):
        self.service = service

    def create_invitation(self, courseid, publicInvitation=True, send=True, addresses=None,
                          emailSubject=None, emailBody=None, creatingUserEmail=None,
                          registrationCap=None, postbackUrl=None, authType=None, urlName=None,
                          urlPass=None, resultsFormat=None, async_=False):
        request = self.service.request()

        request.parameters['courseid'] = courseid
        request.parameters['send'] = str(send).lower()
        request.parameters['public'] = str(publicInvitation).lower()

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
        if postbackUrl:
            request.parameters['postbackUrl'] = postbackUrl
        if authType:
            request.parameters['authType'] = authType
        if urlName:
            request.parameters['urlName'] = urlName
        if urlPass:
            request.parameters['urlPass'] = urlPass
        if resultsFormat:
            request.parameters['resultsFormat'] = resultsFormat

        if async_:
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


@interface.implementer(IReportingService)
class ReportingService(object):

    def __init__(self, service):
        self.service = service

    def get_reportage_date(self):
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
        request = self.service.request()
        request.parameters['navpermission'] = navperm
        request.parameters['admin'] = 'true' if allowadmin else 'false'
        xmldoc = request.call_service('rustici.reporting.getReportageAuth')
        token = xmldoc.getElementsByTagName('auth')
        if token.length > 0:
            return token[0].childNodes[0].nodeValue
        return None

    def _get_reportage_service_url(self):
        return self.service.config.serviceurl.replace('EngineWebServices', '')

    def _get_base_reportage_url(self):
        return (  self._get_reportage_service_url() 
                + 'Reportage/reportage.php'
                + '?appId=' + self.service.config.appid)

    def get_report_url(self, auth, reportUrl):
        request = self.service.request()
        request.parameters['auth'] = auth
        request.parameters['reporturl'] = reportUrl
        url = request.construct_url('rustici.reporting.launchReport')
        return url

    def get_reportage_url(self, auth):
        reporturl = self._get_base_reportage_url()
        return self.get_report_url(auth, reporturl)

    def get_course_reportage_url(self, auth, courseid):
        reporturl = self._get_base_reportage_url() + '&courseid=' + courseid
        return self.get_report_url(auth, reporturl)

    def get_widget_url(self, auth, widgettype, widgetSettings):
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


@interface.implementer(IWidgetSettings)
class WidgetSettings(object):

    def __init__(self, dateRangeSettings=None, tagSettings=None):
        self.tagSettings = tagSettings
        self.dateRangeSettings = dateRangeSettings

        self.courseId = None
        self.learnerId = None

        self.showTitle = True
        self.vertical = False
        self.public = True
        self.standalone = True
        self.iframe = False
        self.expand = True
        self.scriptBased = True

        self.divname = u''
        self.embedded = True
        self.viewall = True
        self.export = True

    def get_url_encoding(self):
        widgetUrlStr = ''
        if self.courseId:
            widgetUrlStr += '&courseId=' + quote(self.courseId)
        if self.learnerId:
            widgetUrlStr += '&learnerId=' + quote(self.learnerId)

        widgetUrlStr += '&showTitle=' + str(self.showTitle).lower()
        widgetUrlStr += '&standalone=' + str(self.standalone).lower()
        if self.iframe:
            widgetUrlStr += '&iframe=true'
        widgetUrlStr += '&expand=' + str(self.expand).lower()
        widgetUrlStr += '&scriptBased=' + str(self.scriptBased).lower()
        widgetUrlStr += '&divname=' + quote(self.divname)
        widgetUrlStr += '&vertical=' + str(self.vertical).lower()
        widgetUrlStr += '&embedded=' + str(self.embedded).lower()

        if self.dateRangeSettings is not None:
            widgetUrlStr += self.dateRangeSettings.get_url_encoding()

        if self.tagSettings is not None:
            widgetUrlStr += self.tagSettings.get_url_encoding()

        return widgetUrlStr


@interface.implementer(IDateRangeSettings)
class DateRangeSettings(object):

    def __init__(self, dateRangeType, dateRangeStart, dateRangeEnd, dateCriteria):
        self.dateRangeEnd = dateRangeEnd
        self.dateCriteria = dateCriteria
        self.dateRangeType = dateRangeType
        self.dateRangeStart = dateRangeStart

    def get_url_encoding(self):
        result = ''
        if self.dateRangeType == 'selection':
            result += '&dateRangeType=c'
            result += '&dateRangeStart=' + quote(self.dateRangeStart)
            result += '&dateRangeEnd=' + quote(self.dateRangeEnd)
        else:
            result += '&dateRangeType=' + quote(self.dateRangeType)
        result += '&dateCriteria=' + quote(self.dateCriteria)
        return result


@interface.implementer(ITagSettings)
class TagSettings(object):

    def __init__(self):
        self.tags = {'course': set(), 'learner': set(), 'registration': set()}

    def add(self, tagType, tagValue):
        self.tags[tagType].add(tagValue)
        return self

    def get_tag_str(self, tagType):
        return ','.join(sorted(self.tags[tagType])) + "|_all"

    def get_view_tag_str(self, tagType):
        return ','.join(sorted(self.tags[tagType]))

    def get_url_encoding(self):
        result = []
        for k in self.tags.keys():
            if self.tags[k]:
                result.extend(('&', k))
                result.extend(('Tags=', quote(self.get_tag_str(k))))
                result.extend(('&view', k.capitalize()))
                result.extend(('TagGroups=', quote(self.get_view_tag_str(k))))
        return ''.join(result)


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

    def __init__(self, courseDataElement=None):
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
        self.file_ = None
        self.service = service
        self.parameters = dict()

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
        values = list()
        signing = list()
        secret = self.service.config.secret
        for key in sorted(dictionary.keys(), key=str.lower):
            signing.append(key + dictionary[key])
            values.append(key + '=' + quote_plus(dictionary[key]))
        signing = bytes_(''.join(signing))
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

        :param organization: the name of the organization that created the software
            using the Python Cloud library
        :param application: the name of the application software using the Python
            Cloud library
        :param version: the version string for the application software
        :type organization: str
        :type application: str
        :type version: str
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

        :param url: the URL for the Cloud service, typically as entered by a user
            in their configuration
        :type url: str
        """
        parts = url.split('/')
        if not parts[len(parts) - 1] == 'api':
            parts.append('api')
        return '/'.join(parts)
