#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from six.moves.urllib_parse import quote

from zope import interface

from nti.scorm_cloud.interfaces import ICourseService
from nti.scorm_cloud.interfaces import IUploadService
from nti.scorm_cloud.interfaces import IWidgetSettings

logger = __import__('logging').getLogger(__name__)


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
