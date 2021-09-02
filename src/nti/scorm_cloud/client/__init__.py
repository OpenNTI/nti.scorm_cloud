#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import datetime

from six.moves import urllib_parse

try:
    from urllib2 import urlopen
except ImportError:  # pragma: no cover
    from urllib.request import urlopen
    
from zope import interface

from nti.scorm_cloud.client.config import Configuration

from nti.scorm_cloud.client.course import CourseService
from nti.scorm_cloud.client.course import UploadService

from nti.scorm_cloud.client.debug import DebugService

from nti.scorm_cloud.client.invitation import InvitationService

from nti.scorm_cloud.client.registration import RegistrationService

from nti.scorm_cloud.client.reporting import ReportingService

from nti.scorm_cloud.client.request import make_utf8
from nti.scorm_cloud.client.request import ServiceRequest
from nti.scorm_cloud.client.request import ScormCloudError
from nti.scorm_cloud.client.request import ScormCloudUtilities

from nti.scorm_cloud.client.scorm import ScormCloudService

from nti.scorm_cloud.client.tag import TagService

from nti.scorm_cloud.interfaces import ITagSettings
from nti.scorm_cloud.interfaces import IDebugService
from nti.scorm_cloud.interfaces import IWidgetSettings
from nti.scorm_cloud.interfaces import IReportingService
from nti.scorm_cloud.interfaces import IDateRangeSettings
from nti.scorm_cloud.interfaces import IScormCloudService
from nti.scorm_cloud.interfaces import IRegistrationService


logger = __import__('logging').getLogger(__name__)


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
            result += '&dateRangeStart=' + urllib_parse.quote(self.dateRangeStart)
            result += '&dateRangeEnd=' + urllib_parse.quote(self.dateRangeEnd)
        else:
            result += '&dateRangeType=' + urllib_parse.quote(self.dateRangeType)
        result += '&dateCriteria=' + urllib_parse.quote(self.dateCriteria)
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
                result.extend(('Tags=', urllib_parse.quote(self.get_tag_str(k))))
                result.extend(('&view', k.capitalize()))
                result.extend(('TagGroups=',
                               urllib_parse.quote(self.get_view_tag_str(k))))
        return ''.join(result)


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
            widgetUrlStr += '&courseId=' + urllib_parse.quote(self.courseId)
        if self.learnerId:
            widgetUrlStr += '&learnerId=' + urllib_parse.quote(self.learnerId)

        widgetUrlStr += '&showTitle=' + str(self.showTitle).lower()
        widgetUrlStr += '&standalone=' + str(self.standalone).lower()
        if self.iframe:
            widgetUrlStr += '&iframe=true'
        widgetUrlStr += '&expand=' + str(self.expand).lower()
        widgetUrlStr += '&scriptBased=' + str(self.scriptBased).lower()
        widgetUrlStr += '&divname=' + urllib_parse.quote(self.divname)
        widgetUrlStr += '&vertical=' + str(self.vertical).lower()
        widgetUrlStr += '&embedded=' + str(self.embedded).lower()

        if self.dateRangeSettings is not None:
            widgetUrlStr += self.dateRangeSettings.get_url_encoding()

        if self.tagSettings is not None:
            widgetUrlStr += self.tagSettings.get_url_encoding()

        return widgetUrlStr

