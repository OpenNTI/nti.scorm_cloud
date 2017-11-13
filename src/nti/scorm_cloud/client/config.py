#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from nti.scorm_cloud.compat import bytes_

logger = __import__('logging').getLogger(__name__)


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
