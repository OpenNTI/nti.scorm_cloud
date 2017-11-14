#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from xml.dom.minidom import Document


def getData(nodes=(), types=()):
    result = []
    for node in nodes or ():
        if node.nodeType in types:
            result.append(node.data)
    return ''.join(result)


def getText(nodes=()):
    return getData(nodes, (Document.TEXT_NODE,))


def getCDATA(nodes=()):
    return getData(nodes, (Document.CDATA_SECTION_NODE,))


def getTextOrCDATA(nodes=()):
    return getData(nodes, (Document.TEXT_NODE, Document.CDATA_SECTION_NODE))


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


def getChildTextOrCDATA(node, name):
    nodes = node.getElementsByTagName(name)
    if nodes:
        return getTextOrCDATA(nodes[0].childNodes)
    return None


def getChildren(node, parent, child):
    nodes = node.getElementsByTagName(parent)
    if nodes:
        return nodes[0].getElementsByTagName(child)
    return None


def getFirstChild(node, name):
    nodes = node.getElementsByTagName(name)
    if nodes:
        return nodes[0]
    return None


def getAttributeValue(node, name):
    attr = node.attributes.get(name)
    return attr.value if attr is not None else None
