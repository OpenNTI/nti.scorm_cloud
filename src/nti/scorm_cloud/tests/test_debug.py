#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

# disable: accessing protected members, too many methods
# pylint: disable=W0212,R0904

from hamcrest import is_
from hamcrest import none
from hamcrest import assert_that

import unittest

import fudge

from nti.scorm_cloud.client.scorm import ScormCloudService

from nti.scorm_cloud.tests import SharedConfiguringTestLayer

XML_HEADER = '<?xml version="1.0" encoding="utf-8" ?>'


class TestDebugService(unittest.TestCase):

    layer = SharedConfiguringTestLayer

    @fudge.patch('nti.scorm_cloud.client.request.ServiceRequest.session')
    def test_service(self, mock_ss):
        service = ScormCloudService.withargs("appid", "secret",
                                             "http://cloud.scorm.com/api")
        debug = service.get_debug_service()

        # ping / authping
        for method in ('ping', 'authping'):
            reply = XML_HEADER + '<rsp stat="ok"><pong /></rsp>'
            data = fudge.Fake().has_attr(text=reply)
            session = fudge.Fake().expects('get').returns(data)
            mock_ss.is_callable().returns(session)

            method = getattr(debug, method)
            assert_that(method(), is_(True))

            session = fudge.Fake().expects('get').raises(ValueError())
            mock_ss.is_callable().returns(session)
            assert_that(method(), is_(False))

        # gettime
        reply = XML_HEADER + '<rsp stat="ok"><currenttime tz="UTC">20171130152345</currenttime></rsp>'
        data = fudge.Fake().has_attr(text=reply)
        session = fudge.Fake().expects('get').returns(data)
        mock_ss.is_callable().returns(session)
        assert_that(debug.gettime(), is_('20171130152345'))

        session = fudge.Fake().expects('get').raises(ValueError())
        mock_ss.is_callable().returns(session)
        assert_that(debug.gettime(), is_(none()))