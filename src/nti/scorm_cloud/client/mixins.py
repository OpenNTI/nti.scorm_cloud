#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from nti.scorm_cloud.minidom import getAttributeValue

logger = __import__('logging').getLogger(__name__)


class NodeMixin(object):
    """
    Base class for objects derived from an xml source
    """


class RegistrationMixin(NodeMixin):

    def __init__(self, format_, regid=None, instanceid=None):
        self.regid = regid
        self.format = format_
        self.instanceid = instanceid

    @classmethod
    def fromMinidom(cls, node):
        return cls(getAttributeValue(node, 'format'),
                   getAttributeValue(node, 'regid'),
                   getAttributeValue(node, 'instanceid'))
