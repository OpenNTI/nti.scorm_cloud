#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from zope import interface

from nti.scorm_cloud.interfaces import IDebugService

logger = __import__('logging').getLogger(__name__)


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
