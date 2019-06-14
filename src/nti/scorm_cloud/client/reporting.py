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

from nti.scorm_cloud.interfaces import ITagSettings
from nti.scorm_cloud.interfaces import IWidgetSettings
from nti.scorm_cloud.interfaces import IReportingService
from nti.scorm_cloud.interfaces import IDateRangeSettings

logger = __import__('logging').getLogger(__name__)


@interface.implementer(IReportingService)
class ReportingService(object):

    def __init__(self, service):
        self.service = service

    def get_account_info(self):
        return self.service.make_call('rustici.reporting.getAccountInfo')

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
        return (self._get_reportage_service_url()
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
