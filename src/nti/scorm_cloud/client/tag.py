#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from zope import interface

from nti.scorm_cloud.interfaces import ITagService

logger = __import__('logging').getLogger(__name__)


@interface.implementer(ITagService)
class TagService(object):

    def __init__(self, service):
        self.service = service

    def get_scorm_tags(self, scorm_id):
        """
        Get tags for the given scorm_id

        :param scorm_id: the scorm_id to fetch tags for
        """
        request = self.service.request()
        request.parameters['courseid'] = scorm_id
        result = request.call_service('rustici.tagging.getCourseTags')
        tags = []
        for tag_element in result.getElementsByTagName("tag"):
            tags.append(tag_element.childNodes[0].nodeValue)
        return tags

    def set_scorm_tags(self, scorm_id, tags):
        """
        Set tags for the given scorm_id

        :param scorm_id: the scorm_id to set tags on
        :param tags: An iterable of tags
        """
        request = self.service.request()
        request.parameters['courseid'] = scorm_id
        request.parameters['tags'] = tags
        result = request.call_service('rustici.tagging.setCourseTags')
        return result

    def add_scorm_tag(self, scorm_id, tag):
        """
        Add a tag for the given scorm_id

        :param scorm_id: the scorm_id to add the tag
        :param tag: The new tag
        """
        request = self.service.request()
        request.parameters['courseid'] = scorm_id
        request.parameters['tag'] = tag
        return request.call_service('rustici.tagging.addCourseTag')

    def remove_scorm_tag(self, scorm_id, tag):
        """
        Remove a tag for the given scorm_id

        :param scorm_id: the scorm_id to remove the tag
        :param tag: The tag to remove
        """
        request = self.service.request()
        request.parameters['courseid'] = scorm_id
        request.parameters['tag'] = tag
        return request.call_service('rustici.tagging.removeCourseTag')
