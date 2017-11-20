#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import six
from io import BytesIO

from zope import interface

from nti.scorm_cloud.interfaces import IUnmarshalled

from nti.scorm_cloud.minidom import getAttributeValue

logger = __import__('logging').getLogger(__name__)


def nodecapture(f):
    def wrapper(*args):
        node = args[-1]
        result = f(*args)
        result._v_node = node
        return result
    return wrapper


@interface.implementer(IUnmarshalled)
class NodeMixin(object):
    """
    Base class for objects derived from an xml source
    """

    @property
    def _node(self):
        return getattr(self, '_v_node', None)


class RegistrationMixin(NodeMixin):

    def __init__(self, format_, regid=None, instanceid=None):
        self.regid = regid
        self.format = format_
        self.instanceid = instanceid

    @classmethod
    @nodecapture
    def fromMinidom(cls, node):
        return cls(getAttributeValue(node, 'format'),
                   getAttributeValue(node, 'regid'),
                   getAttributeValue(node, 'instanceid'))


def _type_name(self):
    t = type(self)
    type_name = t.__module__ + '.' + t.__name__
    return type_name


def _default_repr(self):
    # When we're executing, even if we're wrapped in a proxy when called,
    # we get an unwrapped self.
    return "<%s at %x %s>" % (_type_name(self), id(self), self.__dict__)


def make_repr(default=_default_repr):
    def __repr__(self):
        return default(self)
    return __repr__


def WithRepr(default=object()):
    """
    A class decorator factory to give a ``__repr__`` to
    the object. Useful for persistent objects.

    :keyword default: A callable to be used for the default value.
    """

    # If we get one argument that is a type, we were
    # called bare (@WithRepr), so decorate the type
    if isinstance(default, type):
        default.__repr__ = make_repr()
        return default

    # If we got None or anything else, we were called as a factory,
    # so return a decorator
    def d(cls):
        cls.__repr__ = make_repr(default)
        return cls
    return d


def get_source(context):
    if hasattr(context, 'read'):
        return context
    elif isinstance(context, bytes):
        return BytesIO(context)
    elif isinstance(context, six.string_types):
        with open(context, "r") as fp:
            return BytesIO(fp.read())
    raise ValueError("Invalid context source")
