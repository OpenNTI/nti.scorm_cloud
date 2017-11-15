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


def getChildNodesByName(node, name):
    result = []
    for node in node.childNodes or ():
        if      node.nodeType == node.ELEMENT_NODE \
            and (name == "*" or node.tagName == name):
            result.append(node)
    return result


def getChildText(node, name):
    nodes = getChildNodesByName(node, name)
    return getText(nodes[0].childNodes) if nodes else None


def getChildCDATA(node, name):
    nodes = getChildNodesByName(node, name)
    return getCDATA(nodes[0].childNodes) if nodes else None


def getChildTextOrCDATA(node, name):
    nodes = getChildNodesByName(node, name)
    return getTextOrCDATA(nodes[0].childNodes) if nodes else None


def getChildren(node, parent, child):
    nodes = getChildNodesByName(node, parent)
    return getChildNodesByName(nodes[0], child) if nodes else None


def getFirstChild(node, name):
    nodes = getChildNodesByName(node, name)
    return nodes[0] if nodes else None


def getAttributeValue(node, name):
    attr = node.attributes.get(name)
    return attr.value if attr is not None else None
