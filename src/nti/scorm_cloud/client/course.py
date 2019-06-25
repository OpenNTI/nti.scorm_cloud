#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from zope import interface

from nti.common.string import is_true

from nti.scorm_cloud.client.request import ScormUpdateError

from nti.scorm_cloud.client.mixins import get_source
from nti.scorm_cloud.client.mixins import nodecapture

from nti.scorm_cloud.interfaces import ICourseService
from nti.scorm_cloud.interfaces import IUploadService

from nti.scorm_cloud.minidom import getChildTextOrCDATA

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

    def _validate_import(self, xmldoc):
        results = xmldoc.getElementsByTagName('importresult')
        if results:
            result = results[0]
            success = result.attributes['successful'].value
            if not is_true(success):
                msg = ''
                for child_node in result.childNodes or ():
                    if child_node.tagName == 'message':
                        msg = child_node.firstChild.wholeText
                raise ScormUpdateError(msg)

    def import_uploaded_course(self, courseid, path):
        request = self.service.request()
        request.parameters['courseid'] = courseid
        request.file_ = get_source(path)
        result = request.call_service('rustici.course.importCourse')
        self._validate_import(result)
        result = ImportResult.list_from_result(result)
        return result

    def _get_token(self, xmldoc):
        tokens = xmldoc.getElementsByTagName('token')
        token = tokens[0]
        id_node = token.getElementsByTagName('id')[0]
        return id_node.childNodes[0].nodeValue

    def import_uploaded_course_async(self, courseid, path):
        """
        Import the given scorm course package asynchronously, returning
        the token.
        """
        request = self.service.request()
        request.parameters['courseid'] = courseid
        request.file_ = get_source(path)
        result = request.call_service('rustici.course.importCourseAsync')
        return self._get_token(result)

    def get_async_import_result(self, token):
        """
        Return the async import result for the given token.
        """
        request = self.service.request()
        request.parameters['token'] = token
        xmldoc = request.call_service('rustici.course.getAsyncImportResult')
        return AsyncImportResult.fromMinidom(xmldoc)

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

    def get_course_detail(self, courseid):
        """
        Return the scorm detail for the given scorm course_id.
        """
        request = self.service.request()
        request.parameters['courseid'] = courseid
        result = request.call_service('rustici.course.getCourseDetail')
        course_result = result.documentElement.getElementsByTagName('course')[0]
        courses = CourseData(course_result)
        return courses

    def get_course_list(self, courseIdFilterRegex=None, tags=None):
        """
        Fetch the scorm content, filtering by the scorm courseId or
        by the given tags (must match all).
        """
        request = self.service.request()
        if courseIdFilterRegex:
            request.parameters['filter'] = courseIdFilterRegex
        if tags:
            request.parameters['tags'] = tags
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
        xml_response = request.call_service('rustici.course.getMetadata')
        return Metadata(xml_response)

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

    def update_assets(self, courseid, path):
        request = self.service.request()
        request.parameters['courseid'] = courseid
        request.file_ = get_source(path)
        result = request.call_service('rustici.course.updateAssets')
        self._validate_import(result)
        return result

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
    tags = []

    def __init__(self, courseDataElement=None):
        if courseDataElement is not None:
            tags = []
            for tag_element in courseDataElement.getElementsByTagName("tag"):
                tags.append(tag_element.childNodes[0].nodeValue)
            self.tags = tags
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


class Metadata(object):
    """
    An object containing the information returned by `get_metadata`.

    #TODO: Implement remaining properties as needed
    """

    title = u''

    def __init__(self, xmldoc):
        obj_element = xmldoc.documentElement.getElementsByTagName('object')[0]
        self.title = obj_element.getAttribute('title')



class AsyncImportResult(object):
    """
    An object containing the information returned by `getAsyncImportResult`.
    """

    title = None
    status = None
    error_message = None

    def __init__(self, title=None, status=None, error_message=None):
        self.title = title
        self.status = status
        self.error_message = error_message

    @classmethod
    @nodecapture
    def fromMinidom(cls, xmldoc):
        title = None
        error_message = None
        status_element = xmldoc.documentElement.getElementsByTagName('status')[0]
        status = status_element.childNodes[0].nodeValue
        if status == 'finished':
            # Successful, get title
            title_element = xmldoc.documentElement.getElementsByTagName('title')[0]
            title = title_element.childNodes[0].nodeValue
        elif status == 'error':
            # Error, get error message
            error_element = xmldoc.documentElement.getElementsByTagName('error')[0]
            error_message = error_element.childNodes[0].nodeValue
        return cls(title=title, status=status, error_message=error_message)

class UploadToken(object):
    server = ""
    tokenid = ""

    def __init__(self, server, tokenid):
        self.server = server
        self.tokenid = tokenid
