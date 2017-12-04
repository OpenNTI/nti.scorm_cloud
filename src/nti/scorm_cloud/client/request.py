#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
.. $Id$
"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import re
import datetime
from hashlib import md5
from xml.dom import minidom

from six import text_type
from six.moves.urllib_parse import quote_plus

from requests import Session

from nti.scorm_cloud.compat import bytes_
from nti.scorm_cloud.compat import native_

from nti.scorm_cloud.minidom import getAttributeValue

logger = __import__('logging').getLogger(__name__)


def make_utf8(dictionary):
    """
    Encodes all Unicode strings in the dictionary to UTF-8. Converts
    all other objects to regular strings.

    Returns a copy of the dictionary, doesn't touch the original.
    """
    result = {}
    for key, value in dictionary.items():
        if isinstance(value, text_type):
            value = native_(value, 'utf-8')
        else:
            value = str(value)
        result[key] = value
    return result


class ScormCloudError(Exception):

    def __init__(self, msg, code=None, json=None):
        Exception.__init__(self, msg)
        self.code = code
        self.json = json


class ServiceRequest(object):
    """
    Helper object that handles the details of web service URLs and parameter
    encoding and signing. Set the web service method parameters on the
    parameters attribute of the ServiceRequest object and then call
    call_service with the method name to make a service request.
    """

    def __init__(self, service):
        self.file_ = None
        self.service = service
        self.parameters = dict()

    def call_service(self, method, serviceurl=None):
        """
        Calls the specified web service method using any parameters set on the
        ServiceRequest.

        Arguments:
        method -- the full name of the web service method to call.
            For example: rustici.registration.createRegistration
        serviceurl -- (optional) used to override the service host URL for a
            single call
        """
        url = self.construct_url(method, serviceurl)
        rawresponse = self.send_post(url, self.parameters)
        response = self.get_xml(rawresponse)
        return response

    def construct_url(self, method, serviceurl=None):
        """
        Gets the full URL for a Cloud web service call, including parameters.

        :param method: the full name of the web service method to call.
            For example: rustici.registration.createRegistration
        :param serviceurl: (optional) used to override the service host URL for a
            single call
        """
        params = {'method': method}

        # 'appid': self.service.config.appid,
        # 'origin': self.service.config.origin,
        # 'ts': datetime.datetime.utcnow().strftime('yyyyMMddHHmmss'),
        # 'applib': 'python'}
        for k, v in self.parameters.items():
            params[k] = v
        url = serviceurl or self.service.config.serviceurl
        url = (
            ScormCloudUtilities.clean_cloud_host_url(url)
            + '?'
            + self.encode_and_sign(params)
        )
        return url

    def get_xml(self, raw):
        """
        Parses the raw response string as XML and asserts that there was no
        error in the result.

        :param raw the raw response string from an API method call
        """
        xmldoc = minidom.parseString(raw)
        rsp = xmldoc.documentElement
        if rsp.attributes['stat'].value != 'ok':
            err = rsp.firstChild
            msg = getAttributeValue(err, 'msg')
            code = getAttributeValue(err, 'code')
            raise ScormCloudError('SCORM Cloud Error: %s - %s' % (code, msg),
                                  msg, code)
        return xmldoc

    def session(self):
        result = Session()
        return result

    def send_post(self, url, postparams=None):
        session = self.session()
        if not postparams:
            reply = session.get(url).text
        elif self.file_ is not None:
            reply = session.post(url, postparams,
                                 files={u'file': self.file_}).text
        else:
            reply = session.post(url, postparams).text
        return reply

    def encode_and_sign(self, dictionary):
        """
        URL encodes the data in the dictionary, and signs it using the
        given secret, if a secret was given.

        :param dictionary: the dictionary containing the key/value parameter pairs
        """
        dictionary['appid'] = self.service.config.appid
        dictionary['origin'] = self.service.config.origin
        dictionary['ts'] = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
        dictionary['applib'] = "python"
        dictionary = make_utf8(dictionary)
        values = list()
        signing = list()
        secret = self.service.config.secret
        for key in sorted(dictionary.keys(), key=str.lower):
            signing.append(key + dictionary[key])
            values.append(key + '=' + quote_plus(dictionary[key]))
        signing = bytes_(''.join(signing))
        values.append('sig=' + md5(secret + signing).hexdigest())
        return '&'.join(values)


class ScormCloudUtilities(object):
    """
    Provides utility functions for working with the SCORM Cloud.
    """

    @staticmethod
    def get_canonical_origin_string(organization, application, version):
        """
        Helper function to build a proper origin string to provide to the
        SCORM Cloud configuration. Takes the organization name, application
        name, and application version.

        :param organization: the name of the organization that created the software
            using the Python Cloud library
        :param application: the name of the application software using the Python
            Cloud library
        :param version: the version string for the application software
        :type organization: str
        :type application: str
        :type version: str
        """
        namepattern = re.compile(r'[^a-z0-9]')
        versionpattern = re.compile(r'[^a-z0-9\.\-]')
        org = namepattern.sub('', organization.lower())
        app = namepattern.sub('', application.lower())
        ver = versionpattern.sub('', version.lower())
        return "%s.%s.%s" % (org, app, ver)

    @staticmethod
    def clean_cloud_host_url(url):
        """
        Simple function that helps ensure a working API URL. Assumes that the
        URL of the host service ends with /api and processes the given URL to
        meet this assumption.

        :param url: the URL for the Cloud service, typically as entered by a user
            in their configuration
        :type url: str
        """
        parts = url.split('/')
        if not parts[len(parts) - 1] == 'api':
            parts.append('api')
        return '/'.join(parts)
