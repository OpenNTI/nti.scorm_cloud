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

from nti.scorm_cloud.interfaces import IAccountInfo
from nti.scorm_cloud.interfaces import IAccountUsageInfo
from nti.scorm_cloud.interfaces import IReportingService
from nti.scorm_cloud.interfaces import IUnmarshalled

from nti.scorm_cloud.minidom import getChildDatetime
from nti.scorm_cloud.minidom import getChildText
from nti.scorm_cloud.minidom import getFirstChild

logger = __import__('logging').getLogger(__name__)

@interface.implementer(IAccountUsageInfo, IUnmarshalled)
class AccountUsageInfo(object):

    @classmethod
    def createFromMinidom(cls, node):
        info = cls()
        info.fromMinidom(node)
        return info

    def fromMinidom(self, node):
        self._node = node
        self.reg_count = IAccountUsageInfo['reg_count'].fromUnicode(
            getChildText(node, 'regcount'))
        self.total_registrations = IAccountUsageInfo['total_registrations'].fromUnicode(
            getChildText(node, 'totalregistrations'))
        self.total_courses = IAccountUsageInfo['total_courses'].fromUnicode(
            getChildText(node, 'totalcourses'))

        self.month_start = getChildDatetime(node, 'monthstart')

@interface.implementer(IAccountInfo, IUnmarshalled)
class AccountInfo(object):

    @classmethod
    def createFromMinidom(cls, node):
        info = cls()
        info.fromMinidom(node)
        return info

    def fromMinidom(self, node):
        self._node = node

        usage_dom = getFirstChild(node, 'usage')
        self.usage = AccountUsageInfo.createFromMinidom(usage_dom) if usage_dom else None

        self.email = getChildText(node, 'email')
        self.firstname = getChildText(node, 'firstname')
        self.lastname = getChildText(node, 'lastname')
        self.account_type = getChildText(node, 'accounttype')
        self.reg_limit = IAccountInfo['reg_limit'].fromUnicode(
            getChildText(node, 'reglimit'))
        self.strict_limit = IAccountInfo['strict_limit'].fromUnicode(
            getChildText(node, 'strictlimit'))

        self.create_date = getChildDatetime(node, 'createdate')
        
@interface.implementer(IReportingService)
class ReportingService(object):

    def __init__(self, service):
        self.service = service

    def get_account_info(self):
        resp = self.service.make_call('rustici.reporting.getAccountInfo')
        resp = resp.getElementsByTagName('account')
        return AccountInfo.createFromMinidom(resp[0]) if resp else None

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


