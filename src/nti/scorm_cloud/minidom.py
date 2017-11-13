#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import


def getText(nodes=()):
    result = []
    for node in nodes or ():
        if node.nodeType == node.TEXT_NODE:
            result.append(node.data)
    return ''.join(result)


def getCDATA(nodes=()):
    result = []
    for node in nodes or ():
        if node.nodeType == node.CDATA_SECTION_NODE:
            result.append(node.data)
    return ''.join(result) or None


def getChildText(node, name):
    nodes = node.getElementsByTagName(name)
    if nodes:
        return getText(nodes[0].childNodes)
    return None


def getChildCDATA(node, name):
    nodes = node.getElementsByTagName(name)
    if nodes:
        return getCDATA(nodes[0].childNodes)
    return None


def getAttributeValue(node, name):
    attr = node.attributes.get(name)
    return attr.value if attr is not None else None
