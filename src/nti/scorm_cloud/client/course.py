#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from rustici_software_cloud_v2.api.course_api import CourseApi as SCV2CourseApi

from rustici_software_cloud_v2.models.launch_auth_schema import LaunchAuthSchema

from rustici_software_cloud_v2.models.launch_link_request_schema import LaunchLinkRequestSchema

from rustici_software_cloud_v2.rest import ApiException

from zope import interface

from nti.common.string import is_true

from nti.scorm_cloud.client.request import ScormCloudError
from nti.scorm_cloud.client.request import ScormUpdateError

from nti.scorm_cloud.client.mixins import get_source
from nti.scorm_cloud.client.mixins import nodecapture

from nti.scorm_cloud.interfaces import ICourseService
from nti.scorm_cloud.interfaces import IUploadService

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

    def get_preview_url(self, courseid, redirecturl, stylesheeturl=None,
                        launchAuthType='vault', launchAuth=None):
        """
        Generate the launch url that can be used by the user to preview the provided
        registration.

        This has been migrated to the v2 api, notice some of the kwargs are translated
        based on the migration guide.

        https://cloud.scorm.com/docs/v2/reference/migration_guide/
        """
        if launchAuth is None:
            launchAuth = LaunchAuthSchema(type=launchAuthType)
        v2_course_api = SCV2CourseApi(api_client=self.service.make_v2_api())
        launch_link_request = LaunchLinkRequestSchema(redirect_on_exit_url=redirecturl,
                                                      css_url=stylesheeturl,
                                                      launch_auth=launchAuth)
        try:
            result = v2_course_api.build_course_preview_launch_link(courseid, 
                                                                    launch_link_request)
        except ApiException as exc:
            logger.exception("Error while getting scorm preview url")
            raise ScormCloudError('Cannot get scorm preview url')
        logger.info('Scorm preview link: %s', result.launch_link)
        return result.launch_link

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
    learningStandard = None

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

            _ls = courseDataElement.getElementsByTagName('learningStandard')
            if _ls and _ls[0].firstChild:
                self.learningStandard = _ls[0].firstChild.nodeValue or None
                

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
            import_result_node = xmldoc.documentElement.getElementsByTagName('importresult')[0]
            import_result = ImportResult(import_result_node)
            # Successful, get title
            title = import_result.title
            if not import_result.wasSuccessful:
                # Another type of error
                status = 'error'
                error_message = import_result.message
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
