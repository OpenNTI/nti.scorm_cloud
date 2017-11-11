#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import six


def bytes_(s, encoding='utf-8', errors='strict'):
    """
    If ``s`` is an instance of ``text_type``, return
    ``s.encode(encoding, errors)``, otherwise return ``s``
    """
    if not isinstance(s, bytes) and s is not None:
        return s.encode(encoding, errors)
    return s


if six.PY3:  # pragma: no cover
    def native_(s, encoding='latin-1', errors='strict'):
        """ 
        If ``s`` is an instance of ``text_type``, return
        ``s``, otherwise return ``str(s, encoding, errors)``
        """
        if isinstance(s, six.text_type):
            return s
        return str(s, encoding, errors)
else:
    def native_(s, encoding='latin-1', errors='strict'):
        """ 
        If ``s`` is an instance of ``text_type``, return
        ``s.encode(encoding, errors)``, otherwise return ``str(s)``
        """
        if isinstance(s, six.text_type):
            return s.encode(encoding, errors)
        return str(s)
